#!/usr/bin/env python3
"""
ingest_to_lightrag.py — Indicizza wiki/ nel knowledge graph di LightRAG.

Viene chiamato automaticamente da watchdog.py dopo ogni elaborazione Ollama
(pipeline: inbox/ → Ollama elabora → wiki/ → LightRAG indicizza).

Può anche girare standalone per re-indicizzare tutto il vault:
    python ingest_to_lightrag.py --full-reindex

Logica di idempotenza: ogni documento ha un ID univoco basato sul path
relativo nel vault. Se il documento esiste già e non è cambiato (stesso
body hash), viene saltato. Se è cambiato (versione aggiornata), viene
prima cancellato e poi re-inserito.

Requisiti:
    - LightRAG server in esecuzione su Office PC (docker compose up -d)
    - pip install requests pyyaml
    - JSB_CONFIG punta a ~/.jsb-config.json con sezione "lightrag"
"""

from __future__ import annotations

import sys
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from jsb_core import (
    load_config,
    log_msg,
    split_frontmatter,
    parse_frontmatter,
    serialize_frontmatter,
)

import requests


# ---------------------------------------------------------------------------
# Config LightRAG da .jsb-config.json
# ---------------------------------------------------------------------------

def get_lightrag_cfg(cfg: dict) -> dict:
    lr = cfg.get("lightrag", {})
    url = lr.get("url", "http://localhost:9621")
    key = lr.get("api_key", "")
    return {
        "base_url": url.rstrip("/"),
        "headers": {
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {key}"} if key else {}),
        },
        "timeout": lr.get("timeout", 60),
    }


# ---------------------------------------------------------------------------
# State file separato per LightRAG (non mescola con lo state di Ollama)
# ---------------------------------------------------------------------------

def get_lr_state_file(cfg: dict) -> Path:
    return cfg["_system_dir"] / ".lightrag-state.json"


def load_lr_state(cfg: dict) -> dict:
    sf = get_lr_state_file(cfg)
    if not sf.exists():
        return {}
    try:
        return json.loads(sf.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_lr_state(state: dict, cfg: dict) -> None:
    sf = get_lr_state_file(cfg)
    tmp = sf.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(sf)


# ---------------------------------------------------------------------------
# Health check LightRAG
# ---------------------------------------------------------------------------

def check_health(lr_cfg: dict) -> bool:
    """Ritorna True se LightRAG risponde. Fa 3 tentativi con backoff."""
    for attempt in range(3):
        try:
            r = requests.get(
                f"{lr_cfg['base_url']}/health",
                headers=lr_cfg["headers"],
                timeout=10,
            )
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        if attempt < 2:
            time.sleep(2 ** attempt)
    return False


# ---------------------------------------------------------------------------
# Operazioni sui documenti LightRAG
# ---------------------------------------------------------------------------

def doc_id_from_path(rel_path: str) -> str:
    """
    ID documento stabile: hash MD5 del path relativo nel vault.
    Stesso file → stesso ID sempre, su tutti i PC.
    """
    return hashlib.md5(rel_path.encode("utf-8")).hexdigest()


def insert_document(
    rel_path: str,
    content: str,
    metadata: dict,
    lr_cfg: dict,
) -> tuple[bool, Optional[str]]:
    """
    Inserisce un documento in LightRAG via POST /documents/text.
    Ritorna (success, error_message).
    """
    doc_id = doc_id_from_path(rel_path)
    payload = {
        "id": doc_id,
        "content": content,
        "metadata": {
            "source_path": rel_path,
            "type": metadata.get("type", "unknown"),
            "tags": metadata.get("tags", []),
            "status": metadata.get("status", "published"),
            "date_elaborated": metadata.get("date_elaborated", ""),
            "version": metadata.get("version", 1),
        },
    }
    try:
        r = requests.post(
            f"{lr_cfg['base_url']}/documents/text",
            headers=lr_cfg["headers"],
            json=payload,
            timeout=lr_cfg["timeout"],
        )
        if r.status_code in (200, 201):
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:300]}"
    except requests.exceptions.Timeout:
        return False, f"Timeout dopo {lr_cfg['timeout']}s"
    except requests.exceptions.RequestException as e:
        return False, f"Errore connessione: {e}"


def delete_document(rel_path: str, lr_cfg: dict) -> bool:
    """Cancella un documento da LightRAG per ri-indicizzarlo."""
    doc_id = doc_id_from_path(rel_path)
    try:
        r = requests.delete(
            f"{lr_cfg['base_url']}/documents/{doc_id}",
            headers=lr_cfg["headers"],
            timeout=30,
        )
        return r.status_code in (200, 204, 404)  # 404 = già assente, OK
    except requests.exceptions.RequestException:
        return False


# ---------------------------------------------------------------------------
# Costruzione contenuto da inviare a LightRAG
# ---------------------------------------------------------------------------

def build_lightrag_content(filepath: Path, fm: dict, body: str) -> str:
    """
    Costruisce il testo da inviare a LightRAG combinando frontmatter
    leggibile + body elaborato da Ollama.

    LightRAG indicizza questo testo per costruire il knowledge graph.
    Il frontmatter è incluso come contesto strutturato (tags, tipo, date)
    così le query su "note con tag stripe" funzionano correttamente.
    """
    tags_str = ", ".join(fm.get("tags", [])) if fm.get("tags") else ""
    header = (
        f"Type: {fm.get('type', 'unknown')}\n"
        f"Tags: {tags_str}\n"
        f"Date: {fm.get('date_elaborated', fm.get('created', ''))}\n"
        f"Source: {fm.get('source_file', filepath.name)}\n"
        f"Version: {fm.get('version', 1)}\n"
        f"---\n"
    )
    title = filepath.stem.replace("-", " ").title()
    return f"# {title}\n\n{header}\n{body.strip()}"


# ---------------------------------------------------------------------------
# Trova file wiki/ da indicizzare
# ---------------------------------------------------------------------------

WIKI_SUBFOLDERS = ["concepts", "learn", "projects", "decisions"]


def find_wiki_files(cfg: dict) -> list[Path]:
    """Tutti i file markdown in wiki/, esclude _system e archive."""
    wiki = cfg["_wiki_dir"]
    files = []
    for sub in WIKI_SUBFOLDERS:
        sub_path = wiki / sub
        if sub_path.exists():
            files.extend(sub_path.glob("*.md"))
    return files


def body_hash_str(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def ingest_all(cfg: dict, force_reindex: bool = False) -> tuple[int, int, int]:
    """
    Indicizza wiki/ in LightRAG.
    Ritorna (indexed, skipped, failed).
    """
    lr_cfg = get_lightrag_cfg(cfg)

    if not check_health(lr_cfg):
        log_msg(
            "ERROR",
            f"LightRAG non raggiungibile su {lr_cfg['base_url']}. "
            "Verifica che Docker sia in esecuzione (docker compose up -d).",
            cfg,
        )
        return 0, 0, 0

    state = load_lr_state(cfg)
    wiki_files = find_wiki_files(cfg)
    vault = cfg["_vault_dir"]

    indexed = skipped = failed = 0

    for filepath in wiki_files:
        try:
            content = filepath.read_text(encoding="utf-8")
        except OSError as e:
            log_msg("WARN", f"Impossibile leggere {filepath.name}: {e}", cfg)
            failed += 1
            continue

        fm_str, body = split_frontmatter(content)
        fm = parse_frontmatter(fm_str)
        rel_path = str(filepath.relative_to(vault)).replace("\\", "/")
        current_hash = body_hash_str(body)

        # Decide se indicizzare
        entry = state.get(rel_path, {})
        if not force_reindex and entry.get("hash") == current_hash:
            skipped += 1
            continue

        # Se esiste già una versione precedente, cancellala prima
        if entry.get("hash") and entry["hash"] != current_hash:
            log_msg("INFO", f"Re-indicizzazione (versione aggiornata): {rel_path}", cfg)
            delete_document(rel_path, lr_cfg)
        else:
            log_msg("INFO", f"Indicizzazione nuova: {rel_path}", cfg)

        lr_content = build_lightrag_content(filepath, fm, body)
        success, error = insert_document(rel_path, lr_content, fm, lr_cfg)

        if success:
            state[rel_path] = {
                "hash": current_hash,
                "indexed_at": datetime.now().isoformat(timespec="seconds"),
                "type": fm.get("type", "unknown"),
            }
            save_lr_state(state, cfg)
            indexed += 1
        else:
            log_msg("WARN", f"Fallita indicizzazione {rel_path}: {error}", cfg)
            failed += 1

    return indexed, skipped, failed


def main() -> int:
    force_reindex = "--full-reindex" in sys.argv

    cfg = load_config()
    log_msg("INFO", "=== LightRAG ingest avviato ===", cfg)

    if force_reindex:
        log_msg("INFO", "Modalità full-reindex: tutti i documenti verranno re-indicizzati.", cfg)

    # Verifica configurazione LightRAG nel config file
    if not cfg.get("lightrag", {}).get("url"):
        log_msg(
            "ERROR",
            "Sezione 'lightrag.url' mancante in .jsb-config.json. "
            "Aggiungi: \"lightrag\": {\"url\": \"http://localhost:9621\", \"api_key\": \"...\"}",
            cfg,
        )
        return 1

    indexed, skipped, failed = ingest_all(cfg, force_reindex=force_reindex)

    log_msg(
        "INFO",
        f"=== LightRAG ingest completato: {indexed} indicizzati, "
        f"{skipped} saltati, {failed} falliti ===",
        cfg,
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
