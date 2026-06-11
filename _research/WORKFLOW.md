# WORKFLOW.md — Agent Execution Contract
# Authority Level: ORCHESTRATION POLICY
# Override by: Hooks > Pre-commit > this file
# Overrides: CLAUDE.md (in case of conflict, this file wins)

<mandatory_reading>
## READ BEFORE STARTING ANY TASK

Un agente che inizia a scrivere codice senza aver letto questo file
sta violando il contratto di esecuzione. STOP. Leggi tutto.

Ordine obbligatorio di lettura contestuale:
1. Questo file (WORKFLOW.md) — contratto di esecuzione
2. CONTEXT.md — linguaggio del dominio e regole di business
3. ADR rilevanti in docs/adr/ (filtrati per categoria del task)
4. CLAUDE.md — regole operative e comandi
5. Task description specifica assegnata dall'orchestratore
</mandatory_reading>

<execution_methodology>
## Metodologia: Superpowers Cycle

La metodologia è NON OPZIONALE. Ogni task segue questo ciclo.
Saltare una fase non è ottimizzazione — è deficit di processo.

```
BRAINSTORM → PLAN → VALIDATE → TDD → PROOF → SHIP
```

### Fase 1 — BRAINSTORM
**Trigger:** Ricezione del task dall'orchestratore
**Obiettivo:** Capire il problema prima di risolvere qualsiasi cosa
**Tool:** Lettura CONTEXT.md + ADR rilevanti + repomix snapshot

Domande obbligatorie da porsi:
- Quale comportamento del sistema sto modificando?
- Quali ADR esistenti sono rilevanti per questo task?
- Ci sono dipendenze non dichiarate esplicitamente?
- Qual è il criterio di successo verificabile?

**Output:** Lista di assunzioni esplicite + domande aperte (se presenti)

---

### Fase 2 — PLAN
**Trigger:** Assunzioni chiarite, domande aperte risolte
**Obiettivo:** Piano tecnico con zero ambiguità
**Tool:** /grill-me skill (se task ambiguo) → /to-prd skill → Plan Mode (Shift+Tab x2)

Regola: Se dopo /grill-me rimangono branch decisionali aperti,
NON passare alla fase successiva. Risolvi l'ambiguità.

**Output:** Piano tecnico approvato con:
- Step sequenziali con dipendenze esplicite
- Criterio di successo per ogni step
- File che verranno modificati (scope dichiarato)
- Test da scrivere (lista, non codice ancora)

---

### Fase 3 — VALIDATE
**Trigger:** Piano tecnico completo
**Obiettivo:** Validazione sistematica delle decisioni
**Tool:** /grill-me skill (seconda passata sul piano, non sul problema)

Checklist di validazione:
- [ ] Il piano rispetta gli ADR esistenti?
- [ ] Ogni step è indipendentemente testabile?
- [ ] Lo scope è minimo (Karpathy P2 — Simplicity First)?
- [ ] Ci sono edge case non coperti?
- [ ] Il piano crea nuovo debito tecnico? Se sì, è dichiarato?

**Output:** Piano validato o piano rivisto

---

### Fase 4 — TDD (RED → GREEN → REFACTOR)
**Trigger:** Piano validato e approvato
**Obiettivo:** Implementazione con proof of correctness integrato
**Tool:** /tdd skill (anthropics/skills)

**CICLO OBBLIGATORIO per ogni step del piano:**

```
RED:
  1. Scrivi il test che descrive il comportamento atteso
  2. Verifica che il test FALLISCE (se passa subito, il test è sbagliato)
  3. Commit: "test: [descrizione] — RED"

GREEN:
  1. Scrivi il codice MINIMO per far passare il test
  2. Nessuna ottimizzazione, nessuna astrazione prematura
  3. Verifica che il test PASSA
  4. Commit: "feat: [descrizione] — GREEN"

REFACTOR:
  1. Migliora il codice mantenendo i test verdi
  2. Applica Karpathy P2 (Simplicity) e P3 (Surgical)
  3. Verifica che i test passano ancora
  4. Commit: "refactor: [descrizione] — CLEAN"
```

**CRITICO:** Il commit history DEVE mostrare questo pattern.
Il pre-push hook valida l'ordine RED→GREEN→REFACTOR come proof of work.
Un agente che scrive il codice PRIMA del test sta producendo TDD falso.

---

### Fase 5 — PROOF
**Trigger:** Implementazione completata
**Obiettivo:** Assemblare proof of work verificabile per l'orchestratore
**Tool:** /triage-issue skill (se bug) + test runner

Proof of Work richiesto:
```xml
<proof_of_work>
  <task_id>[TICKET-ID]</task_id>
  <status>complete|partial|blocked</status>
  <tests>
    <total>[N]</total>
    <passing>[N]</passing>
    <coverage_delta>[+/-X%]</coverage_delta>
  </tests>
  <commit_history_valid>true|false</commit_history_valid>
  <adr_updated>true|false|not_required</adr_updated>
  <context_usage_at_completion>[X%]</context_usage_at_completion>
  <blockers>[lista o "none"]</blockers>
</proof_of_work>
```

Se context_usage_at_completion > 70%: segnalare obbligatoriamente.
Se > 85%: il proof of work potrebbe essere inaffidabile — dichiararlo.

---

### Fase 6 — SHIP
**Trigger:** Proof of work assemblato e valido
**Obiettivo:** PR pulita e pronta per merge
**Tool:** git + pre-push hook (automatico)

```bash
git push origin feature/[ticket-id]-descrizione
# Il pre-push hook esegue automaticamente la validazione
# Vedi .husky/pre-push per la logica completa
```

**PR Description Template:**
```markdown
## Task
[TICKET-ID] — [descrizione una riga]

## Cambio
[Cosa fa questo PR — comportamento, non implementazione]

## Test
- N test aggiunti
- Coverage: [prima] → [dopo]
- Test suite: verde ✅

## ADR
- [ ] Nessuna decisione architetturale richiesta
- [ ] ADR-NNN aggiornato/creato

## Proof of Work
[incollare XML proof_of_work]
```
</execution_methodology>

<skills_registry>
## Skills Disponibili — Anthropic Official + Community

### Planning Skills (usa PRIMA di scrivere codice)
```
/grill-me                   → Valida decisioni, forza risoluzione edge case
/to-prd                     → Sintetizza conversazione in PRD formale
/to-issues                  → Break PRD in vertical slices (DAG-ready)
/request-refactor-plan      → Interview-driven refactor con tiny commits
/design-an-interface        → Genera design paralleli via sub-agent
```

### Development Skills (usa DURANTE implementazione)
```
/tdd                        → Red-Green-Refactor loop guidato
/triage-issue               → Bug investigation + root cause + fix plan
/improve-codebase-architecture → Analisi con CONTEXT.md + ADR integration
```

### Document Skills — Anthropic Official
```
/docx                       → Manipolazione file Word
/pdf                        → Creazione/lettura/merge PDF
/pptx                       → Presentazioni PowerPoint
/xlsx                       → Spreadsheet e modelli finanziari
/webapp-testing             → Testing Playwright end-to-end
```

### Safety Skills (configura PRIMA di tutto il resto)
```
/setup-pre-commit           → Husky + lint-staged (eseguire una volta)
/git-guardrails-claude-code → Block git push --force e comandi distruttivi
```

### Knowledge Skills
```
/ubiquitous-language        → Estrae glossario DDD → aggiorna CONTEXT.md
/write-a-skill              → Crea nuove skill production-ready
```

### Context Management Skills
```
repomix                     → Snapshot repo (vedi CLAUDE.md per comandi)
/compact                    → Comprimi context al 50% utilizzo
/clear                      → Reset completo (cambio task radicale)
/rewind                     → Torna a checkpoint (dopo 2 fallimenti)
```
</skills_registry>

<context_management_rules>
## Regole Context Management — NON ADVISORY, OPERATIVE

### Soglie di intervento
```
< 50% utilizzo:   Continua normalmente
50-70% utilizzo:  Esegui /compact manualmente PRIMA di continuare
> 70% utilizzo:   Considera /clear + richiedi nuovo snapshot a orchestratore
> 85% utilizzo:   STOP — sei nella "dumb zone" — segnala all'orchestratore
```

### Regola dei 2 Tentativi
```
Tentativo 1 fallisce:   Cambia approccio, stesso thread, usa /rewind
Tentativo 2 fallisce:   STOP — non continuare — escalate all'orchestratore
                         NON fare il terzo tentativo da solo
```

### Isolamento per Subagente
Ogni subagente che spawni deve avere:
- ✅ repomix snapshot filtrato per il SUO dominio
- ✅ CONTEXT.md
- ✅ ADR con categories rilevanti (non tutti)
- ✅ Task description specifica
- ❌ NON: history della tua sessione corrente
- ❌ NON: output di altri agenti paralleli in corso
</context_management_rules>

<escalation_policy>
## Escalation Policy

```
Livello 1 — Auto-recovery (agente):
  - Hook failure → auto-fix (max 2 tentativi)
  - Test failure → debug + fix (max 2 approcci diversi)
  - Context alto → /compact o /clear

Livello 2 — Escalate all'orchestratore:
  - 2 auto-recovery falliti senza fix
  - Context > 85% con task incompleto
  - Decisione architettural non coperta da ADR esistente
  - Dipendenza su task di un altro agente non completato

Livello 3 — Escalate all'umano (OBBLIGATORIO):
  - Creazione o modifica di ADR
  - Decisione che cambia comportamento di produzione
  - Qualsiasi operazione irreversibile non prevista dal piano
  - 3 tentativi falliti su un singolo task
```
</escalation_policy>
