# STATE.md — Session State & Context Rot Prevention
# Managed by: get-shit-done (GSD) + manual maintenance
# Read by: Every agent at session start
# Updated by: Agent at session end OR at each phase transition

<session_metadata>
## Session Info
- Task ID: [TICKET-ID]
- Session started: [YYYY-MM-DD HH:MM]
- Session N (of this task): [N]
- Context usage at last save: [X%]
- Agent model: [claude-sonnet-4-6]
- Workflow phase: [BRAINSTORM|PLAN|VALIDATE|TDD|PROOF|SHIP]
</session_metadata>

<current_task>
## Task Corrente
- Obiettivo: [descrizione una riga]
- Criterio di successo: [verificabile, non vago]
- Scope dichiarato: [lista file che VERRANNO modificati]
- Scope escluso: [cosa NON verrà toccato — esplicito]
- Deadline: [data o "none"]
</current_task>

<decisions_made>
## Decisioni Prese (questa sessione)
<!-- Aggiornare ogni volta che viene presa una decisione non banale -->
<!-- Formato: [timestamp] — [decisione] — [rationale in una riga] -->

- [YYYY-MM-DD HH:MM] — [Decisione A] — [Perché]
- [YYYY-MM-DD HH:MM] — [Decisione B] — [Perché]
</decisions_made>

<plan_status>
## Piano di Esecuzione — Status
<!-- Aggiornare dopo ogni step completato -->

| Step | Descrizione | Status | Test | Commit |
|------|-------------|--------|------|--------|
| 1 | [descrizione] | ✅ done / 🔄 in progress / ⏳ pending | [test name] | [hash] |
| 2 | [descrizione] | ⏳ pending | - | - |
| 3 | [descrizione] | ⏳ pending | - | - |
</plan_status>

<blockers>
## Blockers Attivi
<!-- Se vuoto: scrivere "none" — non lasciare questa sezione vuota -->

- none
</blockers>

<context_snapshot_used>
## Context Snapshot di Questa Sessione
<!-- Documenta cosa è stato fornito all'agente — per audit e reproducibilità -->

- repomix snapshot: [nome file / "none"]
- CONTEXT.md version: [hash git o data]
- ADR inclusi: [lista ID o "none"]
- Context fresco o continuato: [fresh|continued from session N-1]
</context_snapshot_used>

<phase_transitions>
## Transizioni di Fase (Context Rot Prevention)

### Regole GSD per le transizioni
Ogni transizione di fase DEVE:
1. Salvare STATE.md con phase aggiornata
2. Eseguire /compact se context > 50%
3. Iniettare solo i file rilevanti per la NUOVA fase (non tutti)
4. Documentare le decisioni prese nella fase uscente

### Transizioni e Context Injection
```
BRAINSTORM → PLAN:
  Mantieni: task description, assunzioni, domande risolte
  Scarica: storia esplorazione codebase
  Inietta: piano vuoto da compilare

PLAN → VALIDATE:
  Mantieni: piano tecnico completo
  Scarica: conversazione di brainstorming
  Inietta: ADR rilevanti per validazione

VALIDATE → TDD:
  Mantieni: piano validato, lista test da scrivere
  Scarica: conversazione di validazione
  Inietta: file specifici del primo step (NON tutto il repo)

TDD step N → TDD step N+1:
  Mantieni: test passanti del step N, piano rimanente
  Scarica: conversazione del step N (già committata)
  Inietta: file specifici del step N+1

TDD → PROOF:
  Mantieni: lista test totali, coverage, commit hashes
  Scarica: tutto il codice (già committato)
  Inietta: template proof_of_work XML
```
</phase_transitions>

<session_handoff>
## Handoff alla Sessione Successiva
<!-- Compilare ALLA FINE di ogni sessione, prima di chiudere -->

### Dove mi sono fermato
[Frase che descrive l'esatto punto di interruzione]

### Prossima azione (specifica, non vaga)
[Prima cosa che il prossimo agente/sessione deve fare]

### Decisioni da prendere ancora
[Lista o "none"]

### Warning per la prossima sessione
[Gotcha, dipendenze, cose non ovvie — o "none"]

### Context necessario per riprendere
```bash
# Comandi da eseguire per riprendere questa sessione
git checkout feature/[ticket-id]-descrizione
git log --oneline -5   # verifica dove siamo
npm run test           # verifica stato test
cat STATE.md           # rileggi questo file
```
</session_handoff>
