# Quick Reference — JSB Knowledge System
**Versione**: 2.0 (allineata a 0.Setup v4.0, Maggio 2026)
**Uso**: Apri questo file ogni volta che inizi una sessione di lavoro.

---

## PATHS — Riferimento rapido

| Cosa               | Dove                                                                  |
| ------------------ | --------------------------------------------------------------------- |
| Vault Obsidian     | `C:\Users\sandr\JSB\` (Personal) · `C:\Users\MS-Sandro\JSB\` (Office) |
| Config macchina    | `%USERPROFILE%\.jsb-config.json`                                      |
| Inbox (cattura)    | `...\JSB\inbox\notes\` · `...\JSB\inbox\articles\`                    |
| Wiki (elaborato)   | `...\JSB\wiki\`                                                       |
| Scripts Python     | `scripts/python/` nella repo 0.Setup                                  |
| Fonte della Verità | `C:\Users\sandr\JSB\Wiki\0.Setup\`                                    |

---

## STARTUP GIORNALIERO

```powershell
# 1. Apri Obsidian → Remotely Save → Sync manuale (se non auto)

# 2. Verifica Ollama attivo (solo su elaborator PC)
curl http://localhost:11434/api/tags

# 3. Se sei sull'Office PC: esegui healthcheck settimanale (ogni venerdì)
python scripts/python/healthcheck.py
```

---

## CATTURA UNA NOTA

Naming convention: `YYYY-MM-DD_[tipo]_[slug].md`

```
Tipi validi:
  brainstorm | learning | idea | decision | question
  lesson-learned | architecture-decision | project-pattern
```

Frontmatter minimo:
```yaml
---
type: lesson-learned
created: 2026-05-10
tags: [dominio, tech, categoria]
status: inbox
priority: normal
---
```

Salva in `inbox/notes/`. Ollama elaborerà nella notte stessa (o seguente).

**Tag: usa 3 dimensioni, 4-7 tag totali**

| Dimensione | Esempi |
|------------|--------|
| Dominio | `ecommerce`, `auth`, `cms`, `analytics` |
| Tech | `typescript`, `postgres`, `stripe`, `react`, `python`, `ollama` |
| Categoria | `security`, `performance`, `testing`, `architecture`, `pattern` |

---

## BRIDGE — Claude Code ↔ Second Brain

### Cercare nel vault da Claude Code
```
Tu: Cerca nel vault decisioni su [argomento]
→ Claude esegue /recall
→ Ottieni top 5 file da wiki/ rilevanti
→ Includi quelli utili in CONTEXT.md del progetto
```

### Salvare una lesson learned
```
Tu: Ho imparato qualcosa di importante, salvalo nel vault
→ Claude esegue /distill-lesson
→ Claude propone nota strutturata con frontmatter
→ Tu confermi → file scritto in inbox/notes/
→ Ollama elabora nella notte stessa
```

---

## CAMBIO PC

```
1. Apri Obsidian sul nuovo PC
2. Remotely Save → Sync (attendi completamento ~5-30s)
3. Leggi wiki/ per aggiornamenti recenti
4. Se sei sull'elaborator PC: controlla inbox/_failed/ per errori
```

---

## OLLAMA — Comandi essenziali

```bash
# Verifica modelli installati
ollama list

# Test rapido (risposta in <10s = OK)
ollama run gemma4:e2b "Riassumi in 1 frase: cos'è un transformer?"

# Server (deve girare in background, di solito già autostart)
ollama serve
```

**Modelli per PC:**

| PC | Modello default | Modello qualità |
|----|----------------|----------------|
| Laptop XPS 15 | `gemma4:e2b` | `gemma4:e2b` (E4B non praticabile: 8GB RAM) |
| Office MS-Sandro | `gemma4:e2b` | `gemma4:e4b` (per `priority: high`) |
| Personal sandr | — | — (editor-only, niente Ollama) |

---

## TROUBLESHOOTING RAPIDO

| Sintomo | Causa probabile | Fix |
|---------|----------------|-----|
| Sync non parte | Token Cloudflare R2 scaduto (90gg) | Rigenera token su Cloudflare |
| Ollama non risponde | Server non avviato | `ollama serve` in terminale separato |
| File in `inbox/_failed/` | Frontmatter errato o body vuoto | Apri `.error` corrispondente, correggi, sposta in `inbox/<tipo>/` |
| `/recall` non trova nulla | Tag insufficienti o keyword diversa | Riprova con keyword diversa; verifica tagging nelle note |
| Task Scheduler non gira | Problema di permessi o configurazione | `Get-ScheduledTask SecondBrain-Watchdog` + verifica history log |

Per dettaglio completo: `0.Setup/SECOND-BRAIN.md` sezione 13.

---

## MANUTENZIONE

| Frequenza | Azione |
|-----------|--------|
| Ogni venerdì (5 min) | `python healthcheck.py` da Office PC |
| Mensile | Review tag inconsistenti in `wiki/`; pulisci `archive/` se >100MB |
| Ogni 90 giorni | Rigenera token Cloudflare R2 |

Checklist dettagliata: `0.Setup/SECOND-BRAIN.md` sezione 11.
