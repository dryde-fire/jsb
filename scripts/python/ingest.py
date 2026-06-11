#!/usr/bin/env python3
"""
ingest.py — Legge un file da inbox/, chiama Ollama, scrive elaborazione in wiki/.

Esposta come funzione `process_file(filepath, cfg) -> (success, error)`
da watchdog.py. Eseguibile anche standalone per debug:
    python ingest.py <path-to-inbox-file>
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from jsb_core import (  # noqa: E402
    call_ollama,
    load_config,
    log_msg,
    parse_frontmatter,
    split_frontmatter,
    write_wiki_file,
)


# -----------------------------------------------------------------------------
# Mappa tipo → cartella wiki
# -----------------------------------------------------------------------------

TYPE_TO_FOLDER: dict[str, str] = {
    "article": "learn",
    "brainstorm": "concepts",
    "idea": "concepts",
    "learning": "learn",
    "decision": "decisions",
    "pdf-excerpt": "learn",
    "ebook-note": "learn",
    "conversation": "concepts",
    # Tipi del bridge Claude Code
    "lesson-learned": "projects",
    "architecture-decision": "decisions",
    "project-pattern": "projects",
}


# -----------------------------------------------------------------------------
# Prompt builder
# -----------------------------------------------------------------------------


def build_prompt(file_type: str, body: str, body_limit: int) -> str | None:
    """Costruisce il prompt in base al tipo. Ritorna None se tipo sconosciuto."""
    truncated = body[:body_limit]
    note = "" if len(body) <= body_limit else f"\n\n[Nota: body troncato a {body_limit} caratteri su {len(body)} totali.]"

    templates = {
        "article": (
            "Elabora questo articolo per il wiki personale.\n"
            "Sezioni richieste:\n"
            "- Summary (2-3 righe)\n"
            "- Key Concepts (3-5 punti)\n"
            "- Key Takeaways (2-3 insight applicabili)\n"
            "- Related Topics (argomenti collegati da approfondire)\n\n"
            f"Articolo:\n---\n{truncated}\n---{note}\n\n"
            "Risposta in Markdown:"
        ),
        "brainstorm": (
            "Espandi questa idea in formato wiki, mantenendo l'energia originale.\n"
            "Sezioni: Core Idea, Implications, Next Steps, Open Questions.\n\n"
            f"Idea originale:\n---\n{truncated}\n---{note}\n\n"
            "Risposta in Markdown:"
        ),
        "idea": (
            "Espandi questa idea in formato wiki.\n"
            "Sezioni: Core Idea, Implications, Next Steps, Open Questions.\n\n"
            f"Idea:\n---\n{truncated}\n---{note}\n\n"
            "Risposta in Markdown:"
        ),
        "learning": (
            "Trasforma questa nota di apprendimento in un insight riusabile.\n"
            "Sezioni: What I Learned, Why It Matters, How To Apply, Related Concepts.\n\n"
            f"Nota:\n---\n{truncated}\n---{note}\n\n"
            "Risposta in Markdown:"
        ),
        "decision": (
            "Formalizza questa decisione come decision record.\n"
            "Sezioni: Context, Decision, Rationale, Alternatives Considered, Consequences.\n\n"
            f"Decisione:\n---\n{truncated}\n---{note}\n\n"
            "Risposta in Markdown:"
        ),
        "pdf-excerpt": (
            "Estrai e organizza i concetti chiave di questo excerpt.\n"
            "Sezioni: Main Argument, Key Points, How To Remember, Source Meta.\n\n"
            f"Excerpt:\n---\n{truncated}\n---{note}\n\n"
            "Risposta in Markdown:"
        ),
        "ebook-note": (
            "Estrai e organizza i concetti chiave di questo passaggio.\n"
            "Sezioni: Main Argument, Key Points, How To Remember, Source Meta.\n\n"
            f"Passaggio:\n---\n{truncated}\n---{note}\n\n"
            "Risposta in Markdown:"
        ),
        "conversation": (
            "Riassumi questa conversazione evidenziando gli insight.\n"
            "Sezioni: Topic, Key Insights, Decisions Made, Open Questions, Action Items.\n\n"
            f"Conversazione:\n---\n{truncated}\n---{note}\n\n"
            "Risposta in Markdown:"
        ),
        # Bridge Claude Code: questi arrivano già strutturati, fai light editing
        "lesson-learned": (
            "Questa è una lesson-learned estratta da un progetto Claude Code.\n"
            "Migliora la chiarezza ma preserva la struttura tecnica.\n"
            "Aggiungi una sezione 'Applicabile a:' con tipi di progetto futuri "
            "che potrebbero beneficiare.\n\n"
            f"Contenuto:\n---\n{truncated}\n---{note}\n\n"
            "Versione raffinata in Markdown:"
        ),
        "architecture-decision": (
            "Questo è un ADR estratto da un progetto. Preservalo "
            "letteralmente ma aggiungi una sezione 'Generalizable Pattern' "
            "che astrae la lezione applicabile ad altri progetti.\n\n"
            f"ADR:\n---\n{truncated}\n---{note}\n\n"
            "Output (ADR + Generalizable Pattern):"
        ),
        "project-pattern": (
            "Questo descrive un pattern emerso in un progetto.\n"
            "Sezioni: Pattern Name, Problem Solved, Solution Sketch, "
            "When To Use, When NOT To Use, Examples From Practice.\n\n"
            f"Pattern:\n---\n{truncated}\n---{note}\n\n"
            "Risposta in Markdown:"
        ),
    }

    return templates.get(file_type)


# -----------------------------------------------------------------------------
# Slug helper (per filenames sicuri su Windows)
# -----------------------------------------------------------------------------

import re  # noqa: E402

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def make_slug(title: str) -> str:
    """Slug filesystem-safe per filename Windows/Unix."""
    s = title.lower()
    s = _INVALID_FILENAME_CHARS.sub("", s)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s[:100] if s else "untitled"


# -----------------------------------------------------------------------------
# Process file (interfaccia con watchdog)
# -----------------------------------------------------------------------------


def process_file(
    filepath: Path, cfg: dict | None = None
) -> tuple[bool, str | None]:
    """
    Elabora un file da inbox/, scrive output in wiki/.

    Ritorna (success, error_message). error_message è None se success=True.

    Cambiamento rispetto allo script originale:
    - Ritorno strutturato → watchdog può aggiornare lo state correttamente
    - Quality threshold per i tipi del bridge (vedi build_prompt)
    """
    if cfg is None:
        cfg = load_config()

    filepath = Path(filepath)
    if not filepath.exists():
        return False, f"File non trovato: {filepath}"

    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError as e:
        return False, f"Impossibile leggere il file: {e}"

    fm_str, body = split_frontmatter(content)
    fm = parse_frontmatter(fm_str)
    file_type = fm.get("type", "unknown")
    title = filepath.stem

    body_limit = cfg.get("ingest", {}).get("body_char_limit", 10000)
    prompt = build_prompt(file_type, body, body_limit)

    if prompt is None:
        return False, f"Tipo sconosciuto: '{file_type}' (vedi templates in ingest.py)"

    # Scelta modello: default oppure quality, in base a fm.priority
    ollama_cfg = cfg.get("ollama", {})
    use_quality = fm.get("priority") == "high" or fm.get("quality_pass") is True
    model = (
        ollama_cfg.get("model_quality")
        if use_quality
        else ollama_cfg.get("model_default")
    )
    if not model:
        return False, "Modello Ollama non configurato (ollama.model_default mancante)"

    log_msg(
        "INFO",
        f"Modello={model}, tipo={file_type}, file={filepath.name}",
        cfg,
    )

    response = call_ollama(prompt, model, cfg)
    if not response:
        return False, "Ollama non ha risposto (vedi log per dettagli retry)"

    # Cartella di destinazione
    dest_folder = TYPE_TO_FOLDER.get(file_type, "learn")
    wiki_dest = cfg["_wiki_dir"] / dest_folder
    output_file = wiki_dest / f"{make_slug(title)}.md"

    # Frontmatter aggiornato
    fm["status"] = "published"
    fm["date_elaborated"] = datetime.now().isoformat(timespec="seconds")
    fm["elaborated_by"] = model
    fm["elaborated_on_machine"] = cfg.get("machine_id", "unknown")
    fm["source_file"] = str(filepath.relative_to(cfg["_vault_dir"])).replace("\\", "/")
    fm["version"] = fm.get("version", 1)

    try:
        write_wiki_file(output_file, fm, response, cfg)
    except OSError as e:
        return False, f"Scrittura wiki fallita: {e}"

    log_msg(
        "INFO",
        f"📝 wiki/{dest_folder}/{output_file.name}",
        cfg,
    )
    return True, None


# -----------------------------------------------------------------------------
# CLI per debug
# -----------------------------------------------------------------------------


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python ingest.py <percorso-file-inbox>")
        return 2

    target = Path(sys.argv[1])
    cfg = load_config()
    success, error = process_file(target, cfg)
    if success:
        print(f"✅ {target.name} elaborato con successo")
        return 0
    print(f"❌ {target.name}: {error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
