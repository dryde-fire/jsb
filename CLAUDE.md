# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Cos'è questa repo

Due sistemi separati che comunicano tra loro (vedi `README.md`):

- **Sistema A — Second Brain** (`SECOND-BRAIN.md`): vault Obsidian sincronizzato via S3 su 3 PC; Ollama elabora di notte `inbox/` → `wiki/`. Il codice è in `scripts/`.
- **Sistema B — Workflow Claude Code** (`SETUP-CLAUDE-CODE.md`): solo documentazione e template per i progetti.
- **Bridge** (`BRIDGE.md`): le skill in `skills/` (`/recall` legge dal vault, `/distill-lesson` scrive in `inbox/notes/`).

`_research/` è materiale storico/di input, non runtime. I file `CLAUDE.md`, `CONTEXT.md`, `WORKFLOW.md`, `STATE.md` lì dentro sono **template per altri progetti**, non istruzioni per questa repo.

## Comandi

Niente build, niente test suite, niente lockfile delle dipendenze (servono `requests`, `pyyaml`). Gli script richiedono un `~/.jsb-config.json` valido e un vault esistente.

```powershell
python scripts/python/healthcheck.py           # report; exit 1 = warning, 2 = critico
python scripts/python/healthcheck.py --json
python scripts/python/ingest.py <file-inbox>   # elabora un solo file (debug)
python scripts/python/watchdog.py              # passata completa su inbox/ (è ciò che lancia Task Scheduler)
PowerShell -ExecutionPolicy Bypass -File scripts/powershell/Setup-Machine.ps1 [-SkipOllamaPull] [-SkipTaskScheduler]
```

Per provare senza toccare la config reale: `$env:JSB_CONFIG = "<path a una config di test>"` (ha la precedenza su `~/.jsb-config.json`).

## Architettura della pipeline (scripts/python)

- `jsb_core.py` è il modulo condiviso: config (con cache), log, state, quarantena, chiamate a Ollama con retry, scrittura in wiki. `load_config()` ricava i path dal `vault_path`: `inbox/`, `wiki/`, `archive/`, `_system/.ingest-state.json`, `_system/ingest-log.md`.
- Flusso: `watchdog.py` trova i file pendenti → `ingest.process_file()` → Ollama → `write_wiki_file()` (archivia la versione precedente in `archive/`).
- Invarianti da preservare:
  - lo state si aggiorna **solo dopo** un'elaborazione riuscita (`mark_success`/`mark_failure`);
  - l'hash è calcolato sul **body, escluso il frontmatter**, quindi le modifiche al solo frontmatter non fanno ri-elaborare il file;
  - dopo N fallimenti il file va in quarantena (`ingest.fail_quarantine_after_retries`);
  - ogni script fa `sys.path.insert(0, <dir dello script>)`, perché Task Scheduler li avvia da working directory arbitrarie.
- Il campo `type` nel frontmatter decide la cartella di `wiki/` (`TYPE_TO_FOLDER` in `ingest.py`). I tipi del bridge (`lesson-learned`, `architecture-decision`, `project-pattern`) vanno tenuti allineati con `skills/distill-lesson/SKILL.md`.
- Retrieval: niente indici o vector DB. `/recall` usa ripgrep sul vault più i `[[link]]` (pattern "LLM Wiki"). LightRAG è stato rimosso di proposito: non reintrodurlo senza una richiesta esplicita.

## Config multi-PC

Ogni PC ha un solo `%USERPROFILE%\.jsb-config.json`, copiato da `templates/jsb-config.{laptop,office,personal}.json`. Il campo `role` (`elaborator-fast` | `elaborator-quality` | `editor-only`) decide cosa gira su quel PC; `Ingest-Orchestrator.ps1` (Office PC) prova il WoL sul laptop e, se non risponde, elabora in locale. Niente path hardcoded nel codice: ogni nuova impostazione va nella config e in tutti e tre i template.

## Skill

Le `SKILL.md` usano un frontmatter cross-LLM (`compatible_agents`, `required_tools`, `config_dependencies`; vedi `CROSS-LLM-COMPAT.md`). Mantieni questo formato quando le modifichi.
