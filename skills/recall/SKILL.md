---
schema_version: "1.0"
name: recall
version: "3.0.0"
description: |
  Cerca nel Second Brain personale (wiki/ del vault Obsidian) con ripgrep,
  seguendo i [[link]] fra note. Attiva quando l'utente chiede:
  "abbiamo già fatto qualcosa di simile?", "cerca nel mio vault", "ricerca
  progetti passati", "ho già preso questa decisione?", "ricordami come avevo
  risolto X". NON attivare per ricerche web o ricerche solo nel codebase corrente.
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
  - shell-exec
config_dependencies:
  - path: "~/.jsb-config.json"
    field: "vault_path"
    required: true
---

# Skill: /recall — Ricerca nel Second Brain

Niente server, niente indice: il vault è markdown locale, lo leggi direttamente.
La "ricerca per significato" la fai tu: espandi la query in sinonimi e segui i link.

## Step 1: Trova il vault

Leggi `vault_path` da `$JSB_CONFIG` o `~/.jsb-config.json`. Cerca in `<vault>/wiki/`.

## Step 2: Espandi la query in keyword

Trasforma la domanda in 3-6 termini alternativi, italiano e inglese.
Es. "decisioni sui database" → `database|postgres|mongo|storage|persistenza|schema`

## Step 3: Cerca

```bash
rg -i -l "database|postgres|mongo|storage|persistenza" "<vault>/wiki/"   # quali file
rg -i -C 2 "<termine>" "<vault>/wiki/<file>.md"                        # contesto
rg -i "^tags:.*<termine>" "<vault>/wiki/"                              # per tag nel frontmatter
```

Se pochi risultati, allarga ai sinonimi o cerca anche in `<vault>/inbox/`
(note non ancora elaborate: segnalalo all'utente).

## Step 4: Segui i link

Nei file trovati, leggi i `[[link]]` e apri le note collegate se pertinenti.
Un livello di profondità basta.

## Step 5: Filtra e presenta (max 5 file)

1. Scarta file con `status: archived` nel frontmatter
2. Ordina per `version` desc, poi `date_elaborated` desc
3. Mostra max 5 file distinti

Formato per ogni file:

    📄 wiki/decisions/postgres-vs-mongo-2025-11.md
       tags: [database, decision, ecommerce]
       version: 2 · elaborated: 2025-11-15
       "2-3 righe del contenuto più rilevante"

Concludi con:
"Vuoi che includa uno di questi nel CONTEXT.md del progetto corrente?"

## Se non trova nulla

Riprova con termini più generici una volta, poi rispondi "non trovato" e
suggerisci `/distill-lesson`. Non inventare risultati.
