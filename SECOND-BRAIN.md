# Second Brain — Documento Operativo Unificato

**Versione**: 4.0 (Maggio 2026)
**Sostituisce**: SECOND_BRAIN_FINAL_ARCHITECTURE_v3_1.md, SECOND_BRAIN_OPERATIVE.md, SECOND_BRAIN_PATHS.md
**Modelli**: Gemma 4 E2B (default veloce), Gemma 4 E4B (qualità, solo Office PC)

> Questo documento descrive il **Sistema A** dell'architettura integrata. Per il bridge
> con Claude Code (Sistema B), vedi `BRIDGE.md`. Per la mappa generale, vedi `README.md`.

---

## 1. Cos'è e cosa NON è

**Cos'è**: una pipeline che cattura note Obsidian su 3 PC, le sincronizza via S3
Cloudflare, e usa Ollama per elaborare contenuto grezzo (`inbox/`) in conoscenza
strutturata (`wiki/`).

**Cosa NON è**: un sistema in tempo reale. C'è delay di 24h fra scrittura nota e
versione elaborata disponibile. Questo è un design choice (forza un quality
check mentale), non un limite tecnico.

---

## 2. Architettura

```
CATTURA (multi-device, immutable)
├── Personal PC (sandr)         ← editor + reader
├── Laptop XPS 15               ← editor + Ollama GPU (E2B veloce)
└── Office PC MS-Sandro         ← always-on + Ollama (E2B + E4B qualità)

                ↓ (Remotely Save → S3 Cloudflare)

inbox/ (raw, write-only)
├── articles/, notes/, documents/, conversations/
└── _failed/                    ← quarantine dopo 3 fallimenti
└── Sincronizzato fra tutti e 3 i PC

                ↓

ELABORAZIONE (00:00 nightly, su Office PC come orchestratore)
├── Try 1: WoL → Laptop online → SSH → watchdog.py su laptop
│   └── Ollama: gemma4:e2b (GPU GTX 1050)
│       ├── Velocità: ~15 tok/s
│       ├── Qualità: 7.5/10
│       └── Contesto: 128K
│
├── Try 2: Fallback locale su Office PC
│   └── Ollama: gemma4:e2b (default) o gemma4:e4b (priority=high)
│       ├── E2B: ~10 tok/s CPU
│       ├── E4B: ~3 tok/s CPU, qualità 8.5/10
│       └── Modello dipende dal `priority` del file
│
└── Output: wiki/ (con archive/ del precedente per idempotenza)

                ↓ (Remotely Save → S3)

wiki/ (knowledge consolidated)
├── concepts/, learn/, projects/, decisions/
└── Visibile a tutti i 3 PC + skill /recall di Claude Code
```

---

## 3. Configurazione per macchina

Tutti gli script leggono da un singolo file: `%USERPROFILE%\.jsb-config.json`.

| PC | machine_id | role | Ollama | Note |
|----|------------|------|--------|------|
| Personal (sandr) | `personal-sandr` | `editor-only` | nessuno | Solo Obsidian + Remotely Save |
| Laptop (XPS 15) | `laptop-xps15` | `elaborator-fast` | gemma4:e2b | GTX 1050 4GB, 8GB RAM. Solo E2B per limiti hw. |
| Office (MS-Sandro) | `office-ms-sandro` | `elaborator-quality` | gemma4:e2b + e4b | 16GB RAM. E4B qualità su CPU lenta ma ok. |

Template di config sono in `templates/jsb-config.{laptop,office,personal}.json`.

**Cambi PC, copi il template, sostituisci il path del vault, hai finito.**

---

## 4. Naming convention dei file

### `inbox/articles/*.md` — articoli da web

```
[YYYY-MM-DD]_[source]_[slug].md

Esempi:
  2026-05-09_newsletter-ai_attention-mechanisms.md
  2026-04-28_medium_memory-systems-architecture.md
  2026-04-25_arxiv_cost-effective-retrieval.md
```

Frontmatter:
```yaml
---
type: article
source: newsletter-ai | medium | arxiv | pocket | rss
url: https://...
date_captured: 2026-05-09
date_published: 2026-04-30
tags: [attention, transformer, ai]
status: inbox
priority: normal              # 'high' attiva model_quality (E4B su Office)
---
```

### `inbox/notes/*.md` — note dirette

```
[YYYY-MM-DD]_[type]_[title].md

Tipi: brainstorm | learning | idea | decision | question
Tipi del bridge: lesson-learned | architecture-decision | project-pattern

Esempi:
  2026-05-09_brainstorm_second-brain-architecture.md
  2026-05-09_lesson-learned_stripe-webhook-server-validation.md
```

Frontmatter:
```yaml
---
type: brainstorm | learning | idea | decision | question | lesson-learned | architecture-decision | project-pattern
created: 2026-05-09
tags: [architecture, memory, llm]
status: inbox
priority: normal
related_to: [other-note-slugs]   # opzionale
---
```

### `inbox/documents/*.md` — excerpt da PDF/ebook

```
[YYYY-MM-DD]_[document-type]_[title].md

Tipi: pdf-excerpt | ebook-note | research | whitepaper

Esempio:
  2026-04-15_pdf-excerpt_attention-is-all-you-need.md
```

Frontmatter:
```yaml
---
type: pdf-excerpt | ebook-note | research | whitepaper
source_title: "Original Document Title"
source_author: Author Name
date_read: 2026-04-15
pages: [45-52]
tags: [ml, system-design]
status: inbox
priority: normal
highlight: true | false
---
```

### `inbox/conversations/*.md` — output di chat con LLM

```
[YYYY-MM-DD]_[llm]-[session-number].md

Esempi:
  2026-05-09_claude-001.md
  2026-05-09_gemini-001.md
```

Frontmatter:
```yaml
---
type: conversation
llm: claude | gemini | hermes | other
date: 2026-05-09
session_number: 001
topic: second-brain-architecture
outcome: architecture-defined | questions-raised | insights-captured
tags: [memory, architecture]
status: inbox
priority: normal
---
```

---

## 5. Workflow degli stati

```
inbox/ (raw, write-only)
  status: inbox
        ↓
  watchdog.py rileva file (hash sul body, non sul frontmatter)
        ↓
  ingest.py chiama Ollama → modello scelto in base a priority:
    - priority: normal → model_default (E2B)
    - priority: high   → model_quality (E4B su Office, E2B su laptop)
        ↓
  Output in wiki/<categoria>/<slug>.md
    - Se file esiste già → archive/<categoria>/<slug>-<timestamp>.md (idempotenza)
    - Frontmatter aggiornato con: status=published, date_elaborated, elaborated_by, version
        ↓
wiki/ (elaborated)
  status: published, version: 1
        ↓
  Tu leggi/editi a mano in Obsidian
  Ogni edit incrementa version manualmente (convenzione, non automatismo)
        ↓
  Se la nota diventa obsoleta:
        ↓
archive/ (stale)
  status: archived
```

I prompt esatti che Ollama riceve per ogni `type` sono codificati nella funzione
`build_prompt()` in `scripts/python/ingest.py`. Non sono nel doc per evitare drift
fra documentazione e codice — il codice è la fonte di verità.

---

## 6. Modelli Ollama: scelte e ragioni

### Su Laptop XPS 15 (8 GB RAM totale, GTX 1050 4 GB VRAM)

**Default e Qualità: `gemma4:e2b`** (entrambi, sì)

Spiegazione onesta: con 8 GB di RAM totale, E4B è impraticabile. Anche col
modello quantizzato Q4 (3.5 GB di soli pesi) e l'offload CPU/GPU, il sistema va
in swap e diventa inusabile per ~minuti durante l'elaborazione. Sul laptop,
**la qualità delegata a Office PC**.

### Su Office PC MS-Sandro (16 GB RAM, CPU only)

**Default: `gemma4:e2b`** — usato per `priority: normal`. ~10 tok/s CPU.

**Qualità: `gemma4:e4b`** — usato solo se la nota ha `priority: high` nel
frontmatter. ~3 tok/s su CPU, ma qualità tangibilmente superiore (8.5/10 vs
7.5/10 di E2B). Utile per articoli lunghi importanti, paper di riferimento,
decision record.

### Modelli da non usare (deprecati per questo setup)

- `gemma2:9b`, `gemma2:2b` — superati da Gemma 4 (aprile 2026)
- `qwen2.5:1.5b` — qualità inferiore, sostituito da E2B
- `llama3.2:1b` — può rimanere come emergency fallback se Gemma 4 ha problemi

---

## 7. Comandi Ollama essenziali

```bash
# Pull modelli (esegui una volta per PC)
ollama pull gemma4:e2b              # Tutti i PC con role=elaborator-*
ollama pull gemma4:e4b              # Solo Office PC

# Verifica modelli installati
ollama list

# Test rapido (deve rispondere in <10s)
ollama run gemma4:e2b "Riassumi in 1 frase: cos'è un transformer?"

# Server (deve girare in background, di solito già autostart)
ollama serve
```

---

## 8. Sync S3 Cloudflare (Remotely Save)

### Setup iniziale (Personal PC)

1. Cloudflare R2: crea bucket `second-brain-vault`.
2. Genera API token con permessi Object Read/Write.
3. Obsidian → Settings → Community plugins → cerca "Remotely Save".
4. Configura S3:
   - Endpoint: `<account-id>.r2.cloudflarestorage.com`
   - Region: `auto`
   - Bucket: `second-brain-vault`
   - Access key + Secret key dal token Cloudflare.
5. Test connessione → Sync iniziale.

### Setup sugli altri PC

Stessa procedura, **stesse credenziali e stesso bucket**. Al primo sync, ognuno
scarica lo stato corrente. Da lì in poi, sync incrementale.

### Importante: token scadenza

Cloudflare R2 access token scade ogni **90 giorni**. Aggiungi un reminder
trimestrale per rigenerarlo. Healthcheck nel modulo `healthcheck.py` non
controlla questo (è scoperto solo al fallimento del sync).

---

## 9. Retrieval — come cercare nel vault

### Obsidian nativo (ogni PC)

```
Ctrl+Shift+F          → full-text search in tutti i file
Ctrl+P → "Search"     → command palette
```

Tag-based query (con plugin "Dataview" o "Query"):
```dataview
TABLE file.name, tags, date_elaborated
FROM "wiki"
WHERE contains(tags, "stripe") AND status = "published"
SORT date_elaborated DESC
```

### Da Claude Code (skill `/recall`)

Vedi `BRIDGE.md` per dettagli. La skill esegue ricerca full-text via
`ripgrep` e ritorna i top 5 file pertinenti, che puoi includere nel CONTEXT.md
del progetto.

### Da iPhone/iPad (Obsidian Mobile)

Sync via Remotely Save (a richiesta, non automatico in background per risparmio
batteria). Search funziona identico al desktop.

---

## 10. Tagging — strategia per ricerca futura

Tre dimensioni di tag, da usare in combinazione:

| Dimensione | Esempi |
|------------|--------|
| **Topic** | `architecture`, `memory`, `llm`, `ai`, `systems-design`, `database`, `ecommerce` |
| **Tech** | `typescript`, `postgres`, `stripe`, `react`, `python`, `ollama`, `obsidian` |
| **Categoria** | `security`, `performance`, `testing`, `deployment`, `pattern`, `decision` |

Aggiungi anche, opzionale:
- `confidence`: `high` | `medium` | `experimental`
- `stage`: `inbox` | `learning` | `reference`

**Convenzione**: 4-7 tag per file. Meno = ricerche future inefficaci. Più = rumore.

**Anti-pattern**: tag generici tipo `interesting`, `important`, `todo`. Inutili.

---

## 11. Maintenance settimanale (5 minuti, ogni venerdì)

```markdown
## Settimana del [DATA]

- [ ] Esegui `python healthcheck.py` (su Office PC) → leggi report
- [ ] Verifica `_system/ingest-log.md` — qualcosa di anomalo?
- [ ] Visita `wiki/` → leggi nuove note pubblicate questa settimana
- [ ] Edita se necessario (incrementa `version` nel frontmatter)
- [ ] Sposta in `archive/` ciò che è obsoleto
- [ ] Verifica `inbox/_failed/` — file in quarantena richiedono review manuale
- [ ] Check inbox/ size: dovrebbe essere stabile, non crescere indefinitamente
```

### Mensile

- Review tag inconsistenti. Se `database`, `databases`, `db` coesistono,
  unificali a uno solo.
- Pulisci `archive/` se cresce oltre i 100 MB (sposta su backup esterno).
- Verifica scadenza token Cloudflare R2 (ogni 90 giorni, tipicamente trimestre).

---

## 12. Setup checklist per PC

### Personal PC (editor-only)

- [ ] Installa Obsidian
- [ ] Crea vault in `C:\Users\sandr\JSB`
- [ ] Installa plugin Remotely Save
- [ ] Configura R2 credentials
- [ ] Copia `templates/jsb-config.personal.json` → `%USERPROFILE%\.jsb-config.json`
- [ ] Esegui `Setup-Machine.ps1` (skip Ollama)
- [ ] Test: crea `inbox/notes/test.md`, sync, verifica su altri PC

### Laptop e Office PC (elaborator)

- [ ] Installa Python 3.11+ (richiesto da pyyaml/requests)
- [ ] Installa Ollama da https://ollama.ai
- [ ] Pull modelli (`ollama pull gemma4:e2b`, e su Office anche `gemma4:e4b`)
- [ ] Installa Obsidian (anche se non scrivi spesso, utile per review)
- [ ] Copia template di config appropriato
- [ ] Esegui `Setup-Machine.ps1` come Admin
- [ ] Verifica Task Scheduler creato: `Get-ScheduledTask SecondBrain-Watchdog`
- [ ] Test fine: `python healthcheck.py` → verdetto OK

### Solo Office PC (orchestratore + WoL verso laptop)

- [ ] Configura sezione `orchestrator` in `.jsb-config.json` con IP e MAC laptop
- [ ] Sul laptop: BIOS → Power Management → Wake on LAN: enabled
- [ ] Sul laptop: Device Manager → Network Adapter → Power Mgmt → "Allow this device to wake the computer"
- [ ] Dal laptop: registra TrustedHosts su Office PC (`Enable-PSRemoting -Force`)
- [ ] Test WoL manuale: dall'Office, esegui `Ingest-Orchestrator.ps1`

---

## 13. Troubleshooting

### Ollama non risponde

```bash
# Verifica server
curl http://localhost:11434/api/tags

# Se non risponde
ollama serve              # in un terminale separato

# Verifica memoria
ollama ps                 # quali modelli sono caricati
```

### `watchdog.py` crasha

```bash
# Run manuale per vedere stack trace
python C:\path\to\vault\_system\watchdog.py
```

Le cause più comuni:
- Config non trovato → verifica `%USERPROFILE%\.jsb-config.json`
- `vault_path` errato → verifica esistenza cartella
- `pyyaml` non installato → `pip install pyyaml`
- Ollama irraggiungibile → vedi sopra

### Sync Remotely Save non parte

- Obsidian → Settings → Remotely Save → "Test S3 Connection"
- Se errore 403: token Cloudflare scaduto, rigenera
- Se errore 404: bucket sbagliato o non esiste

### Task Scheduler non parte di notte

```powershell
# Verifica task
Get-ScheduledTask -TaskName "SecondBrain-Watchdog" | Format-List *

# Vedi history (eventi)
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 50 |
  Where-Object {$_.Message -like "*SecondBrain*"}

# Run manuale per testare
Start-ScheduledTask -TaskName "SecondBrain-Watchdog"
```

### File bloccati in `inbox/_failed/`

- Apri il file `.error` corrispondente per leggere il motivo del fallimento
- Cause tipiche: tipo sconosciuto in frontmatter, body completamente vuoto,
  caratteri Unicode anomali
- Correggi il file e spostalo manualmente da `_failed/` a `inbox/<categoria>/`
- Lo state lo riprenderà al prossimo run

---

## 14. Roadmap (post stabilità Fase 1)

**Fase 1 (oggi → fine Maggio 2026)**: questo documento. Sistema funzionante.

**Fase 2 (Giugno-Luglio 2026, opzionale)**: ricerca semantica con FTS5/SQLite.
Modulo `vault_search.py` aggiunto, skill `/recall` aggiornata. Niente
dipendenze esterne, tutto locale.

**Fase 3 (Q3 2026, se ti attira)**: integrazione Hermes Agent come "voce
parlante" del Second Brain. Hermes legge dal vault, tu chatti con lui via
Telegram/Discord dal telefono. Vedi `BRIDGE.md` sezione "Hermes Integration
Path" per dettagli. **Non richiesto** — il sistema funziona senza.

**Fase 4 (quando avrai bisogno)**: cross-LLM compat full. Le skill `/recall` e
`/distill-lesson` sono già scritte in formato `agentskills.io` standard,
funzionano con Codex, Cursor, Gemini CLI senza modifiche. Vedi
`CROSS-LLM-COMPAT.md`.

---

## 15. Riferimenti e fonti del design

Questa architettura si basa su pattern consolidati nel 2026, in particolare:

- **Karpathy LLM Wiki pattern** (gennaio 2026) — concetto base "raw → LLM
  compiles → wiki"
- **NicholasSpisak/second-brain** (aprile 2026) — implementazione che ha
  ispirato la struttura `raw/` + `wiki/` con sub-cartelle per tipologia
- **eugeniughelbur/obsidian-second-brain** (maggio 2026) — pattern delle skill
  Claude Code per interazione con vault

Specifiche di questa architettura non presenti negli altri (originali del
nostro setup):
- Pipeline multi-PC con S3 sync e routing laptop/office
- Configurazione centralizzata `.jsb-config.json`
- Pattern di "qualità delegata": laptop=veloce, office=qualità
- Bridge bidirezionale con Claude Code via skill `/recall` e `/distill-lesson`
