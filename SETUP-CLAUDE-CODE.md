# SETUP-CLAUDE-CODE.md — Sistema B Definitivo

**Versione**: 4.1 (Maggio 2026)
**Sostituisce**: SETUP-DEFINITIVO-v4_0-FOR-DUMMIES-COMPLETE.md, ARCHITECTURE-CLAUDE-CODE.md, e tutti i setup Claude Code precedenti
**Posizione nell'architettura**: questo è il **Sistema B**. Per il Second Brain (Sistema A) vedi `SECOND-BRAIN.md`. Per come dialogano vedi `BRIDGE.md`.

---

## Filosofia

La struttura è a **6 livelli**. I primi 4 sono tool esterni mantenuti dalla community: installa una volta, dimentica. Gli ultimi 2 sono quello che scrivi tu, perché nessuno può saperli al posto tuo: il tuo dominio, le tue regole, la tua governance.

**Tempo totale di setup**: ~3 ore per progetto.

**Cosa è cambiato rispetto al v4.0 originale**:
- Livello 3 (harness) ora è Go-native, non più TypeScript. Sub-10ms response. **No Node.js richiesto** per harness specifico (Node serve solo per repomix al Livello 4).
- 13 regole guardrail (R01-R13), non 9 come dichiarato in v4.0. Più protezioni di base.
- Aggiunto **Livello 5b** che integra le skill custom del bridge con Sistema A (Second Brain).

---

## Livello 1 — Fondamenta comportamentali

**`forrestchang/andrej-karpathy-skills`**

Inietta i 4 principi di ragionamento di Karpathy in ogni sessione. Zero overhead, zero configurazione.

```bash
# Installazione
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin install andrej-karpathy-skills
```

**Non toccare, non customizzare.** È pensato per essere invisibile: lavora di base in ogni sessione, migliora la qualità del ragionamento dell'agente.

---

## Livello 2 — Execution methodology

**`obra/superpowers`**

Gestisce il workflow di esecuzione: brainstorming socratico, plan scritto, TDD enforcement (Iron Law), subagent dispatch con two-stage review.

```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**Fix obbligatorio post-installazione** — aggiungi questo a `.claude/settings.json` di ogni progetto:

```json
{
  "hooks": {
    "SubagentStart": {
      "command": "cat ~/.claude/skills/using-superpowers/SKILL.md",
      "description": "Inject superpowers discipline into subagents"
    }
  }
}
```

Senza questo fix, i subagent dispatched non ereditano la disciplina superpowers e si comportano come agenti vanilla. Con il fix, ogni subagent legge le regole prima di partire.

**Non documentare TDD, plan, subagent patterns**: è già nel framework, troveresti drift fra docs tue e comportamento reale.

---

## Livello 3 — Guardrail deterministici

**`Chachamaru127/claude-code-harness`** (v4 Hokage, Go-native)

Gestisce: 13 regole guardrail runtime (R01-R13), hooks lifecycle, harness-mem cross-sessione, review post-execution. Single binary Go con sub-10ms response. Non richiede Node.js.

```bash
/plugin marketplace add Chachamaru127/claude-code-harness
/plugin install claude-code-harness@claude-code-harness-marketplace
/harness-setup
```

**Configurazione minima** — `claude-code-harness.config.yaml` nella root del progetto:

```yaml
plan_ssot: Plans.md          # generato da superpowers (Livello 2)
tech_choice_mode: fixed      # stack fisso, non auto-decide

protected_paths:
  - .env
  - .env.*
  - credentials/
  - secrets/
  - .git/
```

Le 13 regole (R01-R13) coprono: blocco `sudo`, deny write su `.git/`/`.env`/`secrets/`, deny `rm -rf /` e path distruttivi, deny `git push --force`, mode-specific guards, anti-tampering test, auto-allow comandi safe (git status, npm test).

**Non documentare i guardrail**: sono dichiarativi nel codice harness, leggi `bin/harness/internal/guardrail/` se vuoi capirli, ma non duplicarli nel tuo CLAUDE.md.

---

## Livello 4 — Context management

**`yamadashy/repomix`** + **`thedotmack/claude-mem`**

Repomix bundla il codebase a inizio sessione (utile per onboarding di Claude su progetti nuovi). claude-mem dà persistenza cross-sessione.

```bash
# Repomix (richiede Node.js 18+)
npm install -g repomix

# claude-mem
/plugin install claude-mem
# oppure: npx claude-mem install
```

Nessuna configurazione aggiuntiva necessaria.

---

## Livello 5 — Knowledge Layer (scrivi tu)

I 3 file di questo livello sono **irriducibili**: nessun tool li genera per te perché contengono il dominio del *tuo* progetto specifico.

### `CLAUDE.md` (< 200 righe)

Comandi bash del progetto, code style, architettura, regole critiche.

Template minimo:

```markdown
# CLAUDE.md

## Stack
- Linguaggio: [TypeScript / Python / ...]
- Framework: [Next.js / FastAPI / ...]
- Database: [PostgreSQL / ...]
- Test: [Vitest / pytest / ...]

## Comandi essenziali
- `pnpm dev` — dev server (porta 3000)
- `pnpm test` — esegue test (Iron Law: tutti i test devono passare prima di commit)
- `pnpm build` — build produzione
- `pnpm typecheck` — verifica TypeScript

## Code style
- Indentazione: 2 spazi
- Quotes: double per stringhe TS, single per stringhe Python
- Naming: camelCase per JS/TS, snake_case per Python
- Import order: standard lib → third-party → locali

## Architettura
- Layer separation: api/ → services/ → repositories/ → db/
- Mai chiamare repositories direttamente dal layer api/
- Errori custom in shared/errors.ts, non throw stringhe

## Regole critiche
- Mai modificare schema DB senza ADR (vedi docs/adr/)
- Mai committare credenziali, anche per test (.env è in .gitignore)
- Test prima del codice (TDD enforced da superpowers)
```

### `CONTEXT.md`

Linguaggio del dominio, business rules, invarianti.

Template minimo:

```markdown
# CONTEXT.md

## Ubiquitous Language

| Termine | Significato nel dominio |
|---------|------------------------|
| [Termine 1] | [Definizione precisa] |
| [Termine 2] | [Definizione precisa] |

## Business rules

1. [Regola 1 — invariante che non può essere violata]
2. [Regola 2]

## Edge cases noti

- [Caso 1: cosa fare quando X accade]
- [Caso 2: ...]

## Reference Material from Personal Knowledge

[Sezione popolata dalla skill /recall del bridge con Sistema A — vedi BRIDGE.md]
```

L'ultima sezione viene popolata automaticamente dalla skill `/recall` quando inizi un progetto e chiedi "abbiamo già fatto qualcosa di simile?". Vedi sezione "Livello 5b" sotto.

### `docs/adr/` (almeno 2-3 ADR retroattivi)

Architecture Decision Records già prese. Formato minimo:

```markdown
---
id: ADR-001
status: Accepted
date: 2026-05-09
decision: Usare PostgreSQL invece di MongoDB per transazioni ACID
categories: [backend, database]
---

## Context
[Il problema o il contesto]

## Decision
[Cosa hai deciso, in modo imperativo]

## Consequences
[Cosa segue da questa decisione, positivo e negativo]

## Alternatives considered
- [Alternative pesate e perché scartate]
```

**Convenzione minimal vs full**: usa il minimal sopra per ADR retroattivi rapidi. Per decisioni nuove e importanti, espandi le sezioni.

---

## Livello 5b — Custom Skills (Bridge con Sistema A)

Questo livello aggiunge le **skill personalizzate** che collegano Claude Code al tuo Second Brain. Sono opzionali ma raccomandate se hai un Sistema A funzionante.

### Skill `/recall` — Lettura dal vault

Cerca nel Second Brain progetti, decisioni e pattern simili a quello attuale. Usa ripgrep sul vault locale, espandendo la query in sinonimi e seguendo i `[[link]]` fra note.

**Installazione**:
```bash
# Copia la cartella della skill nella tua home Claude
cp -r skills/recall ~/.claude/skills/recall
```

**Quando si attiva** (automaticamente in base alla tua frase):
- "abbiamo già fatto qualcosa di simile?"
- "cerca nel mio vault"
- "ricerca progetti passati"
- "ho già preso questa decisione?"

**Output**: max 5 file rilevanti dal `wiki/` del Second Brain, con tag, versione, e snippet del contenuto. Tu scegli cosa includere nel CONTEXT.md.

### Skill `/distill-lesson` — Scrittura nel vault

Estrae lessons-learned, pattern, e architecture decisions dal progetto attuale e li scrive nell'inbox del Second Brain.

**Installazione**:
```bash
cp -r skills/distill-lesson ~/.claude/skills/distill-lesson
```

**Quando si attiva**:
- "salva questa lezione nel vault"
- "questo è un pattern che voglio ricordare"
- Alla fine di una feature significativa, **con conferma esplicita**

**Quality check**: la skill ha 5 domande di filtro per evitare di sporcare il vault con rumore. Vedi `BRIDGE.md` sezione "Quality check".

### Configurazione richiesta

Le skill leggono `~/.jsb-config.json` per sapere dove sta il vault. Vedi `templates/jsb-config.{laptop,office,personal}.json` e `SECOND-BRAIN.md` sezione 3.

**Cross-LLM**: queste skill sono in formato `agentskills.io v1`. Funzionano identicamente con Claude Code, Codex CLI, Cursor, Gemini CLI, Hermes Agent. Vedi `CROSS-LLM-COMPAT.md`.

---

## Livello 6 — Governance Layer

Questo è il **15-18% che nessun tool copre**. Il contratto umano/AI per il tuo progetto.

### `WORKFLOW.md` — il contratto

Deve rispondere a 3 domande: cosa puoi fare da solo? cosa richiede il mio OK? quando devi fermarti?

```markdown
# WORKFLOW.md

## Classi di decisione

### Autonomia AI completa (nessun checkpoint)
- Bug fix con test esistenti che passano
- Refactor entro file singolo, senza cambio API pubblica
- Aggiornamento dipendenze minor (semver patch/minor)
- Aggiunta test per codice esistente
- Type fix (TypeScript strict mode)

### Checkpoint umano obbligatorio (ferma e chiedi prima di procedere)
- Nuova feature con impatto su schema DB
- Modifica a endpoint pubblici (API contract)
- Qualsiasi decisione architetturale → crea ADR prima
- Task che tocca più di 5 file
- Cambio di dipendenze major (semver major)
- Modifica a `.env`, configurazioni di deploy

### Escalation immediata (stop + notifica)
- 2 approcci falliti sullo stesso problema (Iron Law: dopo 2 fail, fermati)
- Dipendenza esterna non raggiungibile (DB, API)
- Conflitto tra ADR esistente e task richiesto
- Errore di sicurezza rilevato (credenziale leaked, vulnerability)
- Test che fallivano e ora passano "magicamente" (sospetto tampering)

## Patterns ricorrenti del progetto

[Documenta qui i pattern emersi nel tempo, popolato a mano o tramite /distill-lesson]

## Postmortem template

Se accade un escalation, registra qui:
- Cosa è successo
- Cosa hai fatto
- Cosa modificare nel WORKFLOW.md per prevenire
```

---

## Struttura cartelle risultante

```
progetto/
├── CLAUDE.md                          ← Livello 5 (scrivi tu)
├── CONTEXT.md                         ← Livello 5 (scrivi tu)
├── WORKFLOW.md                        ← Livello 6 (scrivi tu)
├── Plans.md                           ← generato da superpowers, SSOT
├── docs/
│   └── adr/                           ← Livello 5 (scrivi tu)
│       ├── ADR-001-postgres-vs-mongo.md
│       └── ADR-002-stripe-integration.md
├── .claude/
│   ├── settings.json                  ← SubagentStart hook fix
│   └── skills/                        ← skills custom di progetto
├── claude-code-harness.config.yaml    ← Livello 3
└── .gitignore                         ← include .env, .env.*, credentials/

# Skills globali (in ~/.claude/skills/, non nel progetto)
~/.claude/skills/
├── recall/                            ← Livello 5b — Bridge lettura
└── distill-lesson/                    ← Livello 5b — Bridge scrittura
```

---

## Tempo stimato

| Attività | Tempo |
|----------|-------|
| Installazione Livelli 1-4 | 30 min |
| CLAUDE.md + CONTEXT.md | 1 ora |
| ADR retroattivi (2-3) | 30 min |
| WORKFLOW.md governance | 45 min |
| Installazione skill 5b (recall + distill-lesson) | 5 min |
| Test ciclo completo | 30 min |
| **Totale** | **~3 ore e 20 min** |

---

## Cosa NON serve documentare (perché i tool lo gestiscono)

Il v3.0 documentava tutto: hooks, pre-commit, TDD workflow, subagent patterns. Adesso quei capitoli **non esistono più** perché:

| Funzionalità | Gestita da |
|-------------|-----------|
| TDD enforcement (Iron Law) | superpowers (Livello 2) |
| Subagent dispatch + two-stage review | superpowers |
| Brainstorming socratico | superpowers |
| Plan come SSOT | superpowers (genera `Plans.md`) |
| Guardrail su `.git/`, `.env`, `rm -rf` | harness (Livello 3) |
| Hooks lifecycle (PreToolUse, PostToolUse, etc.) | harness |
| Post-execution review | harness |
| Memory cross-sessione | harness-mem + claude-mem (Livelli 3-4) |
| Context bundling iniziale | repomix (Livello 4) |

Rimane solo quello che i tool non possono sapere al posto tuo: il **tuo dominio**, le **tue regole**, la **tua governance**.

---

## Onboarding di un nuovo progetto

1. **Crea cartella e Git**: `mkdir nuovo-progetto && cd nuovo-progetto && git init`
2. **Apri Claude Code**: `claude`
3. **Installa Livelli 1-4** (15 min con i comandi sopra)
4. **Esegui `/harness-setup`**: bootstrap dei file harness
5. **Scrivi CLAUDE.md, CONTEXT.md, WORKFLOW.md** (1.5-2 ore)
6. **Crea 2-3 ADR retroattivi** se hai decisioni già prese
7. **Aggiungi skill 5b** se vuoi il bridge con Second Brain
8. **Test**: chiedi a Claude di fare una piccola modifica e verifica che il workflow funzioni

---

## Manutenzione

**Settimanale**:
- Review `Plans.md` — sono task chiusi correttamente?
- Review `MEMORY.md` (gestita da harness-mem) — qualche pattern emerso da promuovere a CLAUDE.md?

**Mensile**:
- Aggiornamenti tool: `/plugin update <nome>` per ognuno dei livelli 1-4
- Review ADR — qualcuno è diventato obsoleto? Marcalo come `status: Superseded by ADR-XXX`

**Trimestrale**:
- Audit `WORKFLOW.md`: le 3 classi sono ancora corrette? Hai avuto escalation che andrebbero codificate?

---

## Roadmap & Limiti onesti

**Cosa funziona oggi**:
- Tutti e 4 i livelli tool installabili in ~30 min
- Sistema A (Second Brain) integrato via skill 5b
- Cross-LLM via agentskills.io standard

**Cosa è esplicitamente fuori scope**:
- ❌ Symphony Orchestration (multi-agent oltre i subagent superpowers): NON implementato. Era nel v4.0 originale come "concettuale", ora superpowers copre il caso d'uso reale al ~80%.
- ❌ L5 Distribution / manifest.json: NON implementato. Sostituito dal plugin marketplace di Claude Code 2.1+.

**Cosa potrebbe arrivare**:
- Hermes Agent (Q3 2026, opzionale): gateway Telegram/Discord verso Second Brain. Vedi `CROSS-LLM-COMPAT.md` sezione 4.

---

## Riferimenti

| Tool | Link |
|------|------|
| andrej-karpathy-skills | https://github.com/forrestchang/andrej-karpathy-skills |
| superpowers | https://github.com/obra/superpowers |
| claude-code-harness | https://github.com/Chachamaru127/claude-code-harness |
| repomix | https://github.com/yamadashy/repomix |
| claude-mem | https://github.com/thedotmack/claude-mem |

| Documento del setup | File |
|---------------------|------|
| Mappa generale | `README.md` |
| Sistema A (Second Brain) | `SECOND-BRAIN.md` |
| Bridge fra A e B | `BRIDGE.md` |
| Compatibilità cross-LLM | `CROSS-LLM-COMPAT.md` |
| Migrazione | `MIGRATION.md` |

---

## Acknowledgments

- **Mitchell Hashimoto** — concetto originale di harness engineering ("AGENTS.md as failure log")
- **Andrej Karpathy** — i 4 principi di ragionamento (Livello 1)
- **Forrest Chang, obra, Chachamaru127** — autori dei tool open source che reggono i Livelli 1-3
