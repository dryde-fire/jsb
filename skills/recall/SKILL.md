---
schema_version: "1.0"
name: recall
version: "2.0.0"
description: |
  Cerca nel Second Brain personale usando LightRAG (ricerca semantica su knowledge
  graph) o ripgrep (fallback full-text). Attiva quando l'utente chiede:
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
  - http-get
  - shell-exec
config_dependencies:
  - path: "~/.jsb-config.json"
    field: "vault_path"
    required: true
  - path: "~/.jsb-config.json"
    field: "lightrag.url"
    required: false
---

# Skill: /recall v2 — Ricerca semantica nel Second Brain via LightRAG

## Differenza dalla v1

La v1 usava ripgrep (full-text, trova solo parole esatte).
La v2 usa LightRAG (knowledge graph + vector search, trova per significato).

Esempio pratico:
- Query: "decisioni sui database"
- v1 ripgrep: trova solo file che contengono letteralmente "database"
- v2 LightRAG: trova anche "PostgreSQL vs MongoDB", "scelta dello storage",
  "persistenza dei dati" anche se non contengono la parola esatta "database"

Fallback automatico a ripgrep se LightRAG non è raggiungibile.

## Step 1: Leggi la configurazione

```python
import json, os
from pathlib import Path

cfg_path = os.environ.get("JSB_CONFIG") or Path.home() / ".jsb-config.json"
cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))

vault_path = Path(cfg["vault_path"])
lightrag_url = cfg.get("lightrag", {}).get("url", "")
lightrag_key = cfg.get("lightrag", {}).get("api_key", "")
headers = {"Authorization": f"Bearer {lightrag_key}"} if lightrag_key else {}
```

## Step 2: Costruisci la query in linguaggio naturale

LightRAG capisce frasi complete molto meglio di keyword sparse.

Esempi:
- MALE:  "stripe webhook security"
- BENE:  "Come validare firma webhook Stripe lato server?"
- MALE:  "database decision 2025"
- BENE:  "Quali decisioni ho preso sulla scelta del database per e-commerce?"

## Step 3: Chiama LightRAG

```python
import requests

response = requests.post(
    f"{lightrag_url}/query",
    headers={**headers, "Content-Type": "application/json"},
    json={
        "query": query,
        "mode": "hybrid",          # vector + graph, migliore qualità
        "only_need_context": True, # ritorna chunk sorgente, non riassunto
        "top_k": 10,
    },
    timeout=30,
)
data = response.json()
contexts = data.get("contexts") or data.get("context") or []
```

## Step 4: Fallback ripgrep

Se LightRAG non risponde (Office PC spento, server non avviato), usa ripgrep:

```bash
rg -i --type md -C 2 "<keyword>" "${VAULT_PATH}/wiki/"
```

Quando usi il fallback, avvisa sempre l'utente:
"LightRAG non raggiungibile, uso ricerca full-text (risultati meno precisi)."

## Step 5: Filtra e presenta (max 5 file)

Per ogni chunk ricevuto:
1. Estrai source_path dai metadata
2. Leggi frontmatter del file (status, tags, version, date_elaborated)
3. Scarta file con status: archived
4. Raggruppa chunk dello stesso file
5. Ordina per version desc, poi date_elaborated desc
6. Mostra max 5 file distinti

Formato output per ogni file:

    📄 wiki/decisions/postgres-vs-mongo-2025-11.md
       tags: [database, decision, ecommerce]
       version: 2 · elaborated: 2025-11-15
       "2-3 righe del contenuto più rilevante"

Concludi sempre con:
"Vuoi che includa uno di questi nel CONTEXT.md del progetto corrente?"

## Step 6: Se non trova nulla

1. Riformula la query diversamente
2. Usa fallback ripgrep con keyword più generiche
3. Suggerisci di creare una nota con /distill-lesson

Non inventare risultati. "Non trovato" è una risposta valida.

## Note operative

LightRAG gira su Office PC (processo Python, porta 9621). Se Office PC è spento,
la skill cade automaticamente sul fallback ripgrep — funziona da qualunque
PC che ha il vault sincronizzato localmente.

I file nuovi appaiono in LightRAG solo dopo il run nightly di watchdog.py.
Per indicizzare subito: python scripts/python/ingest_to_lightrag.py da Office PC.

Cross-LLM: questa skill chiama HTTP localhost:9621. Funziona identicamente
da Claude Code, Codex CLI, Cursor, Gemini CLI perché l'endpoint è
indipendente dall'agent.
