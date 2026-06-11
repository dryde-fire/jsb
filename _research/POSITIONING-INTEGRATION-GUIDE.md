# INTEGRAZIONE DI POSITIONING.MD NEL WORKFLOW CLAUDE CODE

**Versione**: 1.0  
**Data**: Maggio 2026  
**Oggetto**: Come aggiungere POSITIONING.md nel setup esistente

---

## 🎯 IL PROBLEMA CHE POSITIONING.MD RISOLVE

Nel setup attuale (CLAUDE.md, CONTEXT.md, WORKFLOW.md, ADRs):

| Livello | Cosa dice | Gap |
|---------|----------|-----|
| **CLAUDE.md** | "Comportati così globalmente" | ❌ Non sa come penso IO nel contesto di QUESTO task |
| **CONTEXT.md** | "Il dominio è questo" | ❌ Non sa cosa ho imparato dalle sessioni precedenti |
| **WORKFLOW.md** | "Eseguici così" | ❌ Non sa se sono Architetto o Implementatore qui |
| **ADRs** | "Abbiamo deciso questo" | ❌ Non sa se questo ADR è rilevante per il task attuale |
| **POSITIONING.md** | ✅ "Per QUESTO task, ecco il contesto, qui il mio ruolo, qui il ragionamento" | ✅ RISOLVE TUTTO |

---

## ARCHITETTURA: POSITIONING.MD NELLA GERARCHIA

```
REPOROOT/
  ├── CLAUDE.md                 ← Regole globali di comportamento (~5 min di lettura)
  ├── CONTEXT.md                ← Dominio e linguaggio ubiquitous (~5 min di lettura)
  ├── WORKFLOW.md               ← Protocollo di esecuzione (~5 min di lettura)
  ├── POSITIONING.md            ← Posizionamento GLOBALE per questo progetto (~5 min di lettura)
  │                                [OPZIONALE: se il progetto è stabile]
  │
  └── docs/adr/
      ├── ADR-001-xxx.md
      └── ADR-002-xxx.md

QUANDO INIZI UN TASK SPECIFICO:
  ├── [Task description inviata dal developer]
  └── POSITIONING-[TASK-NAME].md  ← Crei questo per il task specifico
```

---

## TRE LIVELLI DI POSITIONING

### Livello 1: POSITIONING.md Globale (una volta per progetto)

**Dove**: Root cartella del progetto  
**Quando**: Subito dopo CLAUDE.md, CONTEXT.md  
**Che contiene**:
- Memory injection globale (cosa ha imparato Claude sugli ultimi 3 task)
- Anti-pattern frequenti nel progetto
- Architettura implicita del codebase

**Esempio**:
```
repo/
  ├── CLAUDE.md
  ├── CONTEXT.md
  ├── POSITIONING.md  ← globale per il progetto
  └── docs/adr/
```

**Durata**: 20-30 minuti di setup, aggiornare ogni 3-4 task

---

### Livello 2: POSITIONING-[TASK].md (per task grandi)

**Dove**: Nella cartella del task, o in un file markdown condiviso  
**Quando**: Quando il task è > 4 ore di lavoro manuale equivalente  
**Che contiene**:
- Memory injection dal task precedente (se relato)
- Role definition specifico per questo task
- Reasoning constraints per questa fase
- Proof of thinking prima di codare

**Esempio**:
```
repo/
  ├── CLAUDE.md
  ├── CONTEXT.md
  ├── POSITIONING.md
  ├── POSITIONING-auth-oauth.md     ← specifico per task auth
  ├── POSITIONING-payment-flow.md   ← specifico per task payment
  └── docs/adr/
```

**Durata**: 5-10 minuti di setup per task, vale la pena se task è grande

---

### Livello 3: POSITIONING Inline (per task piccoli)

**Dove**: Direttamente nel prompt quando dai il task  
**Quando**: Task < 4 ore, non vale creare file separato  
**Che contiene**: Versione compatta di POSITIONING

**Esempio**:
```
Task: "Correggi il bug in CartForm"

POSITIONING (inline):
- Role: Implementatore
- Patterns da seguire: src/components/UserProfile.tsx ha pattern che applico qui
- Risks: race condition se user clicca 2 volte → disabilita bottone
- Test: "remove item → fetch → item rimosso"
```

**Durata**: 30 secondi, includere direttamente nel prompt del task

---

## IMPLEMENTAZIONE: STEP BY STEP

### Step 1: Aggiungi POSITIONING.md Globale al Setup

Nel **SETUP-DEFINITIVO-v3.0-FOR-DUMMIES.md**, aggiungi:

```markdown
# PARTE 5.5: POSITIONING.md Globale (Opzionale ma Consigliato)

## Quando Crearlo

Dopo aver completato:
- [ ] CLAUDE.md
- [ ] CONTEXT.md
- [ ] WORKFLOW.md
- [ ] docs/adr/ con 2-3 ADR

## Come Crearlo

```powershell
code POSITIONING.md
```

Copia il template da POSITIONING-SECOND-BRAIN-TEMPLATE.md.

Per un progetto nuovo, la sezione MEMORY INJECTION è vuota:

```markdown
## 1. MEMORY INJECTION — Sessions Precedenti

### Cosa Ho Imparato
(Vuoto all'inizio — update dopo ogni 3-4 task)

### Anti-pattern Visti
(Vuoto all'inizio — update man mano scopri errori)

### Architettura Implicita
(Vuoto all'inizio — update man mano scopri pattern)
```

## Quale Aggiornare?

Dopo ogni task completato (o ogni 3-4 task):
- [ ] Update POSITIONING.md con i learning principali
- [ ] Non aggiungere dettagli minori, solo learning importanti
- [ ] Tieni la sezione MEMORY INJECTION sotto 100 righe
```

### Step 2: Aggiungi POSITIONING-[TASK].md per Task Grandi

Nel **WORKFLOW.md**, aggiungi una sezione:

```markdown
## Quando Creare POSITIONING-[TASK].md?

Se il task richiede:
- [ ] Più di 4 ore di lavoro manuale
- [ ] Decisioni architetturali significative
- [ ] Integration con molteplici componenti
- [ ] Context da memoria di sessioni precedenti

Allora crea POSITIONING-[TASK].md prima di iniziare.

## Come Crearlo?

Template minimalista (5-10 minuti):

```markdown
# POSITIONING.md — [NOME TASK]

## Role
[Architetto | Implementatore | Reviewer | Research]

## Memory from Previous Session
[Se relato a task precedente: cosa ho imparato?]

## Constraints
- Test-first? [Sì/No]
- Simplicity? [Sì/No]
- Surgical only? [Sì/No]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
```

Condividi il file con Claude prima di iniziare il task.
```

### Step 3: Integrazione nel Prompt

Quando dai un task a Claude, includi POSITIONING:

```
Task: Implementa autenticazione Google OAuth

[allega POSITIONING-auth-oauth.md oppure scrivi inline]

POSITIONING:
- Role: Architetto (voglio che pensi alle implicazioni lunghe)
- Memory: La sessione scorsa abbiamo imparato che secret deve restare in backend
- Constraints: Test-first, Error-first thinking (pensa a attacchi)
- Success: User può loginare, token in httpOnly, refresh automatico

Inizia dal PROOF OF THINKING prima di codare.
```

---

## GERARCHIA DI CONFLITTO CON POSITIONING

Se ci sono conflitti tra più file di configurazione:

```
1️⃣ POSITIONING-[TASK].md
   (più specifico al task attuale)

2️⃣ POSITIONING.md
   (specifico al progetto, meno specifico del task)

3️⃣ WORKFLOW.md
   (esecuzione globale)

4️⃣ CLAUDE.md
   (comportamenti globali)

5️⃣ CONTEXT.md
   (dominio, non nego mai)

6️⃣ ADRs
   (decisioni storiche, non nego mai)
```

**Regola**: Se POSITIONING-[TASK].md dice "sii Architetto" ma CLAUDE.md dice "sii veloce", vince POSITIONING-[TASK].md (più specifico).

---

## DIMENSIONAMENTO: QUANDO VALE LA PENA

| Sforzo | Beneficio | Vale la pena? |
|--------|-----------|--------------|
| POSITIONING.md globale (setup 20 min) | Evita ripetizione di errori su tutta la sprints | ✅ **SÌ** |
| POSITIONING-[TASK].md per task 4h+ | Evita dilettantismo architetturale, task più veloce | ✅ **SÌ** |
| POSITIONING inline per task <1h | Micro-optimize, contesto subito | ⚠️ **DIPENDE** |
| POSITIONING per bug fix < 30 min | Overhead non vale | ❌ **NO** |

**Metrica concreta**: Se risparmi 30 min di lavoro di Claude (e di conseguenza di developer per review), vale 5 min di overhead.

---

## INTEGRAZIONE CON GIT

### Versionare POSITIONING.md

```bash
# Dopo ogni update di POSITIONING.md
git add POSITIONING.md
git commit -m "chore: update positioning memory (from auth-oauth task learning)"

# La storia dei positioning ti dice l'evoluzione del progetto
git log POSITIONING.md
# Output:
# commit 1: "update positioning memory (from auth-oauth task learning)"
# commit 2: "update positioning memory (from payment-flow task learning)"
# commit 3: "initial POSITIONING setup"
```

### Versionare POSITIONING-[TASK].md

```bash
# Non committare POSITIONING-[TASK].md?
# Opzione 1: Committalo, così hai storia dei task
git add POSITIONING-auth-oauth.md
git commit -m "task: positioning for auth-oauth feature"

# Opzione 2: Non committarlo, lo crei/elimini per task
echo "POSITIONING-*.md" >> .gitignore
```

**Consiglio**: Committali. Servono come "proof of work" di come abbiamo affrontato il task.

---

## TEMPLATE PER UPDATE PERIODICO DI POSITIONING.MD

Ogni 3-4 task completati, update POSITIONING.md globale:

```markdown
## Sessione [N] — [Data]

**Task completati**:
- [Task 1]
- [Task 2]
- [Task 3]

**Learning consolidati**:
- ✅ Pattern [X] funziona bene per [Y]
- ❌ Anti-pattern [A] causa [B] — evitare sempre
- ⚠️ GOTCHA [C] — ricordare che [D]

**Update gerarchia**:
- CLAUDE.md? No (ancora valido)
- CONTEXT.md? No (dominio non è cambiato)
- ADR? Sì, aggiungi ADR-XXX su [decisione presa]
```

Esempio concreto:

```markdown
## Sessione 3 — 20 maggio 2026

**Task completati**:
- Auth Google OAuth
- Payment flow con Stripe
- Refund handling

**Learning consolidati**:
- ✅ Pattern webhook signature validation funziona per Stripe
- ❌ Anti-pattern: assumere webhook idempotent senza check — causa double-charging
- ⚠️ GOTCHA: Stripe webhook timestamp expira in 5 min, oltre rifiuta

**Update gerarchia**:
- ADR-003: "Webhook Idempotency Protocol"
```

---

## METRICHE: COME SAPERE SE POSITIONING FUNZIONA

### Indica che POSITIONING funziona:
- ✅ Stesso errore non viene fatto 2 volte
- ✅ Claude ricorda pattern da sessioni precedenti
- ✅ Sessione è più veloce perché Claude sa il suo ruolo
- ✅ Task è completato senza rework
- ✅ Review è superficiale (Claude ha già pensato a tutto)

### Indica che POSITIONING non funziona:
- ❌ Claude dimentica learning della sessione precedente
- ❌ Claude scrive codice "generico" senza considerare il dominio
- ❌ Stessi errori ricorrono ogni 3 sessioni
- ❌ Claude chiede di nuovo le stesse domande
- ❌ Task richiede rework significativo

**Azione**: Se vedi ❌, significa POSITIONING.md non è aggiornato. Aggiornalo subito.

---

## INTEGRAZIONE FINALE: CHECKLIST

Quando setup POSITIONING per la prima volta:

### Setup Iniziale (30 minuti totali)

- [ ] Letto POSITIONING-SECOND-BRAIN-TEMPLATE.md
- [ ] Capito i 4 componenti (Memory, Role, Constraints, Proof)
- [ ] Creato POSITIONING.md globale (5-10 min di lettura)
- [ ] Aggiunto POSITIONING.md a .gitignore? (Sì/No)
- [ ] Aggiunto POSITIONING.md a Repo.md o README
- [ ] Istruito il team: "Da adesso, per task > 4h, creiamo POSITIONING-[TASK].md"

### Per Ogni Task Successivo (5-10 minuti)

Se task > 4 ore:
- [ ] Creato POSITIONING-[TASK].md prima di iniziare
- [ ] Claude ha letto e ricapitolato il POSITIONING
- [ ] Claude ha fatto il PROOF OF THINKING prima di codare
- [ ] Task completato con meno rework del solito

Se task < 4 ore:
- [ ] Incluso POSITIONING inline nel prompt del task
- [ ] Claude ha capito il role e constraints

### Ogni 3-4 Task (15 minuti)

- [ ] Review POSITIONING.md globale
- [ ] Aggiunto Learning principale alla sezione MEMORY INJECTION
- [ ] Aggiunto Anti-pattern visto alla sezione corrispondente
- [ ] Committato update su git
- [ ] Vecchi learning rimossi (tenere solo i top 5-10)

---

## CONCLUSIONE

**POSITIONING.md trasforma Claude da "strumento singolo per singolo task"** in **"second brain del developer con memoria persistente tra sessioni"**.

Senza POSITIONING:
- Ogni task ricomincia da zero
- Stesso errore viene fatto 3 volte
- No memoria tra sessioni

Con POSITIONING:
- Task ricomincia con contesto della sessione precedente
- Errori vengono evitati perché ricordati
- Claude è veramente un second brain

**Investimento**: 30 minuti setup + 10 minuti per task = risparmio di ore di rework.

---

**Versione**: 1.0 Final  
**Status**: Ready to integrate into SETUP-GUIDE-v3.0  
**Prossimo**: Aggiorna SETUP-GUIDE-v3.0 per includere questa integrazione
