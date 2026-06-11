#!/usr/bin/env python3
"""
watchdog.py — Monitora inbox/, trigghera ingest.py per file nuovi/modificati.

Eseguito da Task Scheduler (nightly o orario). Sicuro contro:
- Working directory variabile (sys.path fix per import ingest)
- Crash di Ollama (lo state si aggiorna solo dopo successo)
- Modifiche cosmetiche al frontmatter (hash calcolato solo sul body)
- File ostinatamente difettosi (quarantine dopo N fallimenti)
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# BUG FIX: garantisce che `import ingest` funzioni anche se Task Scheduler
# parte da una working directory diversa da quella dello script.
sys.path.insert(0, str(Path(__file__).parent))

from jsb_core import (  # noqa: E402
    body_hash,
    load_config,
    load_state,
    log_msg,
    mark_failure,
    mark_success,
    parse_frontmatter,
    quarantine_file,
    save_state,
    split_frontmatter,
)


SUBFOLDERS = ["articles", "notes", "documents", "conversations"]


def try_index_in_lightrag(inbox_rel_path: str, cfg: dict) -> None:
    """
    Dopo che Ollama ha elaborato un file inbox/, cerca il corrispondente
    file wiki/ e lo indicizza in LightRAG.
    Fallisce silenziosamente: se LightRAG è down il watchdog continua.
    """
    if not cfg.get("lightrag", {}).get("url"):
        return  # LightRAG non configurato — skip silenzioso

    try:
        import ingest_to_lightrag as lr_bot
        import ingest as ingest_mod

        slug = ingest_mod.make_slug(Path(inbox_rel_path).stem)
        wiki = cfg["_wiki_dir"]

        for sub in lr_bot.WIKI_SUBFOLDERS:
            candidate = wiki / sub / f"{slug}.md"
            if not candidate.exists():
                continue

            lr_cfg = lr_bot.get_lightrag_cfg(cfg)
            if not lr_bot.check_health(lr_cfg):
                log_msg("WARN", "LightRAG non raggiungibile, skip indicizzazione.", cfg)
                return

            content = candidate.read_text(encoding="utf-8")
            fm_str, body = split_frontmatter(content)
            fm = parse_frontmatter(fm_str)
            vault_rel = str(candidate.relative_to(cfg["_vault_dir"])).replace("\\", "/")
            lr_content = lr_bot.build_lightrag_content(candidate, fm, body)

            ok, err = lr_bot.insert_document(vault_rel, lr_content, fm, lr_cfg)
            if ok:
                lr_state = lr_bot.load_lr_state(cfg)
                lr_state[vault_rel] = {
                    "hash": lr_bot.body_hash_str(body),
                    "indexed_at": datetime.now().isoformat(timespec="seconds"),
                    "type": fm.get("type", "unknown"),
                }
                lr_bot.save_lr_state(lr_state, cfg)
                log_msg("INFO", f"🔍 LightRAG: {candidate.name}", cfg)
            else:
                log_msg("WARN", f"LightRAG {candidate.name}: {err}", cfg)
            return

    except Exception as e:
        log_msg("WARN", f"LightRAG hook errore (non bloccante): {e}", cfg)


def find_pending_files(cfg: dict, state: dict) -> list[tuple[Path, str, str]]:
    """
    Trova file da processare. Ritorna lista di (filepath, rel_path, current_hash).
    """
    inbox = cfg["_inbox_dir"]
    vault = cfg["_vault_dir"]
    quarantine_threshold = cfg.get("ingest", {}).get(
        "fail_quarantine_after_retries", 3
    )

    pending = []
    for sub in SUBFOLDERS:
        sub_path = inbox / sub
        if not sub_path.exists():
            continue

        for file in sub_path.glob("*.md"):
            try:
                current_hash = body_hash(file)
            except OSError as e:
                log_msg("WARN", f"Lettura fallita per {file.name}: {e}", cfg)
                continue

            rel_path = str(file.relative_to(vault))
            entry = state.get(rel_path)

            if entry is None:
                pending.append((file, rel_path, current_hash))
                continue

            if entry["hash"] != current_hash:
                pending.append((file, rel_path, current_hash))
                continue

            if entry["status"] == "failed":
                if entry["fail_count"] < quarantine_threshold:
                    pending.append((file, rel_path, current_hash))
                else:
                    log_msg(
                        "DEBUG",
                        f"Skip {rel_path} (oltre soglia retry)",
                        cfg,
                    )

    return pending


def main() -> int:
    cfg = load_config()
    log_msg("INFO", "=== watchdog avviato ===", cfg)

    role = cfg.get("role", "")
    if role == "editor-only":
        log_msg("INFO", "Role=editor-only: questo PC non elabora. Esco.", cfg)
        return 0

    state = load_state(cfg)
    pending = find_pending_files(cfg, state)

    if not pending:
        log_msg("DEBUG", "Nessun file in attesa di elaborazione.", cfg)
        return 0

    log_msg("INFO", f"Trovati {len(pending)} file da elaborare.", cfg)

    import ingest

    quarantine_threshold = cfg.get("ingest", {}).get(
        "fail_quarantine_after_retries", 3
    )

    for filepath, rel_path, file_hash in pending:
        log_msg("INFO", f"Elaborazione: {rel_path}", cfg)
        try:
            success, error = ingest.process_file(filepath, cfg)
        except Exception as e:
            success = False
            error = f"Eccezione non gestita: {e}"

        if success:
            mark_success(state, rel_path, file_hash)
            log_msg("INFO", f"✅ {rel_path}", cfg)
            # Pipeline: dopo Ollama, indicizza subito in LightRAG
            try_index_in_lightrag(rel_path, cfg)
        else:
            fail_count = mark_failure(state, rel_path, file_hash, error or "unknown")
            log_msg("WARN", f"❌ {rel_path} (fail #{fail_count}): {error}", cfg)

            if fail_count >= quarantine_threshold:
                quarantine_file(filepath, error or "unknown", cfg)
                state.pop(rel_path, None)

        save_state(state, cfg)

    log_msg("INFO", "=== watchdog completato ===", cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
