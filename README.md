# Sandro's Knowledge Architecture

Questa repo contiene **due sistemi distinti che dialogano fra loro**, non un unico
prodotto. Capire la separazione è la prima cosa da fare.

```
                      ┌─────────────────────────────┐
                      │       BRIDGE.md             │
                      │  (regole di integrazione)   │
                      └──────┬───────────────┬──────┘
                             │               │
                ┌────────────▼──────┐  ┌────▼─────────────────┐
                │   SECOND BRAIN    │  │     CLAUDE CODE      │
                │ (knowledge mgmt)  │  │ (AI dev workflow)    │
                │                   │  │                      │
                │ Obsidian + Ollama │  │ CLAUDE.md + skills   │
                │ + S3 sync         │  │ + hooks + subagents  │
                │                   │  │                      │
                │ SECOND-BRAIN.md   │  │ SETUP-CLAUDE-CODE.md │
                └───────────────────┘  └──────────────────────┘
```

## I due sistemi

### Sistema A — Second Brain (memoria personale)

**Cosa fa**: cattura note in Obsidian, le sincronizza fra 3 PC via S3, e Ollama
le elabora di notte trasformando appunti grezzi (`inbox/`) in conoscenza
strutturata (`wiki/`).

**File guida**: `SECOND-BRAIN.md`

**Quando lo usi**: per leggere, scrivere, cercare nelle tue note personali.
Ogni giorno, da Obsidian.

### Sistema B — Claude Code (workflow di sviluppo)

**Cosa fa**: definisce come Claude Code lavora sui tuoi progetti di codice attraverso 6 livelli. I primi 4 sono tool esterni mantenuti dalla community (installa una volta, dimentica). Gli ultimi 2 (knowledge layer + governance) li scrivi tu.

**File guida**: `SETUP-CLAUDE-CODE.md`

**Quando lo usi**: ogni progetto di sviluppo segue questo setup. Tempo di onboarding: ~3 ore.

### Bridge — Integrazione

**Cosa fa**: permette ai progetti Claude Code di **leggere dal Second Brain**
("abbiamo già preso questa decisione?") e di **scriverci dentro** (lessons,
ADR, pattern emersi).

**File guida**: `BRIDGE.md`

## Configurazione: un solo file per PC

Tutti gli script (Python, PowerShell) e tutte le skill di Claude Code leggono
la configurazione locale da **un singolo file**:

```
%USERPROFILE%\.jsb-config.json     # Windows
~/.jsb-config.json                  # macOS/Linux
```

Template per i tre PC sono in `templates/`:
- `jsb-config.laptop.json` — XPS 15, GPU, role=elaborator-fast
- `jsb-config.office.json` — Office PC, sempre acceso, role=elaborator-quality
- `jsb-config.personal.json` — Personal PC, role=editor-only

**Cambi PC, cambi un file. Nessun hardcoded path nel codice.**

## Struttura della repo

```
.
├── README.md                          ← sei qui
├── BRIDGE.md                          ← integrazione fra i due sistemi
├── CROSS-LLM-COMPAT.md                ← portabilità skill, exit strategy, Hermes
│
├── SECOND-BRAIN.md                    ← guida operativa Sistema A
├── SETUP-CLAUDE-CODE.md                ← guida operativa Sistema B (6 livelli)
├── CHANGELOG.md                       ← evoluzione storica
│
├── templates/
│   ├── jsb-config.laptop.json
│   ├── jsb-config.office.json
│   └── jsb-config.personal.json
│
├── scripts/
│   ├── python/
│   │   ├── jsb_core.py                ← modulo condiviso (config, log, hash, retry)
│   │   ├── watchdog.py                ← monitora inbox/, trigghera ingest
│   │   ├── ingest.py                  ← elabora un file con Ollama
│   │   └── healthcheck.py             ← diagnostica settimanale
│   └── powershell/
│       ├── Setup-Machine.ps1          ← setup di base, agnostico al ruolo
│       ├── Wake-Laptop.ps1            ← magic packet per WoL
│       └── Ingest-Orchestrator.ps1    ← Office PC: routing laptop/locale
│
├── skills/                            ← skill per Claude Code
│   ├── recall/SKILL.md                ← /recall: cerca nel vault
│   └── distill-lesson/SKILL.md        ← /distill-lesson: scrive nel vault
│
└── _research/                         ← storico documentale (non runtime)
    │
    ├── analisi-repos-claude-code.md      ← analisi 12 repo (input per setup)
    ├── claude-code-best-practices-DEFINITIVO.md  ← best practice v2.0 (input)
    ├── hybrid-agentic-architecture-guide.md      ← principi Symphony+Claude
    │
    ├── CHANGELOG.md                      ← evoluzione storica v1→v4
    ├── HYBRID-AGENTIC-ARCHITECTURE-v4.0-COMPLETE.md  ← arch 5-layer completa
    │
    ├── CLAUDE.md                         ← template per-progetto (golden workflow)
    ├── CONTEXT.md                        ← template per-progetto (domain knowledge)
    ├── WORKFLOW.md                       ← template per-progetto (agent contract)
    ├── STATE.md                          ← template per-progetto (session state)
    ├── ADR-000-template.md               ← template ADR standard
    │
    └── gestione multi pc/
        └── QUICK-REFERENCE.md           ← cheat sheet quotidiano (allineato v4.0)
```

## Onboarding per ogni PC

### Personal PC (sandr) — editor-only

```powershell
# 1. Copia jsb-config.personal.json → %USERPROFILE%\.jsb-config.json
# 2. Adatta vault_path se diverso
# 3. Configura Obsidian + Remotely Save (S3 Cloudflare)
# 4. Done. Niente Ollama, niente Python.
```

### Office PC (MS-Sandro) — elaborator-quality

```powershell
# 1. Copia jsb-config.office.json → %USERPROFILE%\.jsb-config.json
# 2. Esegui Setup-Machine.ps1 (installa Python deps, Ollama, registra Task Scheduler)
# 3. Pull modelli: ollama pull gemma4:e2b && ollama pull gemma4:e4b
# 4. Configura TrustedHosts per WoL/PSRemoting verso laptop
# 5. Test: python scripts/python/healthcheck.py
```

### Laptop (XPS 15) — elaborator-fast

```powershell
# 1. Copia jsb-config.laptop.json → %USERPROFILE%\.jsb-config.json
# 2. Esegui Setup-Machine.ps1
# 3. Pull modello: ollama pull gemma4:e2b
# 4. Abilita WoL in BIOS, registra MAC su Office PC
# 5. Test: python scripts/python/healthcheck.py
```

## Come si usano i due sistemi nella pratica

### Catturo un'idea o un articolo
→ Obsidian su Personal PC (o iPhone) → file in `inbox/notes/` o `inbox/articles/`
→ Sync S3 → Office PC pull → Ollama nightly elabora → file in `wiki/`
→ Sync S3 → Personal PC e Laptop ricevono il wiki/ aggiornato

### Inizio un progetto Claude Code
→ Apro il progetto → Claude Code legge CLAUDE.md
→ Chiedo: "abbiamo già fatto qualcosa di simile?"
→ Skill `/recall` cerca in `wiki/` → mi propone reference
→ Includo le reference rilevanti nel `CONTEXT.md` del progetto

### Finisco una feature significativa
→ Skill `/distill-lesson` mi propone di salvare lessons-learned/ADR nel vault
→ Confermo → file scritto in `inbox/notes/` con frontmatter giusto
→ Ollama nightly lo elabora come qualsiasi altra nota

## Stato del progetto

| Componente | Stato |
|---|---|
| Sistema A — Second Brain (capture/sync/elaborazione) | ✅ Production ready |
| Sistema B — Claude Code 6-livelli (Livelli 1-4 esterni) | ✅ Tool installabili |
| Sistema B — Knowledge Layer (CLAUDE.md, CONTEXT.md, ADR) | 🛠️ Per-progetto, scrivi tu |
| Sistema B — Governance (WORKFLOW.md) | 🛠️ Per-progetto, scrivi tu |
| Bridge `/recall` v3 (ripgrep + link fra note) | ✅ Skill operativa |
| Bridge `/distill-lesson` | ✅ Skill operativa con guardrail |
| Cross-LLM compat (agentskills.io) | ✅ Skill formattate da subito |
| Symphony Orchestration | ❌ Out of scope (coperto da superpowers) |
| L5 Distribution / manifest.json | ❌ Out of scope (coperto da plugin marketplace) |
| Hermes Agent integration | 📅 Roadmap Fase 3 (opzionale) |

## Roadmap a fasi

Il sistema è progettato per essere **utile da subito** e **estendibile gradualmente**.
Ogni fase è indipendente e puoi fermarti a qualunque livello.

**Fase 1 (oggi → fine Maggio 2026)** — Sistema base
- Multi-PC sync via S3, elaborazione nightly Ollama, bridge full-text con Claude Code
- Tempo: ~2 settimane di onboarding sui 3 PC

**Fase 2 (Giugno-Luglio 2026, opzionale)** — Semantic search locale
- Aggiunta modulo `vault_search.py` con FTS5/SQLite per ricerca rank-aware
- Niente nuove dipendenze esterne, niente WSL2
- Migliora la qualità di `/recall` ma non lo rivoluziona

**Fase 3 (Q3 2026, opzionale)** — Hermes Agent come voce parlante
- Integrazione Hermes per memoria persistente cross-session
- Telegram/Discord gateway: chatti col Second Brain dal telefono
- Hermes usa la tua API key Claude Pro per task importanti, Ollama per leggeri
- Richiede WSL2 sull'Office PC (~45 min setup)
- Vedi `CROSS-LLM-COMPAT.md` sezione 4 per dettagli

**Fase 4 (quando serve)** — Cross-LLM completo
- Le skill già scritte funzioneranno con Codex, Cursor, Gemini CLI
- Vedi `CROSS-LLM-COMPAT.md`

**Importante**: niente di tutto questo è obbligatorio. Se la Fase 1 ti basta,
il sistema è completo così. Se domani volessi abbandonare tutto, il vault
Obsidian rimane tuo e leggibile in qualunque editor (vedi `CROSS-LLM-COMPAT.md`
sezione 6, "Exit Strategy").

## Manutenzione settimanale

```powershell
# Dal PC più comodo (di solito Office)
python scripts/python/healthcheck.py
```

Output: report markdown che ti dice se Ollama ha girato, se ci sono file
bloccati, se ci sono file in quarantena.

## Riferimenti

- Decisioni storiche: `CHANGELOG.md`
- Best practice Claude Code (input): `_research/claude-code-best-practices-DEFINITIVO.md`
