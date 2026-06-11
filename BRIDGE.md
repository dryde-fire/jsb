# BRIDGE — Integrazione Second Brain ↔ Claude Code

Questo documento definisce **come i due sistemi dialogano**. Senza questo
documento, "unire i due sistemi" è un'intenzione vaga; con questo documento, è
un'architettura.

## Principi

1. **Lettura-scrittura asimmetrica**. Claude Code legge dal vault tutte le volte
   che vuole, ma scrive **solo con conferma utente** (anche conclaudeclau
   `auto_distill_on_adr=true`, "auto" significa "te lo propongo automaticamente",
   non "lo scrivo automaticamente").

2. **Disaccoppiamento via filesystem**. Niente API, niente HTTP fra i due
   sistemi. Il punto di contatto è la cartella `inbox/notes/` del vault. Claude
   Code ci scrive, Ollama la elabora indipendentemente. Se un sistema cade,
   l'altro continua a funzionare.

3. **Configurazione centralizzata**. Path del vault, modelli Ollama, flag del
   bridge — tutto in `~/.jsb-config.json`. Nessun hardcoded path negli script o
   nelle skill.

4. **Quality over volume**. Meglio 50 lessons-learned ben scritte che 500 note
   rumorose. La skill `/distill-lesson` ha un quality check di 5 domande.

## Il flusso (sequenza completa)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Inizio progetto Claude Code                                   │
│  └─> Utente: "Cerca progetti simili"                           │
│      └─> Skill /recall                                         │
│          └─> Legge ~/.jsb-config.json → vault_path             │
│              └─> rg in vault/wiki/{projects,decisions,learn}   │
│                  └─> Filtra per status, version, recency       │
│                      └─> Top 5 risultati a utente              │
│                          └─> Utente sceglie cosa includere     │
│                              └─> Inserito in CONTEXT.md        │
│                                                                 │
│  Sviluppo feature (con CONTEXT.md arricchito)                  │
│  └─> Decisione architetturale presa                            │
│      └─> Scritto ADR in docs/adr/ADR-NNN-*.md                  │
│          └─> Hook PostToolUse rileva nuovo ADR                 │
│              └─> Propone /distill-lesson all'utente            │
│                  └─> Utente conferma → scrive in vault inbox/  │
│                                                                 │
│  Notte (nightly)                                                │
│  └─> Office PC: Task Scheduler 00:00                           │
│      └─> Ingest-Orchestrator.ps1                               │
│          └─> Tenta WoL laptop                                  │
│              ├─> Laptop online → SSH → watchdog.py su laptop   │
│              │   └─> Elabora con E2B (veloce)                  │
│              └─> Laptop offline → watchdog.py locale           │
│                  └─> Elabora con E4B (qualità)                 │
│                  └─> Output in vault/wiki/                     │
│                                                                 │
│  Mattina dopo                                                   │
│  └─> Sync S3 → tutti i PC vedono il nuovo wiki/                │
│      └─> Prossimo /recall trova anche il file appena scritto   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Schema frontmatter per il bridge

I file scritti da Claude Code nel vault hanno frontmatter standard più
estensioni specifiche del bridge:

```yaml
---
# Standard (riconosciuto da ingest.py)
type: lesson-learned | architecture-decision | project-pattern
created: 2026-05-09
status: inbox
version: 1
priority: normal               # 'high' attiva model_quality

# Tag (importanti per /recall futuro)
tags: [<dominio>, <tech>, <categoria>]

# Estensioni del bridge
source_project: ecommerce-stripe-2026
source_path: docs/adr/ADR-005-event-sourcing.md
source_commit: abc123def
generalizable_pattern: true    # se applicabile a progetti diversi
---
```

## Convenzione tag (critica per ricerca)

Tre dimensioni obbligatorie:

| Dimensione | Esempi |
|------------|--------|
| Dominio | `ecommerce`, `auth`, `cms`, `analytics`, `iot` |
| Tech | `typescript`, `postgres`, `stripe`, `react`, `python` |
| Categoria | `security`, `performance`, `testing`, `deployment`, `architecture` |

Una nota tipica avrà 4-7 tag complessivi.

**Anti-pattern**: tag vaghi come `interesting`, `important`, `todo`. Inutili
per ricerche future.

## Hook automatico per ADR (Claude Code → Vault)

Configurato in `.claude/hooks/PostToolUse.sh` di ogni progetto Claude Code che
abilita il bridge:

```bash
#!/bin/bash
# Hook: dopo creazione/modifica di un ADR, suggerisci /distill-lesson

# Leggi config bridge
JSB_CONFIG="${JSB_CONFIG:-$HOME/.jsb-config.json}"
if [ ! -f "$JSB_CONFIG" ]; then exit 0; fi

# Estrai flag bridge.auto_distill_on_adr
AUTO_DISTILL=$(jq -r '.bridge.auto_distill_on_adr // false' "$JSB_CONFIG")
if [ "$AUTO_DISTILL" != "true" ]; then exit 0; fi

# Se l'ultimo file modificato è un ADR
LAST_FILE="$1"
if [[ "$LAST_FILE" =~ docs/adr/ADR-[0-9]+.*\.md$ ]]; then
  echo ""
  echo "💡 ADR rilevato: $LAST_FILE"
  echo "   Vuoi distillarlo nel Second Brain? Esegui: /distill-lesson"
  echo ""
fi
```

L'hook **suggerisce**, non scrive. La scrittura passa sempre dalla skill
`/distill-lesson` con conferma utente esplicita.

## Cosa il bridge NON fa (deliberatamente)

**Non sincronizza in tempo reale.** Le note scritte in `inbox/` arrivano nel
`wiki/` solo dopo il run nightly di Ollama. Per quel momento il sync S3 le ha
già propagate sui 3 PC, ma il file *elaborato* (in `wiki/`) è disponibile solo
il giorno dopo. Questo è **un design choice**: il delay forza un quality check
mentale ("se domani ti pentirai di averlo scritto, è il momento di pulire
l'inbox").

**Non fa semantic search.** La skill `/recall` usa full-text ricerca con
ripgrep. Per fare ricerca per significato (vector search) serve LightRAG, che
è in **Fase 2 della roadmap**. Per ora, la qualità del tagging è ciò che
determina la qualità del retrieval.

**Non modifica file in `wiki/`.** La skill `/distill-lesson` scrive solo in
`inbox/notes/`. Le elaborazioni esistenti in `wiki/` sono immutabili lato
Claude Code (puoi modificarle a mano in Obsidian, ma il bridge non le tocca).

**Non importa progetti automaticamente.** Quando inizi un progetto Claude
Code, **tu** decidi se attivare `/recall`. Non c'è un'inclusione automatica.
Questo evita il rumore di reference irrilevanti.

## Casi d'uso concreti

### Caso 1: Decisione ricorrente

Stai per scegliere fra PostgreSQL e MongoDB per un nuovo progetto. Sai che
l'hai già fatto in passato.

```
Tu: Cerca nel vault le mie decisioni sui database
[Claude esegue /recall]
Claude: Ho trovato 2 ADR rilevanti:
  - wiki/decisions/postgres-vs-mongo-2025-11.md
    "Scelto Postgres per ACID. Considerato Mongo, scartato..."
  - wiki/decisions/mongo-for-content-2024-08.md
    "Scelto Mongo per CMS. Schema flessibile prevale su transazioni..."
```

Risultato: non rifai l'analisi da zero, parti dalle conclusioni passate e le
adatti al contesto nuovo.

### Caso 2: Pattern emerso

Hai appena risolto un bug subdolo: il webhook Stripe veniva validato lato
client. Lo vuoi ricordare per sempre.

```
Tu: Ho imparato qualcosa di importante. Salvalo nel vault.
[Claude esegue /distill-lesson]
Claude: Ti propongo:
  type: lesson-learned
  tags: [stripe, webhook, security, validation]
  ## Insight
  Validare la firma del webhook Stripe DEVE essere lato server.
  Validazione client-side è bypassabile e quindi inutile.
  ## Generalizable
  Vale per tutti i webhook con firma (Stripe, GitHub, Slack, etc.)
  
  Salvo in JSB/inbox/notes/2026-05-09_lesson-learned_stripe-webhook-server-validation.md ?
```

Tre mesi dopo, in un nuovo progetto, `/recall` su keyword "webhook" lo trova.

### Caso 3: Meta-pattern fra progetti

Hai notato che 3 dei tuoi ultimi progetti usano la stessa state machine per
ordini. È un pattern.

```
Tu: Estrai il pattern delle state machine ordini come project-pattern
[Claude esegue /distill-lesson con type: project-pattern]
Claude: Ti propongo:
  type: project-pattern
  tags: [state-machine, ecommerce, ordering, pattern]
  ## Pattern Name
  Monotone Order State Machine
  ## Problem Solved
  Prevenire stati inconsistenti, retroattivi, o duplicate transitions
  ## Solution Sketch
  Stati: Pending → Paid → Shipped → Delivered. Mai retro.
  Una transition richiede event + invariant check.
  ...
```

Diventa una pagina di riferimento per tutti i progetti futuri.

## Failure modes e mitigazioni

| Cosa può andare storto | Cosa succede | Mitigazione |
|------------------------|--------------|-------------|
| Vault non sincronizzato | `/recall` cerca in versione vecchia | Healthcheck rileva età sync, segnala |
| Ollama non gira nightly | File restano in `inbox/`, non elaborati | Healthcheck segnala "ultimo run > 36h" |
| Utente scrive note rumorose | `/recall` futuro restituisce risultati irrilevanti | Quality check in `/distill-lesson` (5 domande) |
| Conflitto sync (Personal e Office editano stesso file) | Last-write-wins di S3 | Convenzione: solo Office scrive in `wiki/`, Personal scrive solo in `inbox/` |
| Skill `/recall` non trova nulla | Vuoto restituito | Skill mostra "Nessun match" e suggerisce di rifare ricerca con keyword diverse |
| File in `inbox/_failed/` | Nessuno se ne accorge | Healthcheck li elenca con severità=critical |

## Manutenzione del bridge

**Settimanale**: `python healthcheck.py` da Office PC.

**Mensile**: review manuale di `wiki/`. Sposta in `archive/` ciò che è
obsoleto. Sistema tag inconsistenti.

**Trimestrale**: review della convenzione tag. Se 80% delle note ha tag in 3
dimensioni, OK. Se molte note hanno solo 1 tag, qualcosa nel quality check di
`/distill-lesson` non funziona.

## Hermes Integration Path (Fase 3, opzionale)

Quando arriverai alla Fase 3 (Q3 2026 o oltre), Hermes Agent può integrarsi nel
sistema **senza modificare il vault** né riscrivere il codice esistente. Diventa
un **terzo modo di interagire** con il Second Brain.

### Come si inserisce

```
Telegram/Discord/CLI (input)
      ↓
Hermes Agent (su Office PC, dentro WSL2)
├─ Modello: Claude API (con tua chiave) o Ollama o entrambi
├─ Skills: importate da ~/.claude/skills/* (formato agentskills.io)
├─ Memoria FTS5: storia chat persistente
└─ Vault access: /mnt/c/Users/MS-Sandro/JSB (montato da WSL2)
      ↓
Vault Obsidian (immutato)
      ↓
Sync S3 (immutato) → tutti i 3 PC
```

Il bridge `/recall` e `/distill-lesson` continua a funzionare con Claude Code
**in parallelo**. Hermes aggiunge un canale, non sostituisce niente.

### Perché ha senso (e quando NON ha senso)

**Ha senso se**:
- Vuoi parlare col tuo Second Brain dal telefono via Telegram
- Vuoi che Hermes ricordi conversazioni precedenti senza che ricarichi context ogni volta
- Vuoi un agent che lavori in background (cron Hermes per sintesi settimanali, briefing)
- Vuoi memoria long-term oltre alle skill statiche

**Non ha senso se**:
- Lavori esclusivamente da PC e Claude Code ti basta
- Ti spaventa il setup WSL2 e l'idea di un altro CLI
- Non vuoi un'altra dipendenza da mantenere

### Cosa cambia per il bridge

Niente di sostanziale. Le skill `/recall` e `/distill-lesson` sono già
agentskills.io-compatible, quindi:

```bash
# Importazione skill in Hermes (un solo comando)
cp -r ~/.claude/skills/recall ~/.hermes/skills/recall
cp -r ~/.claude/skills/distill-lesson ~/.hermes/skills/distill-lesson
hermes skills reload
```

Hermes rispetta `~/.jsb-config.json` come Claude Code (legge `JSB_CONFIG` env).
Stesso vault, stessa convenzione di tag, stessa logica.

### Cosa Hermes aggiunge che il bridge attuale non ha

1. **Memoria conversazionale persistente**: ricordi conversazioni di settimane fa.
2. **Skill auto-create**: quando esegue task complessi (5+ tool calls), Hermes
   genera autonomamente nuove skill che salva in `~/.hermes/skills/`. Tu puoi
   poi promuoverle a skill condivise (Claude Code, Codex, ecc) se utili.
3. **Curator background**: un task ausiliario che consolida skill ridondanti,
   archivia stale entries. Risolve il problema "rumore nel vault" che
   `/distill-lesson` mitiga manualmente.
4. **Multi-platform gateway**: Telegram, Discord, Slack, WhatsApp dal telefono.

### Costo computazionale

Hermes è un processo systemd o background task che gira sull'Office PC. Il
processo Hermes **vuoto** (idle) consuma ~200 MB RAM. Quando esegue task, può
arrivare a ~500 MB-1 GB se usa Ollama in parallelo. Compatibile con i 16 GB
dell'Office PC, ma richiede attenzione se aggiungi anche Gemma 4 E4B (3.5 GB).

### Decisione: aspetta

Per ora **non integrare Hermes**. Aspetta:
1. Che la Fase 1 sia stabile (1-2 mesi di uso reale)
2. Che senti davvero il bisogno della "voce parlante" dal telefono
3. Che `agentskills.io` come standard sia consolidato (sembra di sì, ma vale
   un check fra 3 mesi)

Se a Q3 2026 questi 3 fattori sono allineati, integri Hermes in un weekend.
Se no, salti la Fase 3 e va bene così.

## Roadmap

**Fase 1** (ora, fine Maggio 2026): full-text ricerca via ripgrep. Funziona,
niente dipendenze esterne. Sufficiente per `<5000` note ben taggate.

**Fase 2** (Giugno-Luglio 2026, opzionale): FTS5/SQLite per ranking
intelligente. Modulo `vault_search.py` aggiunto. Skill `/recall` switcha
automaticamente al backend disponibile. Niente WSL2, niente nuove dipendenze
pesanti.

**Fase 3** (Q3 2026, opzionale): Hermes Agent come voce parlante. Vedi sezione
"Hermes Integration Path" sopra.

**Fase 4** (futuro): cross-LLM completo. Le skill sono già agentskills.io,
funzioneranno con Codex, Cursor, Gemini CLI. Vedi `CROSS-LLM-COMPAT.md`.
