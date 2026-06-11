---
# agentskills.io v1 standard frontmatter
schema_version: "1.0"
name: distill-lesson
version: "1.0.0"
description: |
  Estrae lessons-learned, pattern, e architecture decisions da un progetto Claude
  Code attivo e li scrive nell'inbox del Second Brain personale, dove Ollama li
  elaborerà nightly. Attiva quando l'utente chiede: "salva questa lezione nel
  vault", "questo è un pattern che voglio ricordare", "estraine una lesson", o
  alla fine di una feature significativa quando l'utente conferma. NON attivare
  automaticamente senza conferma esplicita: scrivere rumore nel vault è peggio
  di non scrivere nulla.
license: MIT
author: sandr
compatible_agents:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - hermes-agent
required_tools:
  - filesystem-read
  - filesystem-write
config_dependencies:
  - path: "~/.jsb-config.json"
    field: "vault_path"
    required: true
  - path: "~/.jsb-config.json"
    field: "bridge.enabled"
    required: true
    expected_value: true
---

# Skill: /distill-lesson — Salvataggio strutturato nel Second Brain

## Scopo

Questa skill è il complemento di `/recall`: dove `/recall` legge dal vault,
`/distill-lesson` ci scrive. Permette al lavoro fatto in un progetto Claude Code
di diventare memoria persistente, recuperabile da tutti i progetti futuri.

## Principio fondante: meglio non scrivere che scrivere male

Il valore del Second Brain dipende dal **rapporto segnale/rumore**. Scrivere
ogni piccola scelta tecnica diluisce il valore di ricerche future. Per questo:

- Una lesson va estratta solo per cose **non ovvie**
- Una decision va estratta solo per scelte **con alternative reali considerate**
- Un pattern va estratto solo se **applicabile in più contesti**

Prima di scrivere, fai il *quality check* (sotto). Se non passa, **non scrivere**.

## Tre tipi di output

### 1. `type: lesson-learned`
Per intuizioni emerse durante l'implementazione.

Esempio: "Validare la firma del webhook Stripe lato server, non lato client.
Ho perso 2h debuggando perché la mia validazione client-side era inutile."

### 2. `type: architecture-decision`
Per decisioni con alternative pesate.

Esempio: "Scelto Zustand su Redux per state management. Considerato Recoil
(scartato: meno community), MobX (scartato: complessità)."

### 3. `type: project-pattern`
Per soluzioni riutilizzabili in altri progetti.

Esempio: "State machine per ordini con stato monotono crescente
(Pending → Paid → Shipped → Delivered, mai retro). Previene refund abuse."

## Workflow

### Step 1: Trigger e bozza

L'utente dice: "Salva questa lezione". Tu produci una bozza con questo schema:

```markdown
---
type: lesson-learned        # o architecture-decision, project-pattern
created: 2026-05-09
source_project: ecommerce-stripe
tags: [stripe, webhook, security, validation]
status: inbox
priority: normal             # high → trigger model_quality nell'elaborazione
---

# [Titolo conciso, max 60 caratteri]

## Context
[Il problema o la situazione in 2-4 righe]

## Insight
[Cosa è stato imparato, in 3-6 righe]

## Generalizable
[Quando questo si applica anche fuori da questo progetto. Se non si applica
fuori, valuta se vale davvero la pena scriverlo.]

## Anti-pattern (opzionale)
[Cosa NON fare, se rilevante]
```

### Step 2: Quality check (5 domande)

Prima di chiedere conferma all'utente, valuta tu stesso:

1. **È non-ovvio?** Se la lesson è "ricordati di testare il codice", scarta.
2. **È specifico?** Vago = inutile. "Gestire errori" non aiuta nessuno.
3. **Ha contesto?** Senza il problema, la lezione non è recuperabile.
4. **È generalizzabile?** Se è hyper-specifico al progetto, valuta se vale.
5. **Esiste già nel vault?** Esegui `/recall` prima per verificare.

Se 3 delle 5 sono insufficienti, dì all'utente:

> Questa nota mi sembra borderline ([motivo]). La salvo lo stesso?

### Step 3: Path di destinazione

```python
import json, os
from pathlib import Path
from datetime import date

cfg = json.loads((Path(os.environ.get("JSB_CONFIG") or Path.home() / ".jsb-config.json")).read_text(encoding="utf-8"))
vault = Path(cfg["vault_path"])

# Inbox/notes/ è la destinazione per tutti e 3 i tipi
target_dir = vault / "inbox" / "notes"

# Filename: YYYY-MM-DD_<type>_<slug>.md
slug = make_slug(title)  # vedi ingest.py per la convenzione
filename = f"{date.today().isoformat()}_{file_type}_{slug}.md"
target = target_dir / filename
```

### Step 4: Conferma e scrittura

Mostra il file completo all'utente. Domanda:

> Salvo in `[path]`? Sarà elaborato nightly da Ollama nel vault personale.
> [Y/n/edit]

- `Y` → scrivi
- `n` → scarta
- `edit` → permetti modifiche prima di scrivere

### Step 5: Trigger automatico per ADR

Se il progetto ha `docs/adr/ADR-NNN-*.md` nuovi (rilevati via git status), e
in `.jsb-config.json` `bridge.auto_distill_on_adr = true`, **proponi all'utente**
di distillarli.

```
Ho rilevato un nuovo ADR: docs/adr/ADR-005-event-sourcing.md
Vuoi che lo salvi anche nel Second Brain (con tag generalizable_pattern)? [Y/n]
```

Anche con `auto_distill_on_adr = true`, non scrivere mai senza conferma utente.
"Auto" significa "ti propongo automaticamente", non "scrivo automaticamente".

## Convenzione tag (importante per /recall futuro)

Tag obbligatori:
- `tags: [<dominio>]` — es. `ecommerce`, `auth`, `db`, `frontend`
- `tags: [<tech>]` — es. `typescript`, `postgres`, `stripe`, `react`
- `tags: [<categoria>]` — es. `security`, `performance`, `testing`

Più ricco è il tagging, più potente sarà il `/recall` futuro.

## Gotchas

**Non scrivere lesson quando il progetto è ancora in flux.** Se la decisione
potrebbe essere ribaltata domani, aspetta che si stabilizzi.

**Non duplicare il README del progetto.** Se sta nel README, non sta nel vault.
Il vault è per cose che vuoi ricordare *al di là* di questo progetto.

**Non includere segreti.** Mai tag con API keys, password, hostname interni.
Verifica prima di scrivere.

**Frontmatter rispetta lo schema atteso da ingest.py.** Se aggiungi campi nuovi,
controlla che `ingest.py` (in scripts/python/) li gestisca, altrimenti vengono
scartati nell'output wiki.
