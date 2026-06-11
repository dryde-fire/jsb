# 🏗️ Hybrid Agentic Architecture v4.0
## The 5-Layer Model for AI-Assisted Development

**Versione**: 4.0 — Production Ready  
**Data**: Maggio 2026  
**Status**: ✅ Stable, Tested, Operational  
**Precedenti**: v1.0 (Symphony concept) → v2.0 (layer model) → v3.0 (draft) → v4.0 (complete)

---

## 📋 CHANGELOG RAPIDO

| Versione | Data | Cosa Cambia |
|----------|------|------------|
| v1.0 | Maggio 2026 | Symphony + Claude Code concept (macro/micro layers) |
| v2.0 | (Draft) | Aggiunta nominature 5-layer dall'ADK |
| v3.0 | Maggio 2026 | SETUP-DEFINITIVO-v3.0-FOR-DUMMIES release |
| **v4.0** | **Oggi** | **5-layer complete + Distribution + Diagrams + ADK integration** |

---

# PARTE 0: VISUAL EXECUTIVE SUMMARY (30 secondi)

## La Struttura in Una Immagine

```
           ┌─────────────────────────────────┐
           │    SYMPHONY ORCHESTRATION       │
           │   (Who, What, When, Where)     │
           │                                 │
           │  • Task DAG routing             │
           │  • State management             │
           │  • Proof of work validation     │
           │  • Team coordination            │
           └────────────┬────────────────────┘
                        │ spawns agents with
                        │ isolated context
           ┌────────────▼────────────────────┐
           │   CLAUDE CODE EXECUTION LAYER    │
           │   (How to do it right)          │
           │                                 │
           │ ┌─────────────────────────────┐ │
           │ │ L1: MEMORY LAYER            │ │
           │ │ CLAUDE.md (constitution)    │ │
           │ │                             │ │
           │ │ ┌─────────────────────────┐ │ │
           │ │ │ L2: KNOWLEDGE LAYER     │ │ │
           │ │ │ Skills + ADRs           │ │ │
           │ │ │                         │ │ │
           │ │ │ ┌─────────────────────┐ │ │ │
           │ │ │ │ L3: GUARDRAIL       │ │ │ │
           │ │ │ │ Hooks (determinism) │ │ │ │
           │ │ │ │                     │ │ │ │
           │ │ │ │ ┌─────────────────┐ │ │ │ │
           │ │ │ │ │ L4: DELEGATION  │ │ │ │ │
           │ │ │ │ │ Subagents + TDD │ │ │ │ │
           │ │ │ │ └─────────────────┘ │ │ │ │
           │ │ │ └─────────────────────┘ │ │ │
           │ │ └─────────────────────────┘ │ │
           │ └─────────────────────────────┘ │
           └────────────┬────────────────────┘
                        │
           ┌────────────▼────────────────────┐
           │ L5: DISTRIBUTION LAYER          │
           │ manifest.json (team config)     │
           └─────────────────────────────────┘
```

**Cosa significa?**
- **Symphony** = Il "capo progetto" (decide cosa fare, quando, chi)
- **Layers 1-4** = Gli "operai specializzati" (fanno il lavoro bene)
- **L5** = La "cassetta degli attrezzi" (distribuita al team)

---

# PARTE 1: I CINQUE LAYER — Cosa È, Dove Vive, Perché Esiste

## 🔴 L1 — MEMORY LAYER (La Costituzione)

### Cosa È?
Il file **CLAUDE.md** — il contratto scritto tra te e l'AI.

```
CLAUDE.md = La carta costituzionale del tuo progetto
```

### Dove Vive?
```
repo/
├── ~/.claude/CLAUDE.md          (globale, ogni progetto)
└── ./.claude/CLAUDE.md          (locale, solo questo progetto)
```

### Cosa Contiene?
```markdown
# I Principi di Ragionamento
- Think Before Coding
- Simplicity First
- Surgical Changes
- Goal-Driven Execution

# I Comandi Bash Comuni
npm run dev
npm run test
npm run build

# Le Regole di Stile
- TypeScript + ES Modules
- Nomi: kebab-case (files), camelCase (code)
- Max 100 caratteri per linea

# L'Architettura
- Dove vive il codice
- Come è organizzato
- Cosa non si tocca
```

### Perché Esiste?
**Claude dimentica le cose.** Se non glielo dici una volta nel CLAUDE.md, ogni sessione dimanda "come funziona questo progetto?"

**Vantaggio**: Scrivi una volta, risparmi 100 prompts.

### Lunghezza
**< 200 righe** — Se è più lungo, Claude lo ignora (troppo rumore).

---

## 🟠 L2 — KNOWLEDGE LAYER (Gli Esperti Specializzati)

### Cosa È?
La combinazione di:
1. **Skills** — "Ricette" riusabili (PDF skill, TDD skill, Design skill)
2. **CONTEXT.md** — Il vocabolario del dominio ("un Order è...")
3. **docs/adr/** — Le decisioni passate ("Perché usiamo Zustand")

### Dove Vive?
```
repo/
├── ./.claude/skills/
│   ├── tdd-skill/
│   │   ├── SKILL.md
│   │   └── examples/
│   └── code-review-skill/
├── CONTEXT.md          (ubiquitous language)
└── docs/adr/
    ├── ADR-001-tech-stack.md
    └── ADR-002-why-zustand.md
```

### Cosa Contiene una Skill?
```
SKILL.md:
- Quando attivarmi? (trigger)
- Come funziono? (istruzioni)
- Cosa sbaglio spesso? (gotchas)
- Esempi reali (examples/)
```

### Cosa Contiene CONTEXT.md?
```markdown
# Ubiquitous Language (Il vocabolario)

## User
- È una persona che usa l'app
- Ha email, password, profilo

## Order
- È una richiesta di acquisto
- Stati: Pending → Paid → Shipped → Done
- Non può modificarsi dopo Paid

## LineItem
- È un prodotto in un ordine
- Quantità × prezzo = subtotal
```

### Cosa Contiene un ADR?
```markdown
# ADR-001: Perché PostgreSQL e Non MongoDB?

## Decisione
Usiamo PostgreSQL

## Perché?
- I dati sono relazionali (Order → LineItems)
- Transazioni ACID (pagamenti sicuri)
- JSON support nativo

## Conseguenze
- ✅ Affidabili
- ❌ Se scale a 100K req/sec, potrebbe rallentare

## Quando Cambiare?
Se i dati diventano > 100GB o query super complesse
```

### Perché Esiste?
**Claude deve capire il dominio, non solo il codice.**

Se dici "implementa validazione ordine", Claude senza CONTEXT.md dirà "ok, aggiungo un check". Claude con CONTEXT.md dirà "ok, aggiungo un check che un ordine non può avere 0 lineitem, che status segue il flow Pending→Paid→Shipped→Done, e che non può modificarsi dopo Paid".

**Differenza**: Codice generico vs. Codice che conosce le regole di business.

---

## 🟡 L3 — GUARDRAIL LAYER (Le Regole Non Negoziabili)

### Cosa È?
**Hooks** — Bash script che si attivano automaticamente su eventi.

```
Hook = Una regola che si esegue SEMPRE, senza eccezione
```

### Dove Vive?
```
repo/
├── .claude/hooks/
│   ├── PreToolUse.sh      (prima di qualsiasi comando)
│   ├── PostToolUse.sh     (dopo qualsiasi comando)
│   ├── SessionStart.sh    (quando sessione inizia)
│   └── SubagentStop.sh    (quando subagente finisce)
└── .husky/
    ├── pre-commit         (prima del commit)
    └── pre-push           (prima del push)
```

### Cosa Contiene?
```bash
# PreToolUse.sh — Blocca comandi pericolosi
if [[ "$command" == *"git push --force"* ]]; then
  echo "❌ BLOCCATO: git push --force è vietato"
  exit 1
fi

# PostToolUse.sh — Formatta il codice automaticamente
prettier --write {edited_files}
eslint --fix {staged_files}

# pre-commit — Testa prima di committare
npm run test
npm run type-check
```

### Perché Esiste?
**Claude è intelligente ma disattento.**

Senza hook:
- Claude scrive codice non formattato ❌
- Claude committe senza testare ❌
- Claude fa `git push --force` per sbaglio ❌

Con hook:
- Codice formattato automaticamente ✅
- Test SEMPRE eseguiti prima di commit ✅
- Comandi pericolosi BLOCCATI ✅

**Vantaggio**: 100% compliance — non è una raccomandazione, è una REGOLA.

---

## 🟢 L4 — DELEGATION LAYER (I Lavoratori Specializzati)

### Cosa È?
**Subagenti isolati** che fanno un lavoro specifico in parallelo.

```
Subagente = Un Claude Code in una "stanza privata"
           con il suo context isolato
           che fa UN lavoro specifico
           e ritorna i risultati al main thread
```

### Dove Vive?
```
repo/
└── .claude/subagents/
    ├── feature-dev.md       (implementa feature)
    ├── code-reviewer.md     (rivede il codice)
    ├── test-runner.md       (esegue i test)
    └── explorer.md          (esplora il codebase)
```

### Cosa Contiene?
```markdown
# feature-dev Subagent

## Chi sei?
Un specialista in implementazione TDD

## Cosa fai?
- Leggi il task
- Scrivi il test che fallisce (RED)
- Scrivi il codice minimo (GREEN)
- Refactori elegantemente (REFACTOR)

## Quali strumenti hai?
- /tdd skill
- Accesso a CLAUDE.md + CONTEXT.md + ADRs rilevanti
- Permessi per creare/modificare file

## Cosa TORNI?
- Test log (passa/fallisce)
- PR diff
- Commit history
```

### Come Funziona in Pratica?

```
Main Thread (Symphony):
  "Implementa login con Google OAuth"
           │
           ├─ Spawn: code-reviewer subagent
           │         (rivede il mio codice in parallelo)
           │
           ├─ Spawn: test-runner subagent
           │         (esegue test in parallelo)
           │
           └─ Spawn: feature-dev subagent
                     (implementa il login)
                     │
                     ▼ (dopo 2-3 ore di lavoro)
                     Ritorna: "Login implementato, test passano"

Main Thread raccoglie i risultati:
  ✅ Feature implementata
  ✅ Codice revisionato
  ✅ Test passano
  ✅ Merge!
```

### Perché Esiste?
**Un agente non può concentrarsi su 5 cose contemporaneamente.**

Senza subagenti:
- Claude fa la feature ❌
- Intanto dimentica di testare ❌
- Intanto dimentica di rivedere il codice ❌
- Contesto si riempie, qualità degrada ❌

Con subagenti:
- feature-dev fa il suo lavoro ✅
- test-runner fa il suo lavoro in parallelo ✅
- code-reviewer fa il suo in parallelo ✅
- Context di ognuno rimane fresco e focalizzato ✅

---

## 🟣 L5 — DISTRIBUTION LAYER (La Cassetta degli Attrezzi del Team)

### Cosa È?
Un file **manifest.json** che dice:
- "Quali skills ha il team?"
- "Quali agenti abbiamo?"
- "Quali regole vale per tutti?"

```
manifest.json = La configurazione centralizzata del team
```

### Dove Vive?
```
repo/
└── agent-manifest.json
```

### Cosa Contiene?
```json
{
  "version": "1.0",
  "team": "TianYi Studio",
  "sync": "weekly",
  
  "layers": {
    "l1_memory": {
      "global_claude_md": "~/.claude/CLAUDE.md",
      "project_claude_md": "./.claude/CLAUDE.md"
    },
    "l2_knowledge": {
      "skills": [
        "tdd-skill",
        "code-review-skill",
        "pdf-skill"
      ],
      "context_file": "CONTEXT.md",
      "adrs": "docs/adr/"
    },
    "l3_guardrails": {
      "hooks": [
        "PreToolUse.sh",
        "PostToolUse.sh",
        "SessionStart.sh"
      ],
      "husky": [
        "pre-commit",
        "pre-push"
      ]
    },
    "l4_delegation": {
      "subagents": [
        "feature-dev",
        "code-reviewer",
        "test-runner"
      ]
    }
  },
  
  "permissions": {
    "git": ["commit", "branch", "merge"],
    "api": ["read", "write"],
    "files": ["modify", "create"],
    "dangerous": ["blocked"]
  },
  
  "failsafe": {
    "max_retries": 2,
    "rewind_on_error": true,
    "escalate_after": "2 failures"
  }
}
```

### Perché Esiste?
**Un team ha bisogno di sincronizzazione.**

Senza manifest.json:
- Dev A usa skill X, Dev B non lo sa ❌
- Dev A ha hook Y, Dev B non lo ha ❌
- Inconsistenza — feature compilano diverse ❌

Con manifest.json:
- Tutti hanno le stesse skill ✅
- Tutti hanno gli stessi hook ✅
- Tutti seguono le stesse regole ✅
- `team.install` = onboarding istantaneo ✅

---

# PARTE 2: SYMPHONY ORCHESTRATION LAYER
## Il "Capo Progetto" che Coordina Tutto

## 2.1 Cosa È Symphony?

```
Symphony = Il sistema che:
  • Decide COSA fare (quali task)
  • Decide QUANDO farlo (priorità)
  • Decide CHI lo fa (quale agente)
  • Valida il risultato (proof of work)
  • Gestisce il fallimento (retry policy)
```

**Symphony NON scrive codice.** Symphony coordina chi lo scrive.

## 2.2 Il Flusso Completo (Macro-Level)

```
┌─────────────────────────────────────────┐
│ 1. RESEARCH (Issue Tracker Polling)     │
│                                         │
│ Symphony legge le issue aperte          │
│ Identifica quelle "pronte per agente"   │
│ (hanno label "ready", non sono bloccate)│
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│ 2. CONTEXT ASSEMBLY                     │
│                                         │
│ Symphony prepara il context snapshot:   │
│ • CLAUDE.md (regole)                    │
│ • CONTEXT.md (dominio)                  │
│ • ADRs rilevanti (decisioni)            │
│ • Task description (cosa fare)          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│ 3. AGENT SPAWN                          │
│                                         │
│ Symphony crea un agente isolato con:    │
│ • Il context snapshot immutabile        │
│ • Permessi specifici al task            │
│ • Subagenti per supporto                │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│ 4. EXECUTION (Claude Code Session)      │
│                                         │
│ L'agente usa i 5 layer:                 │
│ • L1 (Memory) — ricorda le regole       │
│ • L2 (Knowledge) — capisce il dominio   │
│ • L3 (Guardrails) — rispetta le regole │
│ • L4 (Delegation) — delega sottotask    │
│ → Produce proof of work                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│ 5. PROOF OF WORK COLLECTION             │
│                                         │
│ Symphony raccoglie:                     │
│ • Test log (passa/fallisce)             │
│ • CI status (verde/rosso)               │
│ • PR diff (cosa è cambiato)             │
│ • Coverage (linee testate)              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│ 6. VALIDATION GATE                      │
│                                         │
│ Se proof di work è OK:                  │
│   → MERGE automatico                    │
│ Se proof di work ha problemi:           │
│   → RETRY con nuovo agente              │
│ Se 2 retry falliscono:                  │
│   → ESCALATE a umano                    │
└─────────────────────────────────────────┘
```

## 2.3 Cosa Fa Symphony (Responsabilità)

| Cosa | Chi Decide | Come |
|------|-----------|------|
| **COSA** fare (quale feature) | Task label + priority | issue tracker |
| **QUANDO** (ordine) | DAG dependencies | sequencing |
| **CHI** (quale agente) | Skill match + permessi | agent routing |
| **COME** validare | Test + CI status | proof of work |
| **SE FALLISCE** | Retry policy (max 2) | auto-escalation |

## 2.4 La Regola d'Oro: La Separazione

```
🚨 CRITICO 🚨

Symphony ≠ Claude Code
┌─────────────────────────────────┐
│ SYMPHONY                        │
│ • Non scrive codice             │
│ • Non gestisce context window   │
│ • Non sa di CLAUDE.md           │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ CLAUDE CODE                     │
│ • Non gestisce stato globale    │
│ • Non sa di altri task          │
│ • Non sa come sequenziare work  │
└─────────────────────────────────┘

Comunicano solo via:
  Input:  Task + context snapshot
  Output: Proof of work (test log + PR diff)
```

Se viola questa regola:
- ❌ Context contamination tra task
- ❌ Agenti litigano per gli stessi file
- ❌ Merge conflict hell

---

# PARTE 3: LAYER DETAILS — Cosa Va Dove e Perché

## 3.1 Matrix di Allocazione

| Informazione | Dove Va | Perché | Quando Caricata |
|---|---|---|---|
| "Usa kebab-case per i file" | L1 (CLAUDE.md) | È una regola globale | Sempre (load session) |
| "Order non può avere 0 lineitems" | L2 (CONTEXT.md) | È business logic | Sempre (load session) |
| "Abbiamo Zustand, non Redux" | L2 (ADRs) | È una decisione storica | Sempre (load session) |
| "La skill TDD è come funziona" | L2 (Skills) | È expertise on-demand | Se viene chiesto "/tdd" |
| "Blocca git push --force" | L3 (Hooks) | È safety critical | Sempre (auto hook) |
| "Implementa login Google" | Task description | È il lavoro specifico | Quando spawn agente |
| "Usa questo agente specializzato" | L4 (Subagent def) | È una delegazione | Quando serve parallelo |
| "Ecco le skill del team" | L5 (Manifest) | È coordinamento | Una volta a week |

## 3.2 Load Order (Cosa Si Carica Quando)

```
Sessione Inizia
     │
     ▼
L1 LOAD: CLAUDE.md (100 token overhead, non negoziabile)
     │
     ▼
L2 LOAD: CONTEXT.md + rilevanti ADRs (300 token)
     │
     ▼
L3 SETUP: Hooks (0 token, deterministici)
     │
     ▼
Task description ricevuta
     │
     ▼
Costruisci context snapshot per agente
     │
     ├─ Seleziona skills rilevanti (L2, on-demand)
     ├─ Seleziona subagenti (L4, se parallelo)
     │
     ▼
Spawn agente
     │
     ▼
Agente usa i 5 layer
```

## 3.3 Context Window Sizing

```
Budget totale per sessione: 200K token (Claude 3.5 Sonnet)

L1 (CLAUDE.md):          100 token (fisso)
L2 (CONTEXT.md + ADRs):  300 token (fisso)
L3 (Hooks):              0 token (esterno)
L4 (Subagenti):          0 token (spawn separato)
L5 (Manifest):           50 token (metadata)

Subtotale fisso:         450 token

Task-specific:           5,000-10,000 token
                         (dipende dalla complessità)

Spazio libero:           ~190K token
                         (per exploration, refactor, iterazione)

REGOLA: Compact al 50% (100K token) per evitare degradation
```

---

# PARTE 4: WORKFLOW INTEGRATION
## Come Tutto Funziona Insieme

## 4.1 Scenario Reale: Feature Pagamento

```
Giorno 1, Mattina
├─ PM crea issue: "Implementa pagamento Stripe"
├─ Assegna label "feature", priority "high"
├─ Symphony legge l'issue
│
└─ Symphony: "Non è bloccata, ha contesto. Spawn agente"
     │
     ▼ Context snapshot preparato:
     ├─ CLAUDE.md (regole)
     ├─ CONTEXT.md (Order, Payment, LineItem definitions)
     ├─ ADR-001 (Tech stack)
     ├─ ADR-002 (Zustand over Redux)
     ├─ ADR-003 (Why Stripe over Paypal)
     └─ Task: "Implementa pagamento Stripe"
     │
     ▼ Claude Code Session (feature-dev agent)
     ├─ Legge tutto il contesto
     ├─ Entra in Plan Mode (/grill-me)
     │  "Una Order può essere pagata 2 volte? No"
     │  "Stripe webhook è sicuro? Devo validare firma"
     │  "Refund policy? Entro 30 giorni da Delivered"
     │
     ├─ /to-prd: Crea spec formale
     │
     ├─ /to-issues: Splotta in 3 task
     │  ├─ Setup Stripe API + keys
     │  ├─ Payment component + form
     │  └─ Webhook handler + test
     │
     └─ /tdd: Implementa con RED-GREEN-REFACTOR
        Spawn paralleli:
        ├─ code-reviewer (rivede il codice)
        └─ test-runner (esegue i test)

Giorno 1, Sera
├─ test-runner ritorna: "✅ 50 test passano, coverage 95%"
├─ code-reviewer ritorna: "✅ Nessun console.log, types ok, no hardcoded secrets"
├─ feature-dev ritorna: "✅ 3 task completi, PRs pronti"
│
└─ Symphony: "Proof di work OK! Merge automatico!"
     │
     └─ `git merge feature/stripe-payment` ✅

Giorno 2
└─ Feature live in production 🚀
```

## 4.2 Scenario Problematico: Cosa Succeede Se Fallisce?

```
Feature-dev agent: "Ho fallito il test, TypeError on line 42"
     │
     ▼ Hook L3 detecta l'errore:
     └─ "Test fallito. Non committo."
     │
     ▼ Claude Code agent tenta auto-fix:
     ├─ Legge l'errore
     ├─ Modifica il codice
     └─ Corre di nuovo il test
     │
     Prova 1: "✅ Test passa!"
     │
     └─ Symphony: "Proof di work OK! Merge!"

---

Se prova 1 FALLISCE ancora:
     │
     ▼ Prova 2: Agente cambia approccio radicalmente
     ├─ Rewind a checkpoint precedente (/rewind)
     ├─ Usa una strategia diversa
     └─ Corre il test
     │
     Prova 2: "Ancora fail. Tipo diverso di errore."
     │
     └─ Symphony: "2 fallimenti. Non riprovo."
     │
     └─ ESCALATE A UMANO
        Messaggio: "Feature pagamento fallisce. Root cause: [...]
                    Attendo intervento umano."
```

---

# PARTE 5: COLLISION POINTS
## I 6 Problemi Più Comuni e Come Evitarli

### Collision Point 1: Doppio Planning
**Problema**: Symphony pianifica il DAG, Claude pianifica l'implementazione. Chi vince?

**Soluzione**:
- Symphony pianifica SOLO sequencing (quale task, in quale ordine)
- Claude pianifica SOLO implementation (come implementarlo)
- Confini chiari = niente conflitto

```
❌ SBAGLIATO:
Symphony: "Fai il login in 3 step: 1) DB, 2) API, 3) Frontend"
Claude: "No, faccio 1) API, 2) Frontend, 3) DB"
→ CONFLITTO

✅ CORRETTO:
Symphony: "Task: Implementa login. Dipendenze: nessuna. Esperto: auth-specialist-agent"
Claude: "Capito. Faccio: test→ implementazione → refactor"
```

### Collision Point 2: Context Contamination Cross-Agent
**Problema**: Due agenti paralleli leggono file modificati l'uno dall'altro.

**Soluzione**:
- Ogni agente = branch separato
- File condivisi = locked durante modifica
- DAG esplicito delle dipendenze file

```
❌ SBAGLIATO:
Agent A (feature/auth) modifica src/utils/crypto.ts
Agent B (feature/payment) legge src/utils/crypto.ts
→ Agent B costruisce su codice non mergiato
→ CONFLICT

✅ CORRETTO:
DAG dice: "feature/payment dipende da feature/auth"
→ feature/auth finisce prima
→ feature/payment inizia dopo
```

### Collision Point 3: Hook Retry Loop
**Problema**: Hook fallisce, Symphony riavvia agente, agente ripete lo stesso errore infinitamente.

**Soluzione**:
- Agente legge l'output dello hook
- Agente tenta auto-fix PRIMA di segnalare failure
- Max 2 retry auto, poi escalate

```
Agente: scrive codice con type error
Hook: "TypeError detected"
Agente: "Letto l'errore. Provo a fixare."
Agente: ✅ Fixed, test passa
Symphony: OK, merge

Se agente fallisce 2 volte: escalate, non loop infinito
```

### Collision Point 4: Proof of Work False Positive
**Problema**: Agente scrive test che passano, ma non testano il comportamento corretto.

**Soluzione**:
- TDD strict order: test PRIMA del codice
- Validation: test deve fallire prima di implementazione
- Commit history proof: leggi il git log

```
❌ SBAGLIATO:
/tdd skill mal usato:
1. Claude scrive il codice
2. Claude scrive test che verifica il codice
3. Test passa (tautologia!)
→ Feature ha bug in produzione

✅ CORRETTO:
/tdd strict:
1. Claude scrive test che FALLISCE
2. Claude scrive codice minimo
3. Test PASSA
4. Git log mostra: commit1=test fail, commit2=impl, commit3=refactor
```

### Collision Point 5: Task Troppo Grande
**Problema**: Agente riceve task da 24 ore, context window si riempie, output degrada.

**Soluzione**:
- Soglia massima: 4-8 ore di lavoro umano equivalente
- Symphony splitta con /to-issues se più grande
- Ogni subtask è indipendente

```
❌ SBAGLIATO:
Symphony: "Implementa un CRM completo"
→ Agente context overflow after 4 ore
→ Output degradato

✅ CORRETTO:
Symphony: /to-issues su task
→ "Implementa auth"
→ "Implementa contacts CRUD"
→ "Implementa reports"
Spawn 3 agenti in parallelo
```

### Collision Point 6: Knowledge Rot
**Problema**: CONTEXT.md invecchia, ADRs non sono aggiornati, agenti producono codice incoerente.

**Soluzione**:
- CONTEXT.md review: mensile (team meeting)
- ADRs: aggiornati quando decisione cambia
- /ubiquitous-language skill: extract automatico

```
❌ SBAGLIATO:
CONTEXT.md dice: "Order ha status Pending/Paid/Done"
Realtà: Nuovo status Refunded aggiunto 3 mesi fa
Agente: non sa di Refunded, produce codice incompleto

✅ CORRETTO:
Mensile: team review CONTEXT.md
Quando decision cambia: nuovo ADR
Agente: sempre vede la versione corrente
```

---

# PARTE 6: IMPLEMENTATION CHECKLIST
## Come Attivare Tutto Step by Step

## 6.1 Week 1: Foundation

- [ ] Crea L1 (CLAUDE.md)
  - [ ] 4 principi di ragionamento
  - [ ] Comandi bash comuni
  - [ ] Regole di stile
  - [ ] Architettura overview
  - [ ] < 200 righe

- [ ] Crea L2 (CONTEXT.md)
  - [ ] Ubiquitous language (almeno 5 concetti)
  - [ ] Business rules (almeno 3)
  - [ ] Invarianti (almeno 3)

- [ ] Crea docs/adr/
  - [ ] ADR-001: Tech stack
  - [ ] ADR-002: State management
  - [ ] ADR-003: API design

- [ ] Setup npm + TypeScript
  - [ ] `npm init -y`
  - [ ] `npm install typescript prettier eslint`
  - [ ] `tsconfig.json`

## 6.2 Week 2: Automation

- [ ] Installa Husky
  - [ ] `npx husky install`
  - [ ] pre-commit hook: format + lint + type-check
  - [ ] pre-push hook: test suite

- [ ] Configura L3 (Hooks)
  - [ ] `.claude/hooks/PreToolUse.sh` (blocca git --force)
  - [ ] `.claude/hooks/PostToolUse.sh` (auto-format)

- [ ] Crea primo test
  - [ ] Setup vitest
  - [ ] Scrivi un test semplice
  - [ ] Verifica che passa

## 6.3 Week 3: Knowledge

- [ ] Crea 3-4 Skills (L2)
  - [ ] /tdd-skill
  - [ ] /code-review-skill
  - [ ] /pdf-skill (se gestisci PDF)

- [ ] Estrai ubiquitous-language
  - [ ] Usa `/ubiquitous-language` skill
  - [ ] Aggiorna CONTEXT.md

- [ ] Crea subagents (L4)
  - [ ] feature-dev.md
  - [ ] code-reviewer.md
  - [ ] test-runner.md

## 6.4 Week 4: Distribution

- [ ] Crea agent-manifest.json (L5)
  - [ ] Specifica skills
  - [ ] Specifica subagenti
  - [ ] Specifica permessi
  - [ ] Specifica hook

- [ ] Setup Symphony mock (se non hai real Symphony)
  - [ ] Script che legge issue tracker
  - [ ] Script che prepara context snapshot
  - [ ] Script che valida proof di work

---

# PARTE 7: KEY PRINCIPLES
## I 7 Principi Non Negoziabili

### Principio 1: Context by Design
> Il context di ogni agente è costruito **deliberatamente** prima dello spawn, non accumulato durante l'esecuzione.

### Principio 2: Separation of Concerns
> Symphony gestisce il macro (cosa, quando, chi). Claude Code gestisce il micro (come). Niente overlap.

### Principio 3: Proof First
> Nessun task è completato sulla parola dell'agente. Il proof di work è verificabile (test log + CI status).

### Principio 4: Determinism at Boundaries
> I confini tra sistemi (commit, deploy, merge) sono controllati da hook, non da istruzioni advisory.

### Principio 5: Isolation Prevents Contamination
> Ogni agente = contesto snapshot immutabile. La contaminazione cross-sessione è un bug architetturale.

### Principio 6: Knowledge is Infrastructure
> CONTEXT.md, ADRs e CLAUDE.md non sono documentazione opzionale. Sono infrastruttura critica.

### Principio 7: Fail Fast, Escalate Slow
> Auto-recovery (max 2 tentativi), poi escalation a umano. Non loop infinito.

---

# PARTE 8: VISUAL DIAGRAMS
## Come Communichiamo L'Architettura

### Diagram 1: 5-Layer Concentrica
```
                    SYMPHONY
                 (orchestration)
                        ▲
                        │
        ┌───────────────┴───────────────┐
        │                               │
        │  CLAUDE CODE EXECUTION LAYER   │
        │                               │
        │  ┌─────────────────────────┐  │
        │  │ L1: MEMORY LAYER        │  │
        │  │ (CLAUDE.md)             │  │
        │  │                         │  │
        │  │ ┌─────────────────────┐ │  │
        │  │ │ L2: KNOWLEDGE       │ │  │
        │  │ │ (Skills+CONTEXT+ADR)│ │  │
        │  │ │                     │ │  │
        │  │ │ ┌─────────────────┐ │ │  │
        │  │ │ │ L3: GUARDRAIL   │ │ │  │
        │  │ │ │ (Hooks)         │ │ │  │
        │  │ │ │                 │ │ │  │
        │  │ │ │ ┌─────────────┐ │ │ │  │
        │  │ │ │ │ L4: DELEG.  │ │ │ │  │
        │  │ │ │ │ (Subagents) │ │ │ │  │
        │  │ │ │ └─────────────┘ │ │ │  │
        │  │ │ └─────────────────┘ │ │  │
        │  │ └─────────────────────┘ │  │
        │  └─────────────────────────┘  │
        └──────────────┬────────────────┘
                       │
                ┌──────▼──────┐
                │ L5: DISTRIB  │
                │ (manifest)   │
                └──────────────┘
```

### Diagram 2: Task Execution Flow
```
Issue Tracker
     │
     ▼
Symphony Research
 • Leggi issue
 • Identifica ready
     │
     ▼
Context Assembly
 • CLAUDE.md
 • CONTEXT.md
 • ADRs
 • Task desc
     │
     ▼
Agent Spawn
     │
     ├─ feature-dev agent
     ├─ code-reviewer agent (parallelo)
     └─ test-runner agent (parallelo)
     │
     ▼ (parallel execution)
     │
     ├─ feature-dev produce code
     ├─ code-reviewer review it
     └─ test-runner run tests
     │
     ▼
Proof Collection
     │
     ▼
Validation Gate
 • All tests pass?
 • No hardcoded secrets?
 • Coverage ok?
     │
  ┌──┴──┐
  │ OK  │ FAIL
  ▼     ▼
MERGE  RETRY (max 2)
       │
       If fail 2x
       ▼
       ESCALATE
```

---

# PARTE 9: FAQ

## D: Posso usare questa architettura con uno stack diverso?

R: Sì. Questa architettura è **stack-independent**.
- Symphony? Puoi usare Linear, ClickUp, Jira, GitHub Issues
- Claude Code? Puoi usare Cursor, Codex, OpenCode
- Persistenza? Puoi usare Node.js, Python, Go, Rust
- DB? Puoi usare PostgreSQL, MongoDB, Firebase

I **principi** rimangono uguali. Solo l'implementazione cambia.

## D: Quanto tempo per setup completo?

R: 
- Week 1: 5-6 ore (foundation)
- Week 2: 4-5 ore (automation)
- Week 3: 6-7 ore (knowledge)
- Week 4: 3-4 ore (distribution)

**Totale: ~20 ore di lavoro concentrato.**

Dopo: maintenance mode (1-2 ore/settimana per update CONTEXT.md e ADRs).

## D: Cosa succede se Symphony fallisce?

R: Symphony è un **orchestratore**, non l'AI.

Se Symphony fallisce:
- L'umano interviene manualmente
- Assegna il task direttamente a Claude Code
- Claude Code funziona comunque (L1-L4 rimangono valide)
- Risultato: un po' più lento, ma funzionale

## D: Questa architettura funziona per team di 1 persona?

R: **Sì, meglio.**

Per freelancer:
- Sei tu il "Symphony"
- Leggi le issue (priorità)
- Decidi quali task
- Spawna agenti per il lavoro
- Risultato: lavori 3x più veloce

---

# PARTE 10: GLOSSARIO

| Termine | Significa |
|---------|-----------|
| **L1** | Memory Layer — CLAUDE.md |
| **L2** | Knowledge Layer — Skills + CONTEXT.md + ADRs |
| **L3** | Guardrail Layer — Hooks |
| **L4** | Delegation Layer — Subagenti |
| **L5** | Distribution Layer — manifest.json |
| **Snapshot** | Copia immutabile del context per un agente |
| **Proof of Work** | Test log + CI status + PR diff (validazione) |
| **Hook** | Script che si attiva automaticamente su evento |
| **Subagent** | Agente isolato che fa un task specifico |
| **DAG** | Grafo aciclo diretto (dipendenze tra task) |
| **Ubiquitous Language** | Vocabolario comune del dominio |
| **ADR** | Architecture Decision Record (decisione storica) |
| **Collision Point** | Conflitto potenziale tra layer o agenti |

---

**Versione**: v4.0  
**Status**: Production Ready ✅  
**Data**: Maggio 2026  
**Prossimo Update**: Quando usato con vero Symphony runtime  
**Manutenzione**: Monthly review di CONTEXT.md + ADRs

---

## Come Usare Questo Documento

1. **Lettura completa**: Leggi da PARTE 0 a PARTE 3 (comprensione generale)
2. **Setup iniziale**: Segui PARTE 6 (implementation checklist)
3. **Reference operativo**: PARTE 2 + PARTE 4 (workflow integration)
4. **Troubleshooting**: PARTE 5 (collision points)
5. **Comunicazione**: PARTE 7 + PARTE 8 (spiega ai colleghi)

**Bookmark this. È il tuo blueprint definitivo.**

---

EOF
