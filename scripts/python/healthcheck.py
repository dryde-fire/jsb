#!/usr/bin/env python3
"""
healthcheck.py — Diagnostica settimanale del Second Brain.

Risponde a tre domande pratiche:
1. Ollama ha girato di recente? Quanti file elaborati? Quanti falliti?
2. Ci sono file in inbox che restano fermi da troppo tempo?
3. Ci sono file in quarantena che richiedono attenzione manuale?

Output: report markdown stampato a video. Esci con code 1 se ci sono
warning, 2 se ci sono errori critici. Utile per cron + email.

Uso:
    python healthcheck.py            # report su stdout
    python healthcheck.py --json     # output machine-readable
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from jsb_core import load_config, load_state  # noqa: E402


def find_stale_inbox_files(cfg: dict, days: int = 7) -> list[Path]:
    """File in inbox modificati più di N giorni fa, non ancora elaborati."""
    state = load_state(cfg)
    inbox = cfg["_inbox_dir"]
    threshold = datetime.now() - timedelta(days=days)
    stale = []

    for sub in ["articles", "notes", "documents", "conversations"]:
        sub_dir = inbox / sub
        if not sub_dir.exists():
            continue
        for f in sub_dir.glob("*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime > threshold:
                continue
            rel = str(f.relative_to(cfg["_vault_dir"]))
            entry = state.get(rel)
            if entry is None or entry.get("status") != "done":
                stale.append(f)
    return stale


def find_quarantined(cfg: dict) -> list[Path]:
    failed_dir = cfg["_inbox_dir"] / "_failed"
    if not failed_dir.exists():
        return []
    return list(failed_dir.rglob("*.md"))


def get_last_run_age(cfg: dict) -> timedelta | None:
    """Età dell'ultima elaborazione riuscita, leggendo lo state."""
    state = load_state(cfg)
    if not state:
        return None
    last_runs = []
    for entry in state.values():
        if entry.get("status") == "done":
            try:
                ts = datetime.fromisoformat(entry["last_processed"])
                last_runs.append(ts)
            except (KeyError, ValueError):
                continue
    if not last_runs:
        return None
    return datetime.now() - max(last_runs)


def count_state(cfg: dict) -> tuple[int, int]:
    """Ritorna (n_done, n_failed) dallo state."""
    state = load_state(cfg)
    done = sum(1 for e in state.values() if e.get("status") == "done")
    failed = sum(1 for e in state.values() if e.get("status") == "failed")
    return done, failed


def build_report(cfg: dict) -> tuple[str, int]:
    """
    Costruisce report markdown e ritorna (testo, exit_code).
    Exit codes: 0=ok, 1=warning, 2=critical.
    """
    lines = []
    severity = 0  # 0=ok, 1=warn, 2=critical

    lines.append(f"# Second Brain Health Check")
    lines.append(f"Macchina: **{cfg['machine_id']}** · Ruolo: **{cfg['role']}**")
    lines.append(f"Generato: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    # 1. Ultima esecuzione
    age = get_last_run_age(cfg)
    if cfg["role"] == "editor-only":
        lines.append("## Esecuzione Ollama")
        lines.append("Questo PC non elabora (role=editor-only). Skip.")
    else:
        lines.append("## Esecuzione Ollama")
        if age is None:
            lines.append("⚠️ Nessuna elaborazione registrata. Watchdog mai eseguito o state vuoto.")
            severity = max(severity, 1)
        elif age > timedelta(days=2):
            lines.append(f"❌ Ultima elaborazione: **{age.days} giorni fa**. Task Scheduler probabilmente fermo.")
            severity = max(severity, 2)
        elif age > timedelta(hours=36):
            lines.append(f"⚠️ Ultima elaborazione: {age.days} giorni fa. Verificare che il nightly giri.")
            severity = max(severity, 1)
        else:
            hours = age.total_seconds() / 3600
            lines.append(f"✅ Ultima elaborazione: {hours:.1f}h fa.")

    # 2. Conteggio state
    done, failed = count_state(cfg)
    lines.append("")
    lines.append("## Conteggi")
    lines.append(f"- File elaborati con successo (storico): {done}")
    if failed > 0:
        lines.append(f"- ⚠️ File con stato 'failed' (in retry): **{failed}**")
        severity = max(severity, 1)
    else:
        lines.append(f"- File falliti: 0")

    # 3. Stale inbox
    stale = find_stale_inbox_files(cfg, days=7)
    lines.append("")
    lines.append("## Inbox bloccato")
    if stale:
        lines.append(f"⚠️ {len(stale)} file in inbox/ non elaborati da >7 giorni:")
        for f in stale[:10]:
            lines.append(f"  - {f.relative_to(cfg['_vault_dir'])}")
        if len(stale) > 10:
            lines.append(f"  - ...e altri {len(stale) - 10}")
        severity = max(severity, 1)
    else:
        lines.append("✅ Nessun file bloccato.")

    # 4. Quarantine
    quarantined = find_quarantined(cfg)
    lines.append("")
    lines.append("## Quarantine (richiede review manuale)")
    if quarantined:
        lines.append(f"❌ {len(quarantined)} file in inbox/_failed/:")
        for f in quarantined[:10]:
            err_file = f.with_suffix(f.suffix + ".error")
            err_msg = err_file.read_text(encoding="utf-8")[:200] if err_file.exists() else "(no error log)"
            lines.append(f"  - {f.relative_to(cfg['_vault_dir'])}")
            lines.append(f"    `{err_msg.splitlines()[0] if err_msg else '(empty)'}`")
        severity = max(severity, 2)
    else:
        lines.append("✅ Nessun file in quarantena.")

    # Verdetto
    lines.append("")
    lines.append("## Verdetto")
    if severity == 0:
        lines.append("✅ Tutto in ordine.")
    elif severity == 1:
        lines.append("⚠️ Attenzione richiesta. Vedi sopra.")
    else:
        lines.append("❌ Problemi critici. Intervenire.")

    return "\n".join(lines), severity


def main() -> int:
    cfg = load_config()
    report, severity = build_report(cfg)

    if "--json" in sys.argv:
        # Output JSON minimale per integrazioni
        result = {
            "machine_id": cfg["machine_id"],
            "severity": severity,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "report_markdown": report,
        }
        print(json.dumps(result, indent=2))
    else:
        print(report)

    return severity


if __name__ == "__main__":
    sys.exit(main())


def check_lightrag(cfg: dict) -> tuple[str, int]:
    """Verifica stato LightRAG e conta documenti indicizzati."""
    lr_cfg = cfg.get("lightrag", {})
    url = lr_cfg.get("url", "")
    if not url:
        return "Non configurato (lightrag.url mancante in .jsb-config.json)", 0

    key = lr_cfg.get("api_key", "")
    headers = {"Authorization": f"Bearer {key}"} if key else {}

    try:
        r = requests.get(f"{url.rstrip('/')}/health", headers=headers, timeout=5)
        if r.status_code == 200:
            # Conta documenti indicizzati dallo state file
            state_file = cfg["_system_dir"] / ".lightrag-state.json"
            count = 0
            if state_file.exists():
                import json as _json
                count = len(_json.loads(state_file.read_text(encoding="utf-8")))
            return f"Online · {count} documenti indicizzati", 0
        return f"Risposta HTTP {r.status_code}", 1
    except Exception as e:
        return f"Non raggiungibile: {e}", 2


# Monkey-patch build_report per aggiungere sezione LightRAG
_original_build_report = build_report


def build_report(cfg: dict) -> tuple[str, int]:
    import requests as _req
    lines_orig, severity = _original_build_report(cfg)
    lines = lines_orig.split("\n")

    # Inserisci sezione LightRAG prima del Verdetto
    verdict_idx = next(
        (i for i, l in enumerate(lines) if l.startswith("## Verdetto")), len(lines)
    )

    lr_status, lr_sev = check_lightrag(cfg)
    lr_icon = "✅" if lr_sev == 0 else ("⚠️" if lr_sev == 1 else "❌")
    lr_lines = [
        "",
        "## LightRAG (semantic search)",
        f"{lr_icon} {lr_status}",
    ]

    if lr_sev > 0 and cfg.get("lightrag", {}).get("url"):
        lr_lines.append(
            "   Per avviare: sul PC Office → docker compose up -d (nella cartella LightRAG)"
        )

    lines = lines[:verdict_idx] + lr_lines + [""] + lines[verdict_idx:]
    severity = max(severity, lr_sev if lr_sev < 2 else 1)  # LightRAG down = warning, non critical

    return "\n".join(lines), severity


import requests  # noqa: E402 (import in fondo ok per monkey-patch)
