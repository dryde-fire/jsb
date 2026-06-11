#!/usr/bin/env python3
"""
jsb_core.py — Modulo condiviso per Second Brain.

Fornisce: caricamento configurazione, logging strutturato, gestione state file
con semantica corretta (state aggiornato SOLO dopo successo elaborazione),
hash che esclude il frontmatter, retry con backoff per chiamate Ollama.

Importato da: watchdog.py, ingest.py, distill.py
"""

from __future__ import annotations

import json
import hashlib
import sys
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

# -----------------------------------------------------------------------------
# Configurazione: caricata una volta, accessibile globalmente
# -----------------------------------------------------------------------------

_CONFIG_CACHE: Optional[dict[str, Any]] = None


def get_config_path() -> Path:
    """
    Restituisce il path del file di configurazione.

    Ordine di ricerca:
    1. Variabile ambiente JSB_CONFIG (utile per test e per Claude Code)
    2. %USERPROFILE%\\.jsb-config.json (Windows) o ~/.jsb-config.json (Unix)
    """
    import os

    env_path = os.environ.get("JSB_CONFIG")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    home = Path.home()
    return home / ".jsb-config.json"


def load_config() -> dict[str, Any]:
    """
    Carica la configurazione (con cache). Solleva eccezione se mancante.
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configurazione non trovata: {config_path}\n"
            f"Crea il file o imposta la variabile d'ambiente JSB_CONFIG."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Validazione minima dei campi obbligatori
    required = ["machine_id", "vault_path", "role"]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError(f"Config incompleta: mancano i campi {missing}")

    # Path objects
    cfg["_vault_dir"] = Path(cfg["vault_path"])
    if not cfg["_vault_dir"].exists():
        raise FileNotFoundError(f"Vault path non esiste: {cfg['_vault_dir']}")

    cfg["_inbox_dir"] = cfg["_vault_dir"] / "inbox"
    cfg["_wiki_dir"] = cfg["_vault_dir"] / "wiki"
    cfg["_archive_dir"] = cfg["_vault_dir"] / "archive"
    cfg["_system_dir"] = cfg["_vault_dir"] / "_system"
    cfg["_state_file"] = cfg["_system_dir"] / ".ingest-state.json"
    cfg["_log_file"] = cfg["_system_dir"] / "ingest-log.md"

    _CONFIG_CACHE = cfg
    return cfg


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------


def log_msg(level: str, msg: str, cfg: Optional[dict] = None) -> None:
    """
    Log con timestamp su stdout e su ingest-log.md.

    Levels: DEBUG, INFO, WARN, ERROR
    """
    if cfg is None:
        try:
            cfg = load_config()
        except Exception:
            # Se non c'è config, fallback su stdout
            print(f"[{datetime.now().isoformat(timespec='seconds')}] {level}: {msg}")
            return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    machine = cfg.get("machine_id", "unknown")
    line = f"[{timestamp}] [{machine}] {level}: {msg}"
    print(line)

    log_file = cfg["_log_file"]
    log_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[WARN] Impossibile scrivere log: {e}", file=sys.stderr)


# -----------------------------------------------------------------------------
# Frontmatter & hash
# -----------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n(.*)$", re.DOTALL)


def split_frontmatter(content: str) -> tuple[str, str]:
    """
    Separa frontmatter (YAML grezzo, stringa) e body.
    Restituisce (frontmatter_str, body). Frontmatter vuoto se assente.
    """
    match = _FRONTMATTER_RE.match(content)
    if match:
        return match.group(1), match.group(2)
    return "", content


def parse_frontmatter(fm_str: str) -> dict:
    """Parse YAML frontmatter. Richiede pyyaml."""
    if not fm_str.strip():
        return {}
    import yaml
    try:
        return yaml.safe_load(fm_str) or {}
    except yaml.YAMLError as e:
        log_msg("WARN", f"Frontmatter YAML invalido: {e}")
        return {}


def serialize_frontmatter(fm: dict) -> str:
    """Serializza dict come YAML frontmatter (senza i delimitatori ---)."""
    import yaml
    return yaml.dump(
        fm,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


def body_hash(filepath: Path) -> str:
    """
    SHA256 del SOLO body (esclude il frontmatter).

    BUG FIX rispetto allo script originale: modificare un tag nel frontmatter
    NON deve far rielaborare il contenuto. Solo cambi al body contano.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    _, body = split_frontmatter(content)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


# -----------------------------------------------------------------------------
# State management con semantica corretta
# -----------------------------------------------------------------------------


def load_state(cfg: dict) -> dict:
    """
    Carica lo state file.

    Schema:
    {
      "<rel_path>": {
        "hash": "<sha256>",
        "status": "done" | "failed",
        "last_processed": "<iso-timestamp>",
        "fail_count": 0,
        "last_error": null
      }
    }
    """
    state_file = cfg["_state_file"]
    if not state_file.exists():
        return {}
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        log_msg("WARN", f"State file corrotto, riparto da zero: {e}", cfg)
        return {}


def save_state(state: dict, cfg: dict) -> None:
    """Salva lo state in modo atomico (write-then-rename)."""
    state_file = cfg["_state_file"]
    state_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_file.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    tmp.replace(state_file)


def mark_success(state: dict, rel_path: str, file_hash: str) -> None:
    """Marca un file come elaborato con successo."""
    state[rel_path] = {
        "hash": file_hash,
        "status": "done",
        "last_processed": datetime.now().isoformat(timespec="seconds"),
        "fail_count": 0,
        "last_error": None,
    }


def mark_failure(state: dict, rel_path: str, file_hash: str, error: str) -> int:
    """
    Marca un fallimento e ritorna il fail_count attuale.

    BUG FIX rispetto allo script originale: l'hash viene salvato
    SOLO ora, dopo che sappiamo l'esito. Se il file viene modificato
    e riprovato, fail_count si resetta perché l'hash cambia.
    """
    prev = state.get(rel_path, {})
    prev_hash = prev.get("hash")
    fail_count = prev.get("fail_count", 0)
    if prev_hash == file_hash:
        fail_count += 1
    else:
        fail_count = 1  # nuovo contenuto, nuovo conteggio

    state[rel_path] = {
        "hash": file_hash,
        "status": "failed",
        "last_processed": datetime.now().isoformat(timespec="seconds"),
        "fail_count": fail_count,
        "last_error": error[:500],
    }
    return fail_count


# -----------------------------------------------------------------------------
# Quarantine: file falliti N volte vengono spostati in inbox/_failed/
# -----------------------------------------------------------------------------


def quarantine_file(filepath: Path, error: str, cfg: dict) -> None:
    """
    Sposta un file fallito ripetutamente in inbox/_failed/<sottocartella>/
    con un .error a fianco che spiega cosa è andato storto.
    """
    inbox = cfg["_inbox_dir"]
    rel_to_inbox = filepath.relative_to(inbox)
    failed_dir = inbox / "_failed" / rel_to_inbox.parent
    failed_dir.mkdir(parents=True, exist_ok=True)

    dest = failed_dir / filepath.name
    try:
        filepath.rename(dest)
    except OSError as e:
        log_msg("ERROR", f"Quarantine fallita per {filepath}: {e}", cfg)
        return

    err_file = dest.with_suffix(dest.suffix + ".error")
    err_file.write_text(
        f"Quarantined: {datetime.now().isoformat(timespec='seconds')}\n"
        f"Error: {error}\n",
        encoding="utf-8",
    )
    log_msg("WARN", f"File spostato in quarantena: {dest.name}", cfg)


# -----------------------------------------------------------------------------
# Ollama call con retry esponenziale
# -----------------------------------------------------------------------------


def call_ollama(
    prompt: str, model: str, cfg: dict, timeout: Optional[int] = None
) -> Optional[str]:
    """
    Chiama Ollama con retry esponenziale (1s, 4s, 16s).
    Ritorna la risposta o None se tutti i tentativi falliscono.
    """
    import requests

    ollama_cfg = cfg.get("ollama", {})
    url = (ollama_cfg.get("url") or "http://localhost:11434") + "/api/generate"
    timeout = timeout or ollama_cfg.get("timeout_seconds", 180)
    max_retries = ollama_cfg.get("max_retries", 3)

    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout,
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            last_error = f"HTTP {response.status_code}: {response.text[:200]}"
        except requests.exceptions.ConnectionError:
            last_error = f"Ollama non raggiungibile su {url}"
        except requests.exceptions.Timeout:
            last_error = f"Timeout dopo {timeout}s"
        except Exception as e:
            last_error = f"Errore inatteso: {e}"

        if attempt < max_retries - 1:
            wait = 1 << (2 * attempt)  # 1, 4, 16
            log_msg(
                "WARN",
                f"Ollama tentativo {attempt + 1}/{max_retries} fallito ({last_error}). Retry in {wait}s.",
                cfg,
            )
            time.sleep(wait)

    log_msg("ERROR", f"Ollama definitivamente fallito: {last_error}", cfg)
    return None


# -----------------------------------------------------------------------------
# Output: scrittura sicura con archive su sovrascrittura
# -----------------------------------------------------------------------------


def archive_existing(target: Path, cfg: dict) -> None:
    """
    Se target esiste già, lo sposta in archive/<original-folder>/<basename>-<timestamp>.md
    Implementa l'idempotenza: rielaborazioni non distruggono lavoro precedente.
    """
    if not target.exists():
        return
    archive_root = cfg["_archive_dir"]
    rel = target.relative_to(cfg["_wiki_dir"])
    dest_dir = archive_root / rel.parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = dest_dir / f"{target.stem}-{ts}{target.suffix}"
    target.rename(dest)
    log_msg("INFO", f"Archiviato precedente: {dest.relative_to(cfg['_vault_dir'])}", cfg)


def write_wiki_file(
    target: Path, frontmatter: dict, body: str, cfg: dict
) -> None:
    """Scrive il file in wiki/ archiviando l'eventuale precedente."""
    if cfg.get("ingest", {}).get("archive_on_overwrite", True):
        archive_existing(target, cfg)

    target.parent.mkdir(parents=True, exist_ok=True)
    fm_str = serialize_frontmatter(frontmatter)
    content = f"---\n{fm_str}---\n\n{body.strip()}\n"
    target.write_text(content, encoding="utf-8")


# -----------------------------------------------------------------------------
# Self-test rapido (eseguibile come script)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== JSB Core Self-Test ===")
    try:
        cfg = load_config()
        print(f"✅ Config caricata: machine_id={cfg['machine_id']}, role={cfg['role']}")
        print(f"✅ Vault: {cfg['_vault_dir']}")
        print(f"✅ Vault esiste: {cfg['_vault_dir'].exists()}")
    except Exception as e:
        print(f"❌ Errore: {e}")
        sys.exit(1)
