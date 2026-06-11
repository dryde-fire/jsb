# Claude Code Best Practices - DOCUMENTO DEFINITIVO
**Versione**: 2.0 - Definitiva  
**Data**: 29 aprile 2026  
**Fonti verificate**:
- Docs ufficiali Anthropic (docs.anthropic.com)
- Repository shanraisshan/claude-code-best-practice (19.7k ⭐)
- Repository mattpocock/skills (23.1k ⭐)

---

## 🎯 COME LEGGERE QUESTO DOCUMENTO

Ogni sezione usa questi marker:
- ✅ **VERIFICATO**: Documentato in fonti ufficiali
- ⚠️ **EMPIRICO**: Validato dalla community, non ufficiale
- 🔄 **COMPLEMENTARE**: Aggiunge contesto da multiple fonti
- 🚨 **CRITICO**: Ignorare questo costa produttività

---

# PARTE 1: FONDAMENTI - I TRE PILASTRI

## 1.0 I Tre Pilastri di Claude Code

Claude Code non è "DAI semplicemente il prompt". È un ecosistema con tre pilastri fondamentali:

### Pilastro 1: Context Management (La risorsa più critica)
- Claude's context window è **finito** e si riempie velocemente
- La performance **degrada** man mano che il context cresce
- **Strategia**: Compattare al 50%, non aspettare il 90%

### Pilastro 2: Planning Before Execution (La matematica del successo)
- Senza planning: successo ~1% (0.8^20 = la probabilità che 20 decisioni vadano bene)
- Con planning approvato: successo vicino a 100%
- **Strategia**: Plan mode → approvazione → execution

### Pilastro 3: Automation & Isolation (Composizione senza contaminazione)
- Skills, hooks, subagenti isolano il contesto
- Riusabilità senza cross-contamination
- **Strategia**: Feature-specific skills, non generiche

---

# PARTE 2: SISTEMA DI BASE (CLAUDE.md + CONTEXT.md)

## 2.1 CLAUDE.md - Il Manifesto del Progetto

### ✅ Specifiche Ufficiali

**Lunghezza massima**: <u>200 righe per file</u>

**Quando viene caricato**: All'inizio di OGNI conversazione con Claude Code

**Cosa includervi** (in ordine di priorità):
1. Comandi bash comuni (`npm run test`, `npm run build`, `npm run dev`)
2. Linee guida di stile del codice (ES modules, naming conventions)
3. Pattern architetturali critici
4. Nomi di file/directory chiave
5. Workflow rules specifiche del progetto

**Cosa NON includervi** (spreca token):
- Cose che Claude può dedurre dal codice
- Istruzioni manuali step-by-step
- Spiegazioni lunghe (resoconto, non manuale)

### 📊 Template CLAUDE.md (< 200 linee)

```markdown
# CLAUDE.md - [Project Name]

## Quick Commands
npm install              # Install dependencies
npm run dev             # Start dev server
npm run build           # Production build
npm run test            # Run all tests
npm run test --watch    # Watch mode
git status              # Check git status

## Code Style
- Use ES modules (import/export), never CommonJS
- Functional components + React hooks only
- Use Zustand for state (see src/stores/)
- Always use TypeScript strict mode
- Max line length: 100 characters
- Use kebab-case for filenames, camelCase for code

## Key Architecture
- Backend: Node.js + Express (see src/api/)
- Database: PostgreSQL (migrations in db/)
- Frontend: React + TypeScript
- Testing: Vitest for unit, Playwright for e2e
- API docs: /docs/api.md

## Critical Rules (MUST follow)
- NEVER modify database schema without a migration
- ALWAYS run `npm run test` before committing
- ALWAYS include ticket number in commit messages
- NEVER commit directly to main branch
- Environment variables in `.env.local`, not code

## File Structure
src/
  ├── api/           # Express endpoints
  ├── db/            # Database (migrations, queries)
  ├── components/    # React components
  ├── stores/        # Zustand stores
  └── utils/         # Utilities

## When Stuck
1. Run `npm run test` to find the exact error
2. Check recent commits with `git log --oneline -10`
3. Review the ADR in docs/adr/ for context
4. Ask: "What's the smallest failing test?"
```

### 🔄 Integrazione con CONTEXT.md

**NEW in mattpocock/skills**: Usa **CONTEXT.md** per domain knowledge:

```markdown
# CONTEXT.md - Domain Knowledge

## Ubiquitous Language (DDD)
- **Order**: Customer request for products
- **LineItem**: Individual product in an order
- **Fulfillment**: Process of shipping an order
- **SKU**: Stock Keeping Unit identifier

## Key Business Rules
- Orders can only transition: Pending → Paid → Shipped → Delivered
- LineItems with quantity > 100 trigger bulk discount
- Refunds must happen within 30 days

## Architecture Decisions
See docs/adr/ for:
- ADR-001: Why we chose PostgreSQL over MongoDB
- ADR-002: Why Zustand over Redux
- ADR-003: Why vertical slicing in API design
```

**Beneficio**: Claude capisce il linguaggio del dominio, non solo il codice

---

## 2.2 CLAUDE.md Compliance: Hooks vs Guidance

| Tipo | Compliance | Quando Usare |
|------|-----------|-------------|
| **CLAUDE.md** | ~80% | Guidance e best practices |
| **Hooks** | 100% | Azioni che DEVONO succedere sempre |
| **Pre-commit** | 100% | Validazione prima di commit |

**Regola**: Se qualcosa deve succedere senza eccezione (linting, formatting, security checks), non va in CLAUDE.md — va in **Hooks** o **Pre-commit**.

---

# PARTE 3: PLANNING SYSTEM (La matematica del successo)

## 3.1 Plan Mode - Shift+Tab (due volte)

### ✅ VERO - Il Principio Matematico

**La formula**:
- Claude fa la scelta giusta l'80% delle volte
- Una feature tipica ha ~20 decision points
- Senza planning: 0.8^20 ≈ **1% successo**
- Con planning approvato: vicino a **100%**

**Perché**: Il planning collassa 20 decisioni ambigue in un piano dove OGNI scelta è stata già fatta dall'umano.

### ✅ VERO - Come Entrare in Plan Mode

```
Shift+Tab (una volta):  Uscire dall'implementation mode
Shift+Tab (due volte):  Entrare in plan mode vero
```

**Workflow plan mode**:
1. Entra con Shift+Tab x2
2. Discuti il piano con Claude (iterativo)
3. Claude pone domande specifiche
4. Tu fornisci contesto mancante
5. Plan viene approvato
6. Premi Shift+Tab (una volta) per passare a implementation
7. I piani **persistono** anche se la sessione si resetta

### 🎯 Quando Usare Plan Mode

| Situazione | Approccio | Effort |
|-----------|-----------|--------|
| Bug fix semplice (< 30 min) | Vanilla Claude Code | Basso |
| Feature leggera (< 4 ore manuale) | Shift+Tab plan mode | Basso |
| Feature media (4-24 ore) | Spec scritto + planning session | Medio |
| Feature complessa (> 24 ore) | Spec dettagliato + cross-model review | Alto |
| Refactor significativo | `request-refactor-plan` skill | Medio |

---

## 3.2 PLANNING SKILLS - Automazione del Planning

### 🎯 NEW: Planning come Skills (non solo guidance)

Mattpocock ha reso il planning **explicitamente automato** tramite skills:

#### Skill: `to-prd` (Specifiche PRD)
```
/to-prd
→ Sintetizza l'intera conversazione in un PRD
→ Submitte come GitHub issue
→ Nessuna intervista — solo sintesi di quello che avete discusso
```

**Uso**: Quando hai discusso vagamente una feature e vuoi una spec formale
**Beneficio**: Cattura il contesto, lo struttura, crea issue

#### Skill: `grill-me` (Decision Tree Validation)
```
/grill-me
→ Claude ti intervista RELENTLESSLY su un piano
→ Continua fino a quando ogni branch è risolto
→ Scopre ambiguità prima del coding
```

**Uso**: Quando il piano sembra solido ma sai che ci sono edge case
**Beneficio**: Forza completezza delle decisioni

#### Skill: `to-issues` (Vertical Slicing)
```
/to-issues
→ Prende un piano/spec/PRD
→ Lo rompe in issue indipendenti
→ Usa vertical slices (non layer slices)
```

**Uso**: Dopo aver approvato il piano, crea task grabbare-able
**Beneficio**: Ogni issue è indipendentemente implementabile

#### Skill: `request-refactor-plan` (Interview-Driven Refactor)
```
/request-refactor-plan
→ Intervista per capire il refactor
→ Crea un piano dettagliato con tiny commits
→ File come GitHub issue con step-by-step
```

**Uso**: Prima di refactor significativi
**Beneficio**: Pianifica il refactor con precision, split in commit atomici

#### Skill: `design-an-interface` (Parallel Design)
```
/design-an-interface
→ Genera multiple design RADICALMENTE diversi
→ Usa parallel sub-agents (esecuzione parallela)
→ Confronta approcci
```

**Uso**: Quando hai libertà di design
**Beneficio**: Esplora lo spazio di design senza sequenzialità

---

# PARTE 4: EXECUTION SYSTEM (Code + Testing)

## 4.1 Context Management - La Risorsa Critica

### ✅ VERO - Context Window è Finito

**Fatto fondamentale**: 
- Tutta la conversazione occupa spazio
- Ogni file che leggi occupa spazio
- Ogni comando output occupa spazio
- Performance **degrada** man mano che il context cresce

### ✅ VERO - Strategia: Compattazione Manuale al 50%

**Pratica verificata**:
- Non aspettare fino al 90% (la "dumb zone")
- Quando raggiungi il **50%**, esegui manualmente `/compact`
- Questo previene la degradazione severa

**Come monitorare**:
```
/context              # Vedi l'utilizzo attuale
/compact              # Compatta manualmente
```

### ✅ VERO - Esc Esc per Rewind (Tornare Indietro)

**Pattern quando Claude va off-track**:
1. Non cercare di "fissare" il contesto contaminato
2. Premi **Esc Esc** (o digita `/rewind`)
3. Torna al checkpoint precedente
4. **Cambia approccio** (non continuare nello stesso modo)

**Razionale**: La "contaminazione di contesto" peggiora gli errori. Ricominciare è più veloce.

### ⚠️ EMPIRICO - Regola dei 2 Tentativi

**Community pattern verificato**:
- Se lo stesso approccio fallisce 2 volte nello stesso thread → `/rewind` + nuovo approccio
- Se continui un terzo tentativo, Claude inizia a confondersi
- **Non è fallimento** — è gestione consapevole del context

---

## 4.2 TDD AS FIRST-CLASS WORKFLOW

### 🎯 NEW: TDD Non è Opzionale, è una Skill

Mattpocock ha reso TDD un **primo-class workflow**, non un suggerimento:

#### Skill: `tdd` (Red-Green-Refactor Loop)
```
/tdd
→ Implementa una feature con ciclo TDD puro
→ Red: Scrivi un test che fallisce
→ Green: Scrivi il codice minimo per passare
→ Refactor: Migliora il codice mantenendo i test
→ Ripeti fino a feature completa
```

**Beneficio**: Features testate fin dall'inizio, no "test dopo"

**Workflow**:
1. Claude crea un test (fallisce)
2. Tu approvi il test
3. Claude implementa minimalista (passa il test)
4. Claude refactor elegante
5. Ripete fino a feature completa

#### Skill: `triage-issue` (Bug Investigation + Fix)
```
/triage-issue
→ Investigare a bug esplorando la codebase
→ Identificare la root cause
→ File GitHub issue con TDD-based fix plan
→ Implementazione ready-to-code
```

**Workflow**:
1. Claude esplora il codebase
2. Identifica il bug
3. Crea un test che riproduce il bug
4. Propone un fix TDD-based
5. File issue con tutti i dettagli

---

## 4.3 Code Architecture & Improvement

### Skill: `improve-codebase-architecture`
```
→ Analizza il codebase
→ Legge CONTEXT.md per domain knowledge
→ Legge docs/adr/ per decisioni architetturali passate
→ Suggerisce miglioramenti di architettura
→ Propone refactor con piani
```

**Key**: Usa il dominio (ubiquitous language) per suggerire miglioramenti

---

# PARTE 5: AUTOMAZIONE & ISOLAMENTO

## 5.1 Hooks - Automazione Deterministica 100%

### ✅ VERO - Hooks vs CLAUDE.md

| Tipo | Compliance | Use Case |
|------|-----------|----------|
| **CLAUDE.md** | ~80% | Guidance advisory |
| **Hooks** | 100% | Azioni che accadono SEMPRE |

### Hook Events Disponibili

```json
{
  "hooks": {
    "PreToolUse": "Prima di ogni tool execution",
    "PostToolUse": "Dopo ogni tool execution",
    "UserPromptSubmit": "Quando utente invia prompt",
    "Notification": "Notifiche custom",
    "Stop": "Quando Claude termina",
    "SubagentStart": "Inizio subagent",
    "SubagentStop": "Fine subagent",
    "SessionStart": "Inizio sessione",
    "SessionEnd": "Fine sessione",
    "PermissionRequest": "Richiesta di permesso"
  }
}
```

### Esempio 1: Auto-Format Code
```json
{
  "hooks": {
    "PostToolUse": {
      "command": "prettier --write {edited_files}",
      "description": "Auto-format dopo ogni edit"
    }
  }
}
```

**Effetto**: Claude scrive bene, hook formatta il 10% finale

### Esempio 2: Pre-commit Hooks con Husky
```bash
# .husky/pre-commit
prettier --write {staged_files}
eslint --fix {staged_files}
npm run type-check
npm run test
```

**Effetto**: 100% compliance — niente passa senza linting + testing + types

---

## 5.2 Pre-commit Guardrails (Safety First)

### Skill: `setup-pre-commit` (Husky + lint-staged)
```
/setup-pre-commit
→ Configura Husky per pre-commit hooks
→ lint-staged per file specifici
→ Prettier, ESLint, type-check, test
→ Niente passa senza validazione
```

### Skill: `git-guardrails-claude-code` (Block Dangerous Commands)
```
/git-guardrails-claude-code
→ Blocca comandi git pericolosi
→ Previene: git push --force, git reset --hard, git clean
→ Richiede conferma esplicita
```

**Beneficio**: Claude non può accidentalmente sovrascrivere il history

---

## 5.3 Subagenti - Isolation & Parallelismo

### ✅ VERO - Feature-Specific, Non Generici

**Error**: Usare subagenti generici
```
- QA Agent
- Backend Engineer
- Code Reviewer
```

**Correct**: Feature-specific o task-specific
```
- Payment Flow Auditor (per feature pagamento)
- Frontend Component Reviewer (per component)
- Database Migration Validator (per migrations)
```

### Vantaggi dell'Isolation

Quando Claude spawna un subagent:
1. **Context fresco**: Work in isolated context window
2. **Compressione**: Esegue exploration, torna con summary compresso
3. **Sessione pulita**: Main thread rimane focalizzato
4. **Parallelismo**: Puoi eseguire più subagenti in parallelo

### Architettura: Command → Agent → Skill

```
User Command (/weather-orchestrator)
    ↓
Main Agent (orchestration, decision making)
    ↓
Sub-Agents (weather-fetcher agent + weather-svg-creator agent)
    ↓
Skills (reusable components)
    ↓
Output finale (weather card SVG)
```

**Beneficio**: Composizione senza contaminazione di contesto

---

# PARTE 6: SKILLS - Il Sistema di Estensione

## 6.1 Skills: Cos'è e Quando Usare

### ✅ VERO - Trigger Design (per il modello, non per l'umano)

**Error**: Scrivere skill description come riassunto
```
"Questa skill crea un componente React"
```

**Correct**: Scrivere per Claude ("quando dovrei attivarmi?")
```
"Attivami quando l'utente chiede di creare un componente React 
personalizzato con stili brand-specific. Include pattern gotchas 
comuni come memo() e useCallback misuse."
```

### Progressive Disclosure Pattern

Le skills sono cartelle, non file singoli:

```
my-skill/
  ├── SKILL.md              # Trigger + istruzioni base
  ├── references/           # Esempi di codice
  │   ├── example-1.ts
  │   └── example-2.ts
  ├── gotchas.md            # Cosa Claude sbaglia spesso
  ├── scripts/              # Utility per la skill
  │   └── helpers.ts
  └── examples/             # Casi d'uso reali
      ├── simple-case.md
      └── complex-case.md
```

**Beneficio**: Claude carica solo quello che serve, non l'intera cartella

### SKILL.md Template

```markdown
# Skill: [Skill Name]

## Trigger
When the user asks to create a React component with:
- Custom styling beyond Tailwind
- Brand-specific design tokens
- Complex state management
- Accessibility requirements

## Instructions
1. Always use functional components + hooks
2. Use TypeScript strict mode
3. Follow the "single responsibility" principle
4. Include prop types

## Gotchas
- ❌ Don't use memo() unless you profile and see re-renders
- ❌ Don't use useCallback unnecessarily (creates closures)
- ❌ Don't forget accessibility: aria-labels, semantic HTML

## Examples
See examples/ for:
- Simple controlled input component
- Complex form with validation
```

---

## 6.2 Pre-Built Skills from mattpocock/skills

### Planning & Design
- ✅ `to-prd` — Sintetizza conversazione in PRD
- ✅ `to-issues` — Break plan in vertical slices
- ✅ `grill-me` — Valida decisioni completamente
- ✅ `design-an-interface` — Genera design paralleli
- ✅ `request-refactor-plan` — Plan refactor con tiny commits

### Development
- ✅ `tdd` — Red-green-refactor loop
- ✅ `triage-issue` — Bug investigation + fix plan
- ✅ `improve-codebase-architecture` — Architecture deepening
- ✅ `scaffold-exercises` — Generate exercise structures

### Automation
- ✅ `setup-pre-commit` — Husky + lint-staged
- ✅ `git-guardrails-claude-code` — Block dangerous git commands

### Knowledge Management
- ✅ `ubiquitous-language` — Extract DDD glossary
- ✅ `obsidian-vault` — Manage Obsidian notes
- ✅ `write-a-skill` — Create new skills

### Utility
- ✅ `edit-article` — Improve articles
- ✅ `migrate-to-shoehorn` — Test assertion migration

---

# PARTE 7: KNOWLEDGE MANAGEMENT (NEW)

## 7.1 Domain-Driven Design Integration

### Skill: `ubiquitous-language` (Extract Glossary)

```
/ubiquitous-language
→ Estrae un glossario DDD da una conversazione
→ Organizza per concetto
→ Crea CONTEXT.md standardizzato
```

**Esempio Output**:
```markdown
## Ubiquitous Language

### Core Concepts
- **Order**: A customer's request for products
  - Status: Pending → Paid → Shipped → Delivered
  - Invariant: Can't be modified after Shipped
  
- **LineItem**: Individual product in an order
  - Must have: product_id, quantity, price
  - Derived: subtotal = quantity × price

- **Fulfillment**: Process of shipping an order
  - Triggered by: Payment received
  - Completes: When carrier marks as delivered

### Business Rules
- Orders > $100 get free shipping
- LineItems > 100 units trigger bulk discount (20%)
- Refunds allowed within 30 days of delivery
```

**Beneficio**: Claude capisce il linguaggio del dominio, non solo il codice

### Architecture Decision Records (ADRs)

**Struttura docs/adr/**:
```
docs/adr/
  ├── ADR-001-database-choice.md
  │   ├── Decision: PostgreSQL (not MongoDB)
  │   ├── Rationale: ACID compliance, JSON support
  │   ├── Consequences: Need migrations, no auto-scaling
  │   └── Alternatives: MongoDB, Firebase
  │
  ├── ADR-002-state-management.md
  │   ├── Decision: Zustand (not Redux)
  │   ├── Rationale: Smaller bundle, simpler API
  │   └── Alternatives: Redux, Recoil, MobX
  │
  └── ADR-003-api-design.md
      ├── Decision: Vertical slices (not horizontal layers)
      └── Rationale: Features ship faster
```

**Beneficio**: Quando Claude propone miglioramenti, capisce perché le decisioni passate sono state prese

### Skill: `improve-codebase-architecture`

Usa sia CONTEXT.md che docs/adr/ per informare i suggerimenti:

```
/improve-codebase-architecture
→ Legge CONTEXT.md (ubiquitous language)
→ Legge docs/adr/ (perché)
→ Suggerisce miglioramenti
→ Allineati con le decisioni passate
```

---

## 7.2 Note Management: Obsidian Integration

### Skill: `obsidian-vault` (Manage Notes)

```
/obsidian-vault
→ Search, create, manage notes
→ Support for wikilinks [[internal-link]]
→ Auto-index notes
```

**Workflow**:
1. Crea note durante il planning
2. Collega con wikilinks
3. Claude mantiene l'indice
4. Puoi cercare per concetto

---

# PARTE 8: COMPLETE WORKFLOW (Research → Ship)

## 8.1 Full Workflow: Research → Plan → Execute → Review → Ship

### Fase 1: Research & Clarification
```
Human:
> Voglio aggiungere un sistema di pagamento con Stripe

Claude:
> (automatically asks clarifying questions)
> - Sono su Web o Mobile?
> - Single payment o subscription?
> - Refunds supportate?
> - Multi-currency?
```

### Fase 2: Plan & Validation
```
Human:
> Ecco il contesto, fami un piano

Claude (Plan Mode with /grill-me):
> Ecco il piano:
> 1. Setup Stripe API
> 2. Create Payment component
> 3. Handle success/error
> (pone domande fino a completezza)
```

### Fase 3: Create PRD & Issues
```
Human:
> Converte il piano in issues

Claude:
> /to-prd → Crea PRD come issue
> /to-issues → Break in vertical slices
> (ogni issue è independently grabbable)
```

### Fase 4: Execute with TDD
```
Human:
> Implementa il pagamento

Claude:
> /tdd
> - Red: Test payment success scenario
> - Green: Minimal Stripe integration
> - Refactor: Extract payment logic
> - Repeat per ogni scenario
```

### Fase 5: Review & Improve
```
Human:
> Fai self-review

Claude:
> /improve-codebase-architecture
> (Check if aligns with CONTEXT.md + ADRs)
> (Suggest refactors if needed)
```

### Fase 6: Ship
```
Human:
> Ready to commit

Claude:
> - Runs tests (pre-commit hook)
> - Git push (guardrails prevent --force)
> - PR created with ticket number
```

---

# PARTE 9: PROMPTING PATTERNS

## 9.1 Come Dar Feedback a Claude

### Pattern 1: Challenge Claude
```
"Grill me on these changes and don't make a PR until I pass your test."
→ Claude runs tests, fixes bugs, validates completeness
```

### Pattern 2: After Mediocre Fix
```
"Knowing everything you know now, scrap this and implement 
the elegant solution."
→ Claude reimplements with full context
```

### Pattern 3: Simple Request
```
"Fix" 
→ Don't micromanage. Claude knows the context.
```

### Pattern 4: Context Reset
```
"/clear"
→ Quando sei bloccato 2+ volte nello stesso thread
→ Ricomincia fresco con nuovo approccio
```

---

# PARTE 10: QUICK START CHECKLIST

## Week 1: Setup Foundation
- [ ] Create CLAUDE.md (< 200 righe)
  - [ ] Comandi bash essenziali
  - [ ] Code style rules
  - [ ] Key architecture
  - [ ] Critical rules
- [ ] Create CONTEXT.md (domain knowledge)
  - [ ] Ubiquitous language
  - [ ] Business rules
  - [ ] Key definitions
- [ ] Create docs/adr/ directory
  - [ ] ADR-001: Database choice
  - [ ] ADR-002: Architecture decision
- [ ] Install pre-commit hooks
  ```bash
  npm install husky lint-staged prettier eslint --save-dev
  npx husky install
  ```

## Week 2: Learn Planning
- [ ] Try Plan Mode (Shift+Tab x2)
  - [ ] Simple feature first
  - [ ] Approve plan before coding
- [ ] Try /grill-me for validation
- [ ] Try /to-prd for specification
- [ ] Try /to-issues for task breakdown

## Week 3: Setup Automation
- [ ] Configure PostToolUse hook for auto-format
- [ ] Add /setup-pre-commit for Husky
- [ ] Add /git-guardrails-claude-code for safety
- [ ] Monitor context with `/context`
- [ ] Use `/compact` at 50% usage

## Week 4: Advanced Usage
- [ ] Create first custom skill with write-a-skill
- [ ] Use /tdd for feature implementation
- [ ] Use /triage-issue for bugs
- [ ] Use /improve-codebase-architecture for refactors
- [ ] Extract ubiquitous-language for domain clarity

## Month 2: Scaling
- [ ] Parallel sub-agents for complex features
- [ ] ADR review before architecture changes
- [ ] Monthly CONTEXT.md/ubiquitous-language review
- [ ] Custom skills per domain

---

# PARTE 11: CONFRONTO TABELLARE - UFFICIALE vs COMMUNITY vs MATTPOCOCK

| Best Practice | Official Docs | shanraisshan/repo | mattpocock/skills | Status |
|---|---|---|---|---|
| **CLAUDE.md < 200 righe** | ✅ | ✅ | ✅ | Verificato |
| **CONTEXT.md + ADRs** | ⚠️ Implicit | ⚠️ Brief | ✅ Emphasized | Mattpocock specifico |
| **Plan mode per features** | ✅ | ✅ | ✅ | Verificato |
| **Shift+Tab x2 per plan** | ✅ | ✅ | ✅ | Verificato |
| **Planning come skills** | ❌ | ⚠️ Implicit | ✅ Explicit | Mattpocock innovation |
| **TDD come primo-class** | ⚠️ | ⚠️ | ✅ Emphasized | Mattpocock innovation |
| **Subagenti feature-specific** | ✅ | ✅ | ✅ | Verificato |
| **Hooks 100% deterministico** | ✅ | ✅ | ✅ | Verificato |
| **Pre-commit automation** | ⚠️ | ⚠️ | ✅ Emphasized | Mattpocock innovation |
| **Ubiquitous language** | ❌ | ❌ | ✅ Emphasized | Mattpocock innovation |
| **ADR integration** | ❌ | ❌ | ✅ Emphasized | Mattpocock innovation |
| **Skill authoring skill** | ❌ | ⚠️ | ✅ (write-a-skill) | Mattpocock innovation |
| **Git guardrails** | ❌ | ❌ | ✅ | Mattpocock innovation |
| **Rewind/Compact** | ✅ | ✅ | Implicit | Community pattern |
| **Knowledge management** | ❌ | ❌ | ✅ (obsidian-vault) | Mattpocock innovation |

---

# PARTE 12: COSA NON FARE (Anti-patterns)

## ❌ ANTI-PATTERNS VERIFICATI

❌ **Non** mettere 1000+ righe in CLAUDE.md  
→ Causa token waste e riduce relevanza

❌ **Non** cercare di fissare lo stesso errore 3+ volte nello stesso thread  
→ Context contamination peggiora ogni tentativo

❌ **Non** usare subagenti generici ("QA Agent")  
→ Perde i benefici di isolation

❌ **Non** aspettare il 90% context usage prima di compattare  
→ Performance degrada severamente dopo 70%

❌ **Non** ignorare i gotchas nella skill documentation  
→ Claude sbaglia negli stessi posti ogni volta

❌ **Non** scrivere CLAUDE.md come un manuale completo  
→ Solo essentials che Claude non può dedurre

❌ **Non** usare Planning Mode per bug semplici  
→ Overkill per fix under 30 min

❌ **Non** mixare TDD con implementation casuali  
→ Scegli TDD per feature, speedrun per bug fix

❌ **Non** ignorare CONTEXT.md quando proponi refactors  
→ Perderai il contexto del dominio

❌ **Non** fare hook deterministiche senza test  
→ Creerai biolocks accidentali

---

# PARTE 13: TROUBLESHOOTING

## Sintomo: Claude va off-track

**Diagnosi**: Context contamination  
**Soluzione**:
1. Premi Esc Esc (o `/rewind`)
2. Non continuare nello stesso approccio
3. Cambia strategia completamente

## Sintomo: Performance degrada

**Diagnosi**: Context window troppo pieno  
**Soluzione**:
1. Controlla `/context`
2. Se > 50%, esegui `/compact`
3. Se > 70%, considera `/clear` per reset

## Sintomo: Feature prende troppo tempo

**Diagnosi**: Planning insufficiente  
**Soluzione**:
1. Usa `/grill-me` per validare il piano
2. Usa `/to-issues` per break in smaller tasks
3. Implementa con `/tdd` per clarity

## Sintomo: Hook non si attiva

**Diagnosi**: Hook syntax o timing issue  
**Soluzione**:
1. Controlla `.claude/settings.json`
2. Valida JSON (no trailing commas)
3. Testa con simple hook prima

## Sintomo: Skill non viene riconosciuta

**Diagnosi**: Trigger description troppo vaga  
**Soluzione**:
1. Aggiorna SKILL.md con trigger specifico
2. Includi esempi di quando attivarsi
3. Includi un gotcha comune

---

# PARTE 14: RISORSE UFFICIALI & COMMUNITY

## Docs Ufficiali Anthropic
- **Best Practices**: https://code.claude.com/docs/en/best-practices
- **Docs Map**: https://docs.anthropic.com/en/docs/claude-code/
- **Common Workflows**: https://code.claude.com/docs/en/common-workflows
- **Product Guide**: https://code.claude.com/docs/en/

## Community Resources

### Repository Principals
1. **shanraisshan/claude-code-best-practice** (19.7k ⭐)
   - URL: https://github.com/shanraisshan/claude-code-best-practice
   - 84+ tips, patterns, hooks, skills
   - Foundational community reference

2. **mattpocock/skills** (23.1k ⭐)
   - URL: https://github.com/mattpocock/skills
   - 20+ production skills
   - DDD + knowledge management focus
   - "Agent Skills for real engineers"

3. **Claude Code Hooks** (by shanraisshan)
   - https://github.com/shanraisshan/claude-code-hooks
   - Pre-built hook configurations

4. **Codex CLI** (by shanraisshan)
   - https://github.com/shanraisshan/codex-cli-best-practice
   - CLI utilities for Claude Code

### Video & Podcasts (Boris Cherny, Head of Claude Code)
- **Building Claude Code** - The Pragmatic Engineer (Mar 04, 2026)
- **Head of Claude Code: What Happens After Coding is Solved** - Lenny's Podcast
- **Inside Claude Code With Its Creator** - Y Combinator

### Courses & Tutorials
- mattpocock's newsletter: https://www.aihero.dev/s/skills-newsletter (~60,000 devs)
- Official workshops on code.claude.com

---

# PARTE 15: IMPLEMENTATION MATRIX

## Implementazione Veloce per Ogni Caso

### Per un Individuo (Freelancer/Solo Dev)

**Setup rapido** (1 ora):
```
Week 1:
- CLAUDE.md (30 min) + CONTEXT.md (15 min)
- Pre-commit setup (15 min)

Week 2:
- Imparare Plan Mode (2-3 features)
- Try /grill-me su una decisione

Week 3:
- Aggiungere 3-4 skill rilevanti al tuo dominio
```

**Workflow quotidiano**:
```
Feature:
1. /grill-me → valida idea
2. /to-prd → spec rapida
3. /to-issues → task list
4. /tdd → implement
5. Ship
```

### Per un Team (3-10 persone)

**Setup rapido** (2-3 giorni):
```
Day 1:
- Estrai ubiquitous-language (/ubiquitous-language skill)
- Crea CONTEXT.md + CLAUDE.md condivisi
- Avvia docs/adr/ structure

Day 2:
- Setup pre-commit hooks (team standard)
- Setup git-guardrails
- Review template CLAUDE.md

Day 3:
- Training su Plan Mode
- Demo di skill specifiche
- Configurare skill custom per il team
```

**Workflow settimanale**:
```
Monday:
- Sprint planning con /grill-me + /to-issues

During Sprint:
- Feature con /tdd
- Bug triage con /triage-issue
- Refactor con /improve-codebase-architecture

Friday:
- Review dengan /grill-me
- Update CONTEXT.md/ubiquitous-language
- Capture decision in ADR
```

### Per una Codebase Esistente

**Migration plan** (2-4 settimane):

**Week 1**: Knowledge Extraction
```
- /ubiquitous-language → Extract from codebase + team
- Create CONTEXT.md
- Start docs/adr/ with retrospective decisions
```

**Week 2**: Baseline Automation
```
- /setup-pre-commit → Add linting/testing
- /git-guardrails-claude-code → Prevent accidents
- Create CLAUDE.md from team consensus
```

**Week 3-4**: Skill Development
```
- /write-a-skill → Create domain-specific skills
- /improve-codebase-architecture → Identify refactors
- Setup TDD workflow for new features
```

---

# PARTE 16: FINAL SUMMARY

## I Tre Pilastri (Recap)

### 1️⃣ Context Management
- CLAUDE.md + CONTEXT.md are your memory
- Monitor with `/context`
- Compact at 50% usage
- Rewind when contaminated

### 2️⃣ Planning Before Execution
- Use Shift+Tab x2 for Plan Mode
- Use /grill-me for validation
- Use /to-prd for specification
- Use /to-issues for task breakdown
- Math: 1% success without plan → 100% with plan

### 3️⃣ Automation & Isolation
- Skills for reusability
- Hooks for determinism
- Sub-agents for parallelism
- Knowledge management for context

## Difference Between Frustrated & Productive Users

❌ **Frustrated users**:
- Try to fix same error 5 times
- Don't plan before coding
- Ignore context management
- Treat Claude Code like vanilla Claude

✅ **Productive users**:
- Know when to rewind
- Plan 80% of the time (for complex features)
- Compact proactively
- Use skills, hooks, and sub-agents

## The Repository Difference

**shanraisshan (19.7k ⭐)**: Foundational best practices  
**mattpocock (23.1k ⭐)**: Production skills + DDD patterns

**This document**: Integrated unified reference combining both

---

# PARTE 17: ATTRIBUTION & SOURCES

## Verified Sources

### Official Anthropic
- Docs: docs.anthropic.com
- Claude Code: code.claude.com
- Boris Cherny interviews & talks

### Community Leading Projects
- **shanraisshan**: claude-code-best-practice (19.7k ⭐)
- **mattpocock**: skills (23.1k ⭐)

### Verification Methodology
- Cross-referenced between official docs
- Validated through community adoption
- Tested through production workflows
- Documented gaps and innovations

---

**Documento Finale Compilato**: 29 aprile 2026  
**Versione**: 2.0 - Definitiva  
**Status**: Pronto per produzione  
**Prossimo aggiornamento**: Quando emergeranno nuovi pattern verificati

---

## Come Usare Questo Documento

1. **Onboarding**: Leggi Parte 1-3 (fondamenti)
2. **Setup**: Segui checklist in Parte 10
3. **Workflow**: Usa Parte 8 come reference quotidiana
4. **Troubleshooting**: Vai a Parte 13 quando bloccato
5. **Scaling**: Parte 15 per team/codebase esistente

**Bookmark this document.** È il tuo reference definitivo per Claude Code.
EOF
