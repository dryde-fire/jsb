# Hybrid Agentic Architecture Guide
**Versione**: 1.0 — Framework Radicale  
**Data**: 1 maggio 2026  
**Natura**: Metodo di architettura universale — indipendente da implementazione specifica  
**Fonti sintetizzate**:
- Claude Code Best Practices v2.0 (shanraisshan + mattpocock)
- OpenAI Symphony Specification (openai/symphony)

---

> **Nota di onestà archittetturale**: Symphony è un engineering preview (Apache 2.0, solo Linear + Codex come runtime ufficiali). Questo documento ne estrae i **principi** e li rende applicabili con qualsiasi stack. Dove Symphony è limitato, viene indicato esplicitamente. Le parti verificate come principi universali sono marcate ✅; le parti che richiedono adattamento sono marcate ⚠️.

---

## 🎯 COME LEGGERE QUESTO DOCUMENTO

| Marker | Significato |
|--------|-------------|
| ✅ **VERIFICATO** | Principio documentato e operativo in entrambi i framework |
| ⚠️ **EMPIRICO** | Validato dalla community o in preview, richiede adattamento |
| 🚨 **CRITICO** | Ignorare questo causa fallimento architetturale |
| 🔄 **COMPLEMENTARE** | I due framework si integrano su questo punto |
| ❌ **ANTI-PATTERN** | Collisione tra framework — da evitare |

---

<architecture_vision>

# PARTE 1: VISION — La Sinergia Symphony-Claude

## 1.1 Il Problema che Risolve questa Architettura

Il fallimento più comune nell'adozione degli AI agent non è tecnico — è **architetturale**. I team commettono uno di due errori opposti:

**Errore A — Micro-gestione**: L'umano supervisiona ogni sessione di Claude Code, ogni prompt, ogni output. L'AI è uno strumento, non un membro del team. Risultato: bottleneck umano, zero scalabilità.

**Errore B — Delega cieca**: Un orchestratore lancia agenti su task ambigui senza struttura di context, senza guardrails, senza proof of work. Risultato: output inaffidabili, debug impossibile, rollback frequenti.

**La sinergia Symphony-Claude risolve entrambi** definendo una separazione netta delle responsabilità tra due layer:

---

## 1.2 I Due Layer — Macro-Context e Micro-Context

```
┌─────────────────────────────────────────────────────────────┐
│                   SYMPHONY LAYER                            │
│               [ MACRO-CONTEXT MANAGER ]                     │
│                                                             │
│  • Obiettivi di business a lungo termine                    │
│  • Stato globale del progetto                               │
│  • Routing dei task agli agenti specializzati               │
│  • Proof of work & validazione output                       │
│  • Fault tolerance e retry policy                           │
│  • Decoupling: task ≠ sessione ≠ pull request               │
└─────────────────────────┬───────────────────────────────────┘
                          │  Spawna agenti con context isolato
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 CLAUDE CODE LAYER                           │
│               [ MICRO-CONTEXT EXECUTOR ]                    │
│                                                             │
│  • Files e stato locale del codebase                        │
│  • Plan Mode per decisioni a 20+ fork point                 │
│  • Skills come unità di esecuzione riusabili                │
│  • Hooks per automazione deterministica 100%                │
│  • Context window management (compact al 50%)               │
│  • TDD come proof of correctness                            │
└─────────────────────────────────────────────────────────────┘
```

### 🚨 CRITICO: La Regola della Separazione

> **Symphony non scrive codice. Claude Code non gestisce stato globale.**

Ogni violazione di questa regola è un anti-pattern architetturale. Symphony conosce *cosa* deve essere fatto e *quando*. Claude Code conosce *come* farlo nel contesto locale del codebase. Questi due layer comunicano esclusivamente tramite:

1. **Input**: Task description + context snapshot (ADRs + CONTEXT.md estratti)
2. **Output**: Proof of work (test passing, CI status, PR diff)

---

## 1.3 La Matematica della Sinergia

**Claude Code da solo** (senza orchestrazione):
- Piano approvato → successo vicino a 100% per task singolo
- Ma: chi pianifica i task? Chi li sequenzia? Chi gestisce dipendenze tra task?

**Symphony da solo** (senza execution layer strutturato):
- Orchestrazione robusta, ma agenti generici producono output inaffidabili
- Senza Skills e Hooks, ogni agente reinventa la ruota

**Combinati**:
```
Symphony risolve: sequencing, parallelism, state, fault tolerance
Claude Code risolve: execution quality, context management, determinism

Output: Sistema in cui gli umani gestiscono work items,
        non sessioni di codice
```

</architecture_vision>

---

<hybrid_workflow_integration>

# PARTE 2: WORKFLOW IBRIDO — Le 8 Fasi Orchestrate

## 2.1 Mappa delle Responsabilità per Fase

| Fase | Owner | Tool | Output |
|------|-------|------|--------|
| 1. Research | Symphony Orchestrator | Issue tracker polling | Task enriched con context |
| 2. Clarification | Claude Code (Plan Mode) | `/grill-me` skill | Decision tree completato |
| 3. Specification | Claude Code | `/to-prd` skill | PRD formale → GitHub Issue |
| 4. Task Breakdown | Symphony | `/to-issues` skill | DAG di subtask con dipendenze |
| 5. Execution | Claude Code (sub-agents) | `/tdd` skill | Feature implementata con test |
| 6. Guardrails | Hooks + Pre-commit | Husky/lint-staged | Zero commit non validi |
| 7. Review | Symphony | Proof of work collector | CI status + PR diff + walkthrough |
| 8. Ship | Symphony | Auto-merge policy | PR approvata e lanciata |

---

## 2.2 Fase 1 — Research: Symphony come Radar

```
SYMPHONY ORCHESTRATOR
        │
        ▼ polling continuo
┌───────────────────┐
│   Issue Tracker   │  ← Linear / ClickUp / Jira / GitHub Issues
│   (stato: Open)   │
└─────────┬─────────┘
          │
          ▼ per ogni issue eleggibile
┌───────────────────────────────────┐
│   Context Snapshot Preparation    │
│                                   │
│   Carica automaticamente:         │
│   • CONTEXT.md (dominio)          │
│   • ADR rilevanti (decisioni)     │
│   • CLAUDE.md (regole build)      │
│   • Issue history (se presente)   │
└─────────┬─────────────────────────┘
          │
          ▼
   Workspace isolato creato
   per questo task specifico
```

**🚨 CRITICO**: Symphony non passa l'intero codebase all'agente. Passa un **context snapshot curato**. Questo è il principio chiave del "harness engineering": costruire il contesto giusto, non il contesto completo.

---

## 2.3 Fase 2-3 — Planning: Claude Code come Archivista delle Decisioni

```
Claude Code Agent (Plan Mode attivo)
        │
        ▼
┌─────────────────────────────────────────┐
│         CICLO DI VALIDAZIONE            │
│                                         │
│  1. Legge: CONTEXT.md + ADRs forniti    │
│  2. Entra in Plan Mode (Shift+Tab x2)   │
│  3. /grill-me → intervista relentless   │
│     su ogni edge case del task          │
│  4. Ogni branch decisionale viene       │
│     forzato a risoluzione               │
│  5. /to-prd → sintesi in spec formale   │
│                                         │
│  OUTPUT: PRD con zero ambiguità         │
└─────────────────────────────────────────┘
        │
        ▼ trasmette a Symphony
   PRD approvato come Issue strutturato
```

**✅ Principio verificato**: Il planning collassa 20 decision point ambigui in un piano dove ogni scelta è già stata fatta. 0.8^20 ≈ 1% vs ~100% con piano approvato.

**🔄 Integrazione**: Symphony riceve il PRD come output strutturato, non come testo libero. Il formato deve essere machine-readable per permettere l'auto-generazione del DAG di task.

---

## 2.4 Fase 4 — Task Breakdown: Symphony come DAG Engine

```
Symphony riceve PRD strutturato
        │
        ▼
┌─────────────────────────────────────────┐
│           DAG CONSTRUCTION              │
│                                         │
│  /to-issues skill applicata al PRD:     │
│                                         │
│  Task A ──────────────────→ Task D      │
│  Task B ──┐                    ↑        │
│           └──→ Task C ─────────┘        │
│  Task E (parallelo a A,B,C)             │
│                                         │
│  Regola: ogni task è indipendente       │
│  e implementabile senza dipendenze      │
│  non dichiarate esplicitamente          │
└─────────────────────────────────────────┘
        │
        ▼
Symphony spawna agenti solo sui task
senza blockers attivi → parallelismo naturale
```

**⚠️ EMPIRICO**: Il DAG auto-generato da `/to-issues` richiede validazione umana prima dello spawn. Symphony non dovrebbe procedere automaticamente su DAG complessi senza un checkpoint di review.

---

## 2.5 Fase 5 — Execution: TDD come Contratto di Qualità

```
Per ogni task nel DAG (agente isolato):

┌─────────────────────────────────────────┐
│         /tdd SKILL LOOP                 │
│                                         │
│  RED:     Scrivi test che fallisce      │
│           → checkpoint umano (opz.)     │
│                                         │
│  GREEN:   Implementa il minimo          │
│           necessario per passare        │
│                                         │
│  REFACTOR: Migliora mantenendo          │
│            i test verdi                 │
│                                         │
│  REPEAT:  Per ogni scenario del task    │
│                                         │
│  PROOF:   Test suite completa passing   │
└─────────────────────────────────────────┘
        │
        ▼ trasmette a Symphony
   Proof of work: test log + coverage + PR diff
```

**✅ Principio verificato**: Il test è il contratto. Symphony non accetta un task come completato senza proof of work verificabile — non sulla parola dell'agente.

---

## 2.6 Fase 6 — Guardrails: Husky come Firewall Deterministico

```
HOOKS LAYER (100% deterministico — non byppassabile)

PreToolUse Hook:
  → Blocca git push --force
  → Blocca git reset --hard
  → Blocca comandi destructivi

PostToolUse Hook:
  → prettier --write {edited_files}
  → eslint --fix {staged_files}

Pre-commit Hook (Husky):
  → TypeScript type-check
  → Test suite (subset fast)
  → Lint check

Pre-push Hook:
  → Full test suite
  → Coverage threshold check
  → Dependency audit
```

**🚨 CRITICO**: Hooks ≠ CLAUDE.md. CLAUDE.md ha ~80% compliance (advisory). Gli Hooks hanno 100% compliance (deterministici). Qualsiasi regola che deve essere rispettata senza eccezione va in Hook, non in CLAUDE.md.

**🔄 Integrazione Symphony**: Symphony considera una sessione Claude Code come "trusted" solo se i pre-commit hook passano. Il proof of work include sempre il CI status, non solo l'output dell'agente.

---

## 2.7 Fase 7-8 — Review & Ship: Symphony come Quality Gate

```
Symphony raccoglie proof of work:
  ├── CI status (verde/rosso)
  ├── Test coverage delta
  ├── PR diff review (automated)
  ├── Complexity analysis
  └── Walkthrough video/log (opzionale)

        │
        ▼ decision point
┌───────────────────────────────────┐
│   ACCETTATO: merge automatico     │  ← se tutti i gate passano
│   REVIEW: notifica umano          │  ← se gate ambigui
│   RIFIUTATO: retry con context    │  ← se gate falliscono
└───────────────────────────────────┘
```

</hybrid_workflow_integration>

---

<skill_orchestration_matrix>

# PARTE 3: SKILL ORCHESTRATION MATRIX

## 3.1 Come Symphony Triggera le Claude Code Skills

La regola fondamentale: **Symphony riconosce pattern negli issue, non legge codice**. Il trigger avviene sulla base di label, titolo, e metadati del task — non sul contenuto tecnico.

---

## 3.2 Matrice Completa

| Trigger Symphony | Tipo Issue | Skill Claude Attivata | Skill di Validazione | Output Atteso |
|------------------|------------|-----------------------|---------------------|---------------|
| Label: `bug` + assegnato | Bug report | `/triage-issue` | `/tdd` (test che riproduce) | Root cause + fix con test passing |
| Label: `feature` + milestone | Nuova funzionalità | `/grill-me` → `/to-prd` → `/tdd` | `/setup-pre-commit` | PRD + implementazione TDD |
| Label: `refactor` + no deadline | Refactor tecnico | `/request-refactor-plan` | `/tdd` | Piano a tiny commits + esecuzione |
| Label: `design` + multiple approaches | UI/UX decision | `/design-an-interface` | Review umano | 3-4 design paralleli da confrontare |
| Label: `architecture` + ADR-needed | Decisione architetturale | `/grill-me` + ADR creation | `/improve-codebase-architecture` | ADR formale + refactor proposal |
| Label: `onboarding` + new-skill | Nuovo pattern ripetitivo | `/write-a-skill` | Skill review umano | Skill production-ready |
| Label: `debt` + critical | Technical debt critico | `/triage-issue` + `/improve-codebase-architecture` | `/tdd` | Refactor sistematico con test |
| Label: `knowledge` | Documentazione dominio | `/ubiquitous-language` | Review umano | CONTEXT.md aggiornato |

---

## 3.3 Sequenze di Skill (Flow Chains)

### Bug Flow (più comune)
```
Symphony detecta: issue con label "bug"
        │
        ▼
Claude Agent 1: /triage-issue
  → esplora codebase
  → identifica root cause
  → crea test che riproduce il bug
        │
        ▼ (se root cause chiara)
Claude Agent 2: /tdd
  → RED: test che fallisce (già creato)
  → GREEN: fix minimo
  → REFACTOR: eleganza
        │
        ▼
Symphony collects: test log + PR diff
  → CI passa → merge automatico
  → CI fallisce → notify umano
```

### Feature Flow (standard)
```
Symphony detecta: issue con label "feature"
        │
        ▼
Claude Agent 1: /grill-me
  → valida ogni edge case
  → forza risoluzione di ogni branch
        │
        ▼
Claude Agent 1: /to-prd
  → sintetizza in spec machine-readable
        │
        ▼
Symphony: /to-issues
  → costruisce DAG di subtask
  → spawna agenti paralleli per task sbloccati
        │
        ▼ (per ogni subtask)
Claude Agent N: /tdd
  → implementa con ciclo RED-GREEN-REFACTOR
        │
        ▼
Symphony merge: quando tutti i subtask passano
```

### Architecture Flow (alto rischio)
```
Symphony detecta: issue con label "architecture"
        │
        ▼ CHECKPOINT UMANO OBBLIGATORIO
        │  (Symphony non auto-spawna agenti per decisioni architetturali)
        ▼
Claude Agent 1: /grill-me
  → intervista su impatto, alternative, rischi
        │
        ▼
ADR Creation:
  → docs/adr/ADR-XXX-[decision].md
  → Status: Proposed → Review umano → Accepted/Rejected
        │
        ▼ (solo se ADR Accepted)
Claude Agent 2: /improve-codebase-architecture
  → legge ADR + CONTEXT.md
  → propone refactor allineato alle decisioni storiche
        │
        ▼
Claude Agent 3: /request-refactor-plan
  → tiny commits, dipendenze esplicite
  → Symphony esegue come DAG
```

---

## 3.4 Regole di Priorità tra Skills

```
PRIORITÀ 1 (Safety First):
  /setup-pre-commit e /git-guardrails sempre installati PRIMA di ogni altro flow.
  Nessun agente può operare su un repo senza guardrails attivi.

PRIORITÀ 2 (Knowledge First):
  CONTEXT.md e docs/adr/ devono esistere prima di spawna agenti.
  Symphony non avvia workflow su repo senza knowledge base strutturata.

PRIORITÀ 3 (Plan Before Execute):
  /grill-me SEMPRE prima di /tdd per feature.
  Mai saltare la fase di validazione delle decisioni.

PRIORITÀ 4 (Isolation by Default):
  Ogni agente riceve un context snapshot, non l'intero repo.
  Symphony costruisce il context prima dello spawn, non dopo.
```

</skill_orchestration_matrix>

---

<context_management_rules>

# PARTE 4: REGOLE DI CONTEXT MANAGEMENT

## 4.1 Il Problema del Context a Due Layer

In un'architettura ibrida esistono **due tipi di context** con cicli di vita completamente diversi:

| Tipo | Owner | Ciclo di vita | Strumento di gestione |
|------|-------|---------------|----------------------|
| **Micro-Context** | Claude Code agent | Sessione singola (ore) | `/compact`, `/clear`, `/rewind` |
| **Macro-Context** | Symphony orchestrator | Progetto intero (settimane/mesi) | ADRs, CONTEXT.md, Issue tracker state |

**🚨 CRITICO**: Non confondere i due. Un agente Claude Code non dovrebbe mai essere la fonte di verità per stato globale del progetto. E Symphony non dovrebbe mai gestire il context window di una singola sessione.

---

## 4.2 Regole per il Micro-Context (Claude Code)

### Regola 1 — Compact al 50%, non al 90%
```
Monitoraggio obbligatorio:
  /context → controlla utilizzo attuale

Soglie di intervento:
  < 50%: continua normalmente
  50-70%: esegui /compact manualmente
  > 70%: considera /clear + nuovo context snapshot da Symphony
  > 85%: STOP — "dumb zone" — l'agente inizia a ignorare le istruzioni di sistema
```

### Regola 2 — Rewind prima di Fix
```
Se stesso approccio fallisce 2 volte:
  → NON continuare un terzo tentativo nello stesso thread
  → Esc Esc (o /rewind) al checkpoint precedente
  → Cambia approccio radicalmente
  → Se anche il nuovo approccio fallisce: notifica Symphony → task torna in queue
```

### Regola 3 — Isolamento del Context per Subagente
```
Ogni subagente spawna con:
  ✅ CLAUDE.md (regole di build)
  ✅ CONTEXT.md (dominio)
  ✅ ADRs rilevanti per il task (non tutti)
  ✅ Task description specifica
  ❌ NON: conversazioni di sessioni precedenti
  ❌ NON: output di altri agenti paralleli
  ❌ NON: l'intero history del progetto
```

---

## 4.3 Regole per il Macro-Context (Symphony)

### Regola 4 — ADR Propagation Protocol

Gli ADR sono il meccanismo principale con cui le decisioni passate informano gli agenti futuri. Il protocollo:

```
QUANDO viene presa una decisione architetturale:
  1. Crea ADR in docs/adr/ADR-XXX-[decisione].md
  2. Aggiorna CONTEXT.md con riferimento all'ADR
  3. Symphony indicizza il nuovo ADR nella sua knowledge base
  4. Ogni futuro spawn include gli ADR rilevanti per categoria

FORMATO ADR (machine-readable):
---
id: ADR-001
status: Accepted  # Proposed | Accepted | Deprecated | Superseded
date: 2026-05-01
decision: [una riga, imperativo]
categories: [database, api, frontend]  # per filtering Symphony
---
```

**🔄 Integrazione**: Symphony filtra gli ADR per `categories` quando costruisce il context snapshot. Un agente che lavora su frontend non riceve gli ADR di database (spreco di context).

### Regola 5 — Symphony State Reset vs /compact

| Situazione | Azione corretta |
|-----------|----------------|
| Agente ha context window piena (> 70%) | Claude Code `/compact` — non interrompere il task |
| Task completato, nuovo task inizia | Symphony spawna nuovo agente con context fresco — non usare /compact |
| Agente bloccato 2+ volte sullo stesso approach | Claude Code `/rewind` → se ancora bloccato → Symphony riassegna il task a un nuovo agente |
| Feature completata, nuova feature inizia | Symphony chiude workspace, apre nuovo workspace isolato |
| Decisione architetturale cambia | Symphony propaga nuovo ADR a tutti i workspace attivi |

### Regola 6 — Context Snapshot Versioning

```
Prima di ogni spawn, Symphony costruisce un context snapshot versionato:

snapshot-{task-id}-{timestamp}/
  ├── CLAUDE.md          ← dalla root del repo
  ├── CONTEXT.md         ← dalla root del repo
  ├── adr/               ← solo ADR con categories rilevanti
  │   ├── ADR-002.md
  │   └── ADR-003.md
  ├── task.md            ← task description + PRD
  └── manifest.json      ← metadata del snapshot
```

Il snapshot è immutabile per la durata del task. Se cambiano ADRs o CONTEXT.md durante il task, Symphony crea un nuovo snapshot e decide se interrompere/riavviare l'agente corrente.

---

## 4.4 La Regola d'Oro del Context

> **Un agente non dovrebbe mai "scoprire" informazioni che avrebbero dovuto essere nel suo context snapshot iniziale.**

Se un agente interrompe il proprio lavoro per esplorare dominio, architettura, o decisioni storiche — è un segnale che Symphony ha costruito un context snapshot incompleto. Questa è una failure di Symphony, non di Claude Code.

</context_management_rules>

---

<anti_patterns>

# PARTE 5: ANTI-PATTERN — I Collision Points

## 5.1 Collision Point 1 — Doppio Planning (Ridondanza Critica)

**Descrizione**: Symphony fa planning a livello di DAG → Claude Code fa planning in Plan Mode → si creano due piani che possono divergere.

**Perché accade**: Symphony pianifica *sequencing* (quale task prima), Claude Code pianifica *implementation* (come implementare il task). Se i confini sono blurry, entrambi tentano di fare architectural planning.

**Anti-pattern**:
```
❌ SBAGLIATO:
Symphony: "Implementa autenticazione OAuth (step 1: database, step 2: API, step 3: frontend)"
Claude Agent: entra in Plan Mode e ridefinisce i step in modo diverso
→ CONFLITTO: quale piano è autoritativo?
```

**Pattern corretto**:
```
✅ CORRETTO:
Symphony: definisce SOLO i task e le dipendenze (cosa + ordine)
Claude Agent: definisce SOLO l'implementazione tecnica (come)

Regola: Se il PRD che Symphony fornisce è specifico sull'implementazione,
        Claude Code segue il PRD. Plan Mode serve per chiarire ambiguità,
        non per ridefinire l'architettura del task.
```

---

## 5.2 Collision Point 2 — Context Contamination Cross-Agent

**Descrizione**: Due agenti paralleli lavorano sullo stesso codebase e le loro modifiche si contaminano prima del merge.

**Perché accade**: Git branching non correttamente gestito, o agenti che leggono file modificati da altri agenti in corso d'opera.

**Anti-pattern**:
```
❌ SBAGLIATO:
Agent A (branch: feature/auth) modifica src/utils/crypto.ts
Agent B (branch: feature/payments) legge src/utils/crypto.ts 
→ Agent B costruisce su codice non ancora mergiato
→ merge conflict + regressioni
```

**Pattern corretto**:
```
✅ CORRETTO:
Symphony garantisce:
1. Ogni agente lavora su un branch isolato
2. I file condivisi sono marcati come "locked" durante le modifiche
3. Task con dipendenza su file condivisi vengono sequenzializzati
4. Il DAG include dipendenze a livello di file, non solo a livello logico
```

---

## 5.3 Collision Point 3 — Hook vs Symphony Retry (Loop Infinito)

**Descrizione**: Un agente Claude Code fallisce un pre-commit hook → Symphony interpreta il failure come "task non completato" → riavvia l'agente → l'agente ripete lo stesso errore → loop.

**Perché accade**: Symphony legge CI status, non distingue tra "fallimento di task" e "fallimento di hook di formattazione".

**Anti-pattern**:
```
❌ SBAGLIATO:
Agente: scrive codice con errore TypeScript
Hook: blocca il commit
Symphony: "task non completato" → riavvia agente
Agente (nuovo): stesso errore TypeScript (non ha capito il problema)
→ Loop infinito di retry
```

**Pattern corretto**:
```
✅ CORRETTO:
1. Gli agenti Claude Code devono leggere l'output degli hook
   e tentare auto-fix PRIMA di segnalare failure a Symphony
2. Symphony distingue tra:
   - "hook failure": l'agente ritenta con fix (max 2 volte)
   - "task logic failure": Symphony riassegna il task
3. Dopo 2 hook failure senza fix: Symphony notifica umano,
   non riavvia infinitamente
```

---

## 5.4 Collision Point 4 — CLAUDE.md vs Symphony WORKFLOW.md (Conflitto di Istruzioni)

**Descrizione**: CLAUDE.md contiene regole di progetto. Symphony ha un WORKFLOW.md con istruzioni per gli agenti. Se contengono istruzioni contraddittorie, l'agente è paralizzato.

**Pattern corretto**:
```
✅ GERARCHIA DELLE ISTRUZIONI (ordine di priorità):

1. Hooks (deterministici, non bypassabili)
2. Pre-commit configuration (deterministica)
3. Symphony WORKFLOW.md (orchestration policy)
4. CLAUDE.md (project guidance, ~80% compliance)
5. CONTEXT.md + ADRs (domain knowledge, informativo)

Regola: se c'è conflitto tra livelli, vince sempre il livello superiore.
         CLAUDE.md non può contradire Hooks. WORKFLOW.md non può
         contradire Hooks o Pre-commit.
```

---

## 5.5 Collision Point 5 — Granularità del Task Sbagliata

**Descrizione**: Symphony assegna task troppo grandi agli agenti → il context window si riempie prima che il task sia completato → agente degrada e produce output parziali.

**Soglie operative**:
```
TASK SIZE per agente Claude Code:

✅ OTTIMALE: 2-4 ore di lavoro umano equivalente
   → ~1000-3000 righe di codice modificate
   → Context window: rimane sotto 50% a fine task

⚠️ LIMITE: 4-8 ore di lavoro umano equivalente
   → Richiede /compact durante l'esecuzione
   → Symphony monitora context usage dell'agente

❌ TROPPO GRANDE: > 8 ore di lavoro umano equivalente
   → Symphony DEVE splittare ulteriormente con /to-issues
   → Mai assegnare a un singolo agente
```

---

## 5.6 Collision Point 6 — Proof of Work Falso Positivo

**Descrizione**: Gli agenti producono test che passano ma non testano il comportamento corretto (test scritti per passare, non per validare).

**Anti-pattern**:
```
❌ SBAGLIATO:
/tdd skill mal configurata:
  → Claude scrive il codice PRIMA del test
  → Poi scrive un test che verifica il codice che ha già scritto
  → Test passa sempre (tautologia)
  → Symphony accetta come "proof of work"
  → Il bug o il comportamento scorretto persiste in prod
```

**Pattern corretto**:
```
✅ CORRETTO:
1. /tdd DEVE seguire l'ordine: test PRIMA del codice
2. Il test deve fallire prima dell'implementazione (RED verificato)
3. Symphony verifica che il commit history mostri:
   - Commit 1: test che fallisce
   - Commit 2: implementazione che fa passare il test
   - Commit 3: refactor (test ancora verde)
4. Se il commit history non mostra questo pattern → task rejected
```

---

## 5.7 Summary Anti-Pattern Table

| Anti-Pattern | Rischio | Soluzione |
|-------------|---------|-----------|
| Doppio planning | Piani divergenti, confusione | Separazione netta: Symphony = sequencing, Claude = implementation |
| Context contamination cross-agent | Merge conflict, regressioni | Branch isolation + file locking nel DAG |
| Hook → Symphony retry loop | Spreco di risorse, nessun fix | Agente auto-fixa hook failure prima di escalare |
| Conflitto CLAUDE.md vs WORKFLOW.md | Agente paralizzato | Gerarchia esplicita di precedenza istruzioni |
| Task troppo grande | Context window overflow, output parziali | Soglie operative: max 4-8h equivalente umano |
| Proof of work falso positivo | Bug in prod mascherato da test | TDD strict order + commit history validation |

</anti_patterns>

---

# PARTE 6: IMPLEMENTAZIONE — Da Zero a Operativo

## 6.1 Prerequisiti Non Negoziabili

Prima di attivare qualsiasi orchestrazione Symphony, questi elementi devono esistere:

```
REPO STRUCTURE MINIMA:
repo/
  ├── CLAUDE.md              ← < 200 righe, comandi + regole
  ├── CONTEXT.md             ← dominio + ubiquitous language
  ├── docs/
  │   └── adr/               ← almeno 2-3 ADR retroattivi
  ├── .claude/
  │   └── settings.json      ← hooks configurati
  ├── .husky/                ← pre-commit hooks attivi
  └── WORKFLOW.md            ← istruzioni Symphony per agenti
```

**🚨 CRITICO**: Non attivare Symphony su un repo senza questa struttura. Gli agenti senza knowledge base producono output generici che non rispettano il dominio e le decisioni architetturali del progetto.

---

## 6.2 WORKFLOW.md — Il Contratto tra Symphony e Claude

```markdown
# WORKFLOW.md — Agent Instructions

## Context
Leggi SEMPRE prima di iniziare:
1. CONTEXT.md (dominio e linguaggio ubiquitous)
2. docs/adr/ (decisioni architetturali passate)
3. CLAUDE.md (regole di build e stile)

## Task Execution Protocol
1. Mai iniziare a scrivere codice senza prima aver letto il task completamente
2. Se il task è ambiguo: usa /grill-me prima di qualsiasi implementazione
3. Se il task tocca un'area con ADR rilevante: leggi l'ADR prima di procedere
4. Implementa sempre con TDD (/tdd skill)
5. Prima del commit: verifica che tutti i test passino

## Proof of Work Requirements
- Test suite: tutti i test devono passare
- Coverage: non deve diminuire rispetto al baseline
- Lint: zero errori (hook deterministico)
- Types: zero errori TypeScript

## Escalation Policy
- 1 fallimento: retry con approccio diverso
- 2 fallimenti: /rewind + nuovo approccio radicalmente diverso
- 3 fallimenti: stop, notifica Symphony, task torna in queue
```

---

## 6.3 Checklist di Attivazione

### Settimana 1 — Foundation
- [ ] CLAUDE.md creato (< 200 righe)
- [ ] CONTEXT.md con ubiquitous language
- [ ] docs/adr/ con ADR retroattivi delle decisioni principali
- [ ] Husky + lint-staged installato
- [ ] Git guardrails configurati
- [ ] WORKFLOW.md scritto

### Settimana 2 — Skills
- [ ] /tdd installato e testato su una feature reale
- [ ] /triage-issue installato e testato su un bug reale
- [ ] /grill-me installato e testato su un task ambiguo
- [ ] /to-prd installato

### Settimana 3 — Orchestrazione
- [ ] Issue tracker con stati macchina definiti (Open → In Progress → Review → Done)
- [ ] Label system configurato (bug, feature, refactor, architecture, knowledge)
- [ ] Symphony (o equivalente) in polling sul tracker
- [ ] Primo task orchestrato end-to-end in ambiente di test

### Settimana 4 — Validazione
- [ ] Review del primo ciclo completo
- [ ] Identificazione di collision points specifici al proprio stack
- [ ] Calibrazione delle soglie (task size, context limits)
- [ ] ADR aggiornati con le decisioni prese durante il setup

---

# PARTE 7: PRINCIPI ARCHITETTURALI FONDAMENTALI

Questi sono i principi irriducibili dell'architettura ibrida. Ogni decisione di implementazione deve essere valutata contro questi principi:

**Principio 1 — Separazione dei Layer**  
Symphony gestisce il macro-context. Claude Code gestisce il micro-context. Nessuna eccezione.

**Principio 2 — Context by Design**  
Il context di ogni agente è costruito deliberatamente prima dello spawn, non accumulato durante l'esecuzione.

**Principio 3 — Proof First**  
Nessun task è completato sulla parola dell'agente. Il proof of work è verificabile e automatizzato.

**Principio 4 — Determinism at the Boundary**  
I confini tra sistemi (commit, deploy, merge) sono controllati da meccanismi deterministici (hooks), non da istruzioni advisory.

**Principio 5 — Knowledge is Infrastructure**  
CONTEXT.md, ADRs e CLAUDE.md non sono documentazione opzionale. Sono infrastruttura critica senza cui l'architettura non funziona.

**Principio 6 — Fail Fast, Escalate Slow**  
Gli agenti tentano auto-recovery (2 volte), poi escalano a Symphony, poi escalano all'umano. Non il contrario.

**Principio 7 — Isolation Prevents Contamination**  
Ogni agente lavora in un workspace isolato con un context snapshot immutabile. La contaminazione cross-sessione è un bug architetturale, non un caso d'uso.

---

---

**Documento compilato**: 1 maggio 2026  
**Versione**: 1.0 — Framework Radicale  
**Status**: Production-ready come metodologia  
**Prossimo aggiornamento**: Quando Symphony supera lo stato di engineering preview e supporta tracker multipli e runtime alternativi a Codex
