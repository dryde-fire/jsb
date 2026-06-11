# CLAUDE.md — Golden Workflow Configuration
# Authority Level: ADVISORY (~80% compliance)
# Override by: Hooks > Pre-commit > WORKFLOW.md > this file
# Max length enforced: 200 lines

<project_identity>
## Project
- Name: [PROJECT_NAME]
- Domain: [DOMAIN]
- Stack: [NODE/PYTHON/etc] + [FRAMEWORK] + [DB]
- Ticket prefix: [TY/PRJ/etc]-NNNN

## Quick Commands
npm run dev          # Start dev server
npm run test         # Run full test suite
npm run test:fast    # Run fast subset (pre-commit)
npm run build        # Production build
npm run preflight    # Pre-flight environment check
repomix              # Snapshot repo for AI context (see REPOMIX section)
</project_identity>

<behavioral_principles>
## Karpathy Principles — NON NEGOZIABILI

### P1 — Think Before Coding
- Mai assumere. Se c'è ambiguità, usa /grill-me prima di scrivere codice.
- Se sei confuso su qualcosa, DILLO esplicitamente invece di procedere.
- Una domanda posta prima vale più di 3 refactor dopo.

### P2 — Simplicity First
- Preferisci 100 righe a 1000 se risolvono lo stesso problema.
- No astrazione prematura. Non costruire infrastruttura per feature future ipotetiche.
- YAGNI: You Aren't Gonna Need It. PRIMA fai funzionare, POI generalizza.

### P3 — Surgical Changes
- Non toccare codice che non hai letto e capito completamente.
- Non rimuovere commenti senza capirne il motivo. Potrebbero documentare bug fix.
- Se devi modificare una funzione, leggi prima tutti i suoi caller.
- Scope minimo: cambia solo ciò che è necessario per il task corrente.

### P4 — Goal-Driven Execution
- Il tuo obiettivo è il COMPORTAMENTO corretto del sistema, non la completezza del codice.
- Definisci il criterio di successo PRIMA di scrivere la prima riga.
- "Il test passa" è un criterio. "Il codice sembra giusto" non lo è.
</behavioral_principles>

<repomix_protocol>
## Repomix — Snapshot Context Tool

### Quando usare repomix
- INIZIO di ogni sessione su codebase esistente (> 5 file coinvolti)
- Prima di un refactor significativo
- Quando passi il task a un subagente
- Prima di creare ADR (per avere vista completa)

### Comandi
```bash
# Snapshot standard (AI-optimized XML)
repomix --output repomix-snapshot.xml --style xml

# Snapshot filtrato per dominio specifico
repomix --include "src/payments/**,src/orders/**" --output repomix-payments.xml --style xml

# Snapshot con conteggio token (verifica prima di inviare)
repomix --output repomix-snapshot.xml --style xml --token-count-encoding cl100k_base

# Snapshot escludendo test e build
repomix --ignore "**/*.test.*,dist/**,node_modules/**" --output repomix-core.xml --style xml
```

### Progressive Disclosure — Regola dei Snapshot
- File completo (> 50K token): NON inviare tutto. Usa snapshot filtrato per sottodominio.
- File medio (10-50K token): OK come contesto iniziale.
- File piccolo (< 10K token): OK, aggiungi anche CONTEXT.md e ADR rilevanti.

### Snapshot Naming Convention
```
repomix-{dominio}-{YYYYMMDD}.xml
repomix-full-{YYYYMMDD}.xml
repomix-{task-id}-{YYYYMMDD}.xml
```

### Integrazione con WORKFLOW.md
Ogni agente spawned deve ricevere:
1. repomix snapshot filtrato per il suo dominio
2. CONTEXT.md (dominio)
3. ADR rilevanti (filtrati per categoria)
4. Task description specifica
MAI: l'intera history della sessione precedente.
</repomix_protocol>

<code_style>
## Code Style
- Language: [TypeScript strict / Python 3.11+ / etc]
- Modules: ES modules (import/export) — mai CommonJS
- Components: Functional + hooks — mai class components
- State: [Zustand / Redux / etc] — vedi src/stores/
- Naming: camelCase per variabili, PascalCase per tipi, kebab-case per file
- Max line: 100 caratteri
- Comments: in inglese, solo per WHY non per WHAT

## Key Architecture
- Vedi CONTEXT.md per ubiquitous language e regole di dominio
- Vedi docs/adr/ per decisioni architetturali passate
- Struttura: [descrivi brevemente src/, db/, docs/]
</code_style>

<critical_rules>
## Regole Critiche (MUST — non advisory)

- PRE-FLIGHT sempre: `npm run preflight` prima di ogni implementazione
- Test prima di commit: `npm run test` obbligatorio (hook garantisce)
- Identificatori immutabili: [TY-NNNN / UUID / etc] — mai modificare
- Soft delete only: mai eliminazione fisica di record critici
- ADR obbligatorio: ogni decisione architetturale deve creare o aggiornare un ADR
- Branch naming: feature/[ticket-id]-descrizione, bugfix/[ticket-id]-descrizione

## Escalation Policy (segui questo ordine)
1. Tentativo 1: approccio A
2. Tentativo 2 (stesso thread): approccio B radicalmente diverso — usa /rewind
3. Tentativo 3: STOP — notifica orchestratore — non continuare da solo
</critical_rules>
