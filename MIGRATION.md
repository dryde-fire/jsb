# MIGRATION — Da Repo Attuale a Repo Integrato

Questa è la lista esatta di operazioni per riorganizzare la repo dallo stato
attuale a quello integrato descritto in `README.md`.

**Fai backup prima di eseguire qualunque comando.**

```powershell
# Backup
git add -A
git commit -m "checkpoint: pre-migration to integrated structure"
git tag pre-integration-$(Get-Date -Format 'yyyyMMdd')
```

---

## Step 1: Crea la nuova struttura di cartelle

```powershell
mkdir templates
mkdir scripts
mkdir scripts\python
mkdir scripts\powershell
mkdir skills
mkdir skills\recall
mkdir skills\distill-lesson
mkdir _research
```

## Step 2: Sposta i file di research nella loro cartella

```powershell
git mv claude-code-best-practices-DEFINITIVO.md _research\
git mv analisi-repos-claude-code.md _research\
```

## Step 3: Elimina i file obsoleti

```powershell
# v3.0 obsoleta, sostituita dalla v3.1
git rm SECOND_BRAIN_FINAL_ARCHITECTURE.md

# Setup-SecondBrain.ps1 (vecchio, hardcoded) → sostituito da Setup-Machine.ps1
git rm Setup-SecondBrain.ps1
git rm Setup-SecondBrain-Laptop.ps1
```

## Step 4: Sostituisci i file Claude Code con il SETUP-CLAUDE-CODE.md aggiornato

**FATTO**. Il file `SETUP-CLAUDE-CODE.md` è già pronto, riscritto da zero in modalità v4.1:
- Basato sulla struttura a 6 livelli del documento v4.0 originale
- Corretto: harness v4 è Go-native, 13 regole (R01-R13), no Node.js per harness
- Aggiunto: Livello 5b che integra le skill `/recall` e `/distill-lesson` con Sistema A
- Aggiunto: roadmap onesta ("Cosa NON è implementato e perché")

I file Claude Code originali del progetto vanno trattati così:

```powershell
# Era SETUP-DEFINITIVO-v4_0-FOR-DUMMIES-COMPLETE.md
# Sostituito da SETUP-CLAUDE-CODE.md nuovo (già scritto)
git rm SETUP-DEFINITIVO-v4_0-FOR-DUMMIES-COMPLETE.md

# Era HYBRID-AGENTIC-ARCHITECTURE-v4_0-COMPLETE.md (5-layer custom)
# Spostato in _research/ come "design originale, non più runtime"
git mv HYBRID-AGENTIC-ARCHITECTURE-v4_0-COMPLETE.md _research/

# Il setup attuale è in SETUP-CLAUDE-CODE.md (già nel repo, generato in v4.1)
```

## Step 5: Fondi i file Second Brain

**FATTO**. Il file `SECOND-BRAIN.md` è già pronto, frutto della fusione di:
- `SECOND_BRAIN_OPERATIVE.md` (v2.0, dettagli operativi single-machine)
- `SECOND_BRAIN_FINAL_ARCHITECTURE_v3_1.md` (v3.1, multi-machine)
- `SECOND_BRAIN_PATHS.md` (path config, ora dentro templates/)

Cosa è stato preservato dalla fusione:
- Struttura multi-PC dalla v3.1
- Naming convention dettagliata dalla v2.0 (sezione 4 di SECOND-BRAIN.md)
- Status workflow dalla v2.0 (sezione 5)
- Retrieval patterns dalla v2.0 (sezione 9)
- Maintenance settimanale dalla v2.0 (sezione 11)
- Setup checklist dalla v2.0 (sezione 12)
- Troubleshooting dalla v2.0 (sezione 13)

Cosa è stato aggiornato/corretto:
- ❌ Modelli inventati: `gemma2:9b`, `qwen2.5:1.5b`, riferimenti a "MSA paper"
- ✅ Sostituiti con: `gemma4:e2b` (verificato Aprile 2026), `gemma4:e4b` (verificato)
- ❌ Numeri tok/s irrealistici per GTX 1050 4GB
- ✅ Sostituiti con range realistici da benchmark 2026
- ❌ "256K context" inventato per Gemma 4
- ✅ Corretto a "128K context" (verificato in fonti)
- ❌ Prompt Ollama duplicati in doc + codice
- ✅ Spostati esclusivamente in `scripts/python/ingest.py` come fonte di verità
- ➕ Aggiunta sezione 6 "Modelli Ollama: scelte e ragioni" con razionale 8GB RAM
- ➕ Aggiunta sezione 14 "Roadmap" allineata con README e BRIDGE
- ➕ Aggiunta sezione 15 "Riferimenti e fonti del design" con onestà sui repo ispiratori

```powershell
# I tre file originali si possono eliminare:
git rm SECOND_BRAIN_OPERATIVE.md
git rm SECOND_BRAIN_PATHS.md
git rm SECOND_BRAIN_FINAL_ARCHITECTURE_v3_1.md
# Il nuovo SECOND-BRAIN.md è già pronto.
```

## Step 6: Aggiorna CHANGELOG.md

Apri `CHANGELOG.md` e correggi le affermazioni ottimistiche:

```diff
- Status: Production Ready 🚀
+ Status: Layers L1-L4 production-ready · L5 stub · Symphony concettuale

- "Production Ready 90%" | ✅ "production ready 90%"
+ "Production Ready 70%" | ✅ "L1-L4 production · L5+Symphony stub"
```

Aggiungi una sezione v4.1:

```markdown
# v4.1 — INTEGRATION (Maggio 2026)

## Cosa cambia

- ✨ Repo riorganizzata in due sistemi distinti che dialogano via BRIDGE.md
- ✨ Configurazione centralizzata in `~/.jsb-config.json` per ogni PC
- ✨ Skill `/recall` e `/distill-lesson` per memoria semantica condivisa
- ✨ Bug fix script Python: state corretto, hash su body, retry, quarantine
- ✨ Healthcheck settimanale automatizzato
- 🔧 Modelli aggiornati a Gemma 4 (E2B/E4B realmente disponibili Aprile 2026)
- 🗑️ Rimossi: SECOND_BRAIN_FINAL_ARCHITECTURE.md (v3.0 obsoleta),
              Setup-SecondBrain.ps1, Setup-SecondBrain-Laptop.ps1 (hardcoded)
- 📁 Spostati in `_research/`: claude-code-best-practices, analisi-repos
```

## Step 7: Aggiungi i nuovi file generati

Tutti i file generati in questa sessione vanno aggiunti al repo:

```powershell
# File di radice
git add README.md
git add BRIDGE.md
git add CROSS-LLM-COMPAT.md
git add SECOND-BRAIN.md
git add MIGRATION.md             # questo file

# Templates di config
git add templates\jsb-config.laptop.json
git add templates\jsb-config.office.json
git add templates\jsb-config.personal.json

# Script Python
git add scripts\python\jsb_core.py
git add scripts\python\watchdog.py
git add scripts\python\ingest.py
git add scripts\python\healthcheck.py

# Script PowerShell
git add scripts\powershell\Setup-Machine.ps1
git add scripts\powershell\Ingest-Orchestrator.ps1

# Skills
git add skills\recall\SKILL.md
git add skills\distill-lesson\SKILL.md
```

## Step 8: Test della nuova struttura

```powershell
# Su ogni PC, dopo aver copiato il template appropriato:
copy templates\jsb-config.laptop.json $env:USERPROFILE\.jsb-config.json
# oppure jsb-config.office.json o jsb-config.personal.json

# Adatta vault_path al PC reale, poi:
PowerShell -ExecutionPolicy Bypass -File scripts\powershell\Setup-Machine.ps1

# Verifica
python scripts\python\healthcheck.py
```

## Step 9: Test end-to-end del bridge

```powershell
# 1. Test /recall (su qualunque PC con vault accessibile)
#    Apri Claude Code in un progetto qualsiasi e chiedi:
#    "cerca nel mio vault progetti che usano stripe"
#    La skill /recall dovrebbe attivarsi e cercare in vault\wiki\

# 2. Test /distill-lesson
#    "estrai una lesson da quello che abbiamo fatto sui webhook"
#    La skill dovrebbe proporre un file in inbox\notes\

# 3. Test elaborazione
#    Aspetta il run nightly OPPURE forza:
python "$($cfg.vault_path)\_system\watchdog.py"

# 4. Verifica in wiki\projects\ che la lesson sia stata elaborata
```

## Step 10: Commit finale

```powershell
git add -A
git commit -m "feat: integrated architecture v4.1 — bridge between Second Brain and Claude Code

- Single config file per machine (~/.jsb-config.json)
- /recall and /distill-lesson skills for shared memory
- Python scripts: bug fixes (state semantics, body hash, retry, quarantine)
- PowerShell setup unified: Setup-Machine.ps1 reads config, role-aware
- Models updated to Gemma 4 E2B (fast) + E4B (quality)
- Healthcheck for weekly diagnostics
- BRIDGE.md documents the integration explicitly
"
```

---

## Riepilogo: cosa è cambiato

### File eliminati (5)
- `SECOND_BRAIN_FINAL_ARCHITECTURE.md` (v3.0 obsoleta)
- `SECOND_BRAIN_OPERATIVE.md` (assorbito in SECOND-BRAIN.md)
- `SECOND_BRAIN_PATHS.md` (assorbito in SECOND-BRAIN.md + templates/)
- `Setup-SecondBrain.ps1` (sostituito da Setup-Machine.ps1)
- `Setup-SecondBrain-Laptop.ps1` (sostituito da Setup-Machine.ps1)

### File rinominati (3)
- `SETUP-DEFINITIVO-v4_0-FOR-DUMMIES-COMPLETE.md` → `SETUP-CLAUDE-CODE.md`
- `HYBRID-AGENTIC-ARCHITECTURE-v4_0-COMPLETE.md` → `ARCHITECTURE-CLAUDE-CODE.md`
- `SECOND_BRAIN_FINAL_ARCHITECTURE_v3_1.md` → `SECOND-BRAIN.md` (con contenuti fusi)

### File spostati (2)
- `claude-code-best-practices-DEFINITIVO.md` → `_research/`
- `analisi-repos-claude-code.md` → `_research/`

### File nuovi (14)
- `README.md`, `BRIDGE.md`, `CROSS-LLM-COMPAT.md`, `SECOND-BRAIN.md`, `MIGRATION.md`
- `templates/jsb-config.{laptop,office,personal}.json` (3)
- `scripts/python/{jsb_core,watchdog,ingest,healthcheck}.py` (4)
- `scripts/powershell/{Setup-Machine,Ingest-Orchestrator}.ps1` (2)
- `skills/{recall,distill-lesson}/SKILL.md` (2)

### File aggiornati (1)
- `CHANGELOG.md` con sezione v4.1 e correzione delle affermazioni "Production Ready 90%"
