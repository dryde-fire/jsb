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
    quarantine_file,
    save_state,
)


SUBFOLDERS = ["articles", "notes", "documents", "conversations"]


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
