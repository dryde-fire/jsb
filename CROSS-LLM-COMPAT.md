# CROSS-LLM-COMPAT — Compatibilità cross-LLM e exit strategy

Questo documento spiega come la tua architettura rimane utilizzabile anche se
domani cambi LLM, e descrive l'integrazione futura con Hermes Agent.

> Per la mappa generale, vedi `README.md`. Per il bridge corrente con Claude
> Code, vedi `BRIDGE.md`. Per il Second Brain, vedi `SECOND-BRAIN.md`.

---

## 1. Il problema del lock-in

Il rischio quando si costruisce un sistema attorno a un LLM specifico è
**l'ostaggio**: il tuo workflow funziona solo finché continui a usare quello
strumento. Se domani Anthropic chiude Claude Code, o se esce un agent migliore,
butti via mesi di lavoro.

Questa architettura è progettata per **non avere lock-in significativo**. Le
ragioni concrete:

1. **Il vault Obsidian è la fonte di verità**, non un database proprietario. È
   markdown, leggibile da qualunque tool, fra 10 anni.
2. **Le skill seguono lo standard `agentskills.io`** (formato YAML standardizzato
   nel frontmatter), portabili fra agenti.
3. **La configurazione è in JSON locale**, non in un cloud account. Cambia
   agente, riusi config.
4. **Gli script Python sono tool-agnostic**: `watchdog.py`, `ingest.py`,
   `healthcheck.py` non sanno nulla di Claude. Parlano solo con Ollama e con
   Obsidian.

---

## 2. Lo standard agentskills.io

Le skill `/recall` e `/distill-lesson` hanno frontmatter conforme a v1 di
agentskills.io, lo standard emergente nel 2026 per skill portabili fra agenti.
Il formato chiave:

```yaml
---
schema_version: "1.0"
name: <nome-skill>
version: "1.0.0"
description: |
  <quando attivare, quando NON attivare>
license: MIT
author: <tuo-nome>
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
```

I 5 agenti elencati come compatibili supportano **già oggi** (maggio 2026) di
caricare skill in questo formato. Con piccole differenze:

| Agente | Cartella skill | Note |
|--------|----------------|------|
| Claude Code | `~/.claude/skills/<name>/SKILL.md` | Native, principale target |
| Codex (OpenAI) | `~/.codex/skills/<name>/` | Supporta da v0.8+, simile a Claude Code |
| Cursor | `.cursor/rules/<name>.mdc` | Convertibile, `description` diventa `globs` |
| Gemini CLI | `~/.gemini/extensions/<name>/` | Importazione manuale, formato simile |
| Hermes Agent | `~/.hermes/skills/<name>.md` | Native al 100%, è lo standard di riferimento |

---

## 3. Quando ti servirà cambiare/aggiungere LLM

Tre scenari realistici:

### Scenario A: Anthropic raddoppia il prezzo o rimuove Claude Pro

Probabilità: bassa ma non zero. La tua exit strategy:
1. Continui a usare il vault Obsidian come prima.
2. Sostituisci Claude Code con Codex o Gemini CLI: copia le skill in
   `~/.codex/skills/` o `~/.gemini/extensions/`, sostituisci `~/.claude/` con la
   nuova cartella.
3. Niente codice cambia. Niente vault cambia.

Tempo per la migrazione: **1 ora** se le skill sono già agentskills.io
compatibili (lo sono).

### Scenario B: Un progetto specifico sarebbe meglio servito da un altro LLM

Esempio: un progetto data-science potrebbe beneficiare di Gemini per la sua
forza nei numeri. Un progetto di scrittura creativa beneficia di Claude.

Soluzione: usa **agenti diversi su progetti diversi**, con la stessa skill
`/recall` su entrambi. Il vault è condiviso, le skill sono identiche, il
risultato è coerente.

### Scenario C: Vuoi memoria persistente fra sessioni

Claude Code dimentica fra una conversazione e l'altra. Per memoria
long-term, vedi sezione 4 (Hermes Agent).

---

## 4. Hermes Agent — quando e come integrarlo

**Quando**: Q3 2026 o oltre, **se** vuoi davvero la "voce parlante" del tuo
Second Brain via Telegram/Discord, e se hai un'oretta libera per il setup
WSL2.

**Quando NON**: se Claude Code da solo ti basta, non aggiungere Hermes. È
complessità in più che non ti serve.

### Cos'è Hermes (riassunto onesto)

Hermes Agent (Nous Research, MIT license, febbraio 2026) è un agent
autonomo che:

- Vive su un server (locale o cloud), sempre acceso
- Ha **memoria persistente** fra sessioni (FTS5 + LLM summarization)
- **Crea skill autonomamente** dopo task complessi (5+ tool calls)
- Si interfaccia con **Telegram, Discord, Slack, WhatsApp, Signal, Email**
- È **model-agnostic**: usa Ollama localmente, OPPURE chiama Claude API,
  GPT-4, Gemini via OpenAI-compatible endpoint

**Punto chiave**: Hermes è un **orchestratore**, non un modello. Significa
che puoi usare la tua **API key di Claude (Pro o standard)** dentro Hermes,
ottenendo: la potenza di Claude + memoria persistente di Hermes + interfaccia
Telegram per il telefono. **Non perdi Claude Pro**, lo arricchisci.

### Architettura proposta (quando arriverai a Fase 3)

```
        Telegram/Discord (dal telefono)
                 ↓
        Hermes Agent (su Office PC, dentro WSL2)
        ├─ Modello: Claude API (per task importanti)
        │           o Ollama gemma4:e2b (per task leggeri, gratis)
        ├─ Memoria FTS5: storia delle conversazioni passate
        ├─ Skills: importate da ~/.claude/skills/ (agentskills.io)
        └─ Vault access: legge/scrive in C:\Users\MS-Sandro\JSB
                                          (montato in WSL2 come /mnt/c/...)
                 ↓
        Vault Obsidian (stesso che usi adesso)
                 ↓
        Sync S3 → tutti i 3 PC
```

Il vault rimane invariato. Hermes diventa un **terzo modo di interagire** con
il tuo Second Brain (oltre a Obsidian e Claude Code).

### Cosa devi fare per arrivarci (sintesi, non oggi)

1. WSL2 sull'Office PC (15 min)
2. Installazione Hermes via curl one-liner (5 min)
3. Configurazione del modello: scegli se Claude API o Ollama o entrambi
4. Setup gateway Telegram (10 min, segue il wizard `hermes gateway setup`)
5. Importazione skill `/recall` e `/distill-lesson` da `~/.claude/skills/`
6. Configurazione del vault path: stesso `JSB_CONFIG`

**Tempo totale**: ~45 minuti per setup base. Tutto documentato nei doc ufficiali
Hermes (https://hermes-agent.nousresearch.com/docs/).

### Limiti onesti di Hermes

- **Su Windows richiede WSL2** — non setup zero-config
- **Curva di apprendimento del CLI Hermes** — comandi specifici da imparare
- **Dipendenza da Nous Research** — se chiudessero il progetto (improbabile,
  MIT license, repo aperto), dovresti forkare o cambiare. Mitigato dal fatto
  che `agentskills.io` è uno standard, non proprietario.

---

## 5. Alternative a Hermes (quadro 2026)

Se in futuro Hermes non ti convince, le alternative attive a maggio 2026:

| Tool | Caratteristica chiave | Quando preferirlo |
|------|----------------------|-------------------|
| **OpenClaw** | 345K stelle, 13K skill community, 24 piattaforme | Se vuoi enorme ecosistema di skill già fatte. Cautela: 9 CVE in marzo 2026 |
| **Vellum** | On-device personal AI, identità persistente | Se la privacy è priorità massima |
| **Manus** | Cloud-first, task long-horizon (ore senza supervisione) | Per task autonomi che girano la notte |
| **AutoGPT/CrewAI** | Maturi, focus su task decomposition | Se hai workflow con planning multi-step |
| **Lindy AI** | No-code, integrazioni SaaS | Se vuoi visual workflow builder, non CLI |

Tutti questi tendono a convergere sullo standard `agentskills.io` (Hermes è il
riferimento attuale). **Le tue skill funzioneranno con tutti** o con minime
modifiche al frontmatter.

---

## 6. Exit strategy esplicita

Se domani volessi smettere di usare questa architettura **completamente**:

1. **Il vault Obsidian è tuo per sempre**. È markdown su disco. Ti rimane.
2. **Le note elaborate in `wiki/` sono leggibili in qualunque editor**. Niente
   formato proprietario.
3. **I tag e la struttura cartelle sono convenzioni standard** (Karpathy LLM
   Wiki pattern), riutilizzabili in qualunque sistema futuro.
4. **Gli script Python sono ~500 righe totali**. Se vuoi capire cosa fanno o
   modificarli, è un pomeriggio.
5. **Niente subscription, niente API key proprietaria, niente lock-in con
   Anthropic** se non scegli di mantenerla.

Quello che **perderesti** smettendo:
- L'elaborazione automatica nightly (puoi sempre rifarla a mano in Obsidian
  con plugin tipo "Smart2Brain" o "Copilot").
- Le skill `/recall` e `/distill-lesson` da Claude Code (perdi solo
  l'automazione, non il contenuto).
- Il sync multi-PC automatico (puoi continuare con Remotely Save, è
  indipendente da tutto il resto).

Cioè: anche nel peggiore dei casi, **il valore accumulato nel vault è salvo**.

---

## 7. Decisioni che hai preso e perché

| Decisione | Alternativa scartata | Ragione |
|-----------|---------------------|---------|
| Markdown su filesystem | Database (SQLite, PostgreSQL) | Portabilità, leggibilità a 10 anni, niente lock-in |
| Ollama locale per elaborazione | API Claude per tutto | Costo zero per elaborazione massiva, privacy, indipendenza |
| Sync via S3 (Remotely Save) | iCloud, OneDrive, Dropbox | Costo basso, controllo totale, nessuno legge il contenuto |
| Skill agentskills.io | Skill proprietarie Claude | Future-proof, portabili ad altri agenti |
| Bridge esplicito con doc | Integrazione tacita | Documenta intenzioni, evita drift fra i due sistemi |

---

## 8. Riferimenti

- agentskills.io standard: https://agentskills.io
- Hermes Agent: https://hermes-agent.nousresearch.com/
- Karpathy LLM Wiki concept: https://karpathy.bearblog.dev (cerca "LLM Wiki")
- NicholasSpisak/second-brain: https://github.com/NicholasSpisak/second-brain
- eugeniughelbur/obsidian-second-brain: https://github.com/eugeniughelbur/obsidian-second-brain
