# CONTEXT.md — Domain Knowledge Base
# Authority Level: INFORMATIVE (domain knowledge)
# Maintained by: /ubiquitous-language skill + manual updates
# Review cadence: Monthly or after major domain changes

<ubiquitous_language>
## Ubiquitous Language — Glossario DDD

<!-- Compilare con i concetti specifici del dominio -->
<!-- Usare /ubiquitous-language skill per estrarre da conversazioni -->

### Core Concepts
- **[Entità A]**: [definizione precisa in una riga]
  - Stati: [stato1] → [stato2] → [stato3]
  - Invarianti: [cosa non può cambiare / quando]
  - Identificato da: [campo univoco]

- **[Entità B]**: [definizione precisa in una riga]
  - Aggregato root: [sì/no — se sì, cosa contiene]
  - Relazione con A: [descrizione]

### Termini Tecnici del Dominio
<!-- Termini che il team usa e che Claude deve conoscere -->
- **[Termine]**: [significato nel contesto di questo progetto]

### Termini Ambigui (Chiarimenti Espliciti)
<!-- Termini che sembrano ovvi ma nel dominio hanno significati specifici -->
- **[Termine]**: In questo progetto significa [X], NON [Y comune].
</ubiquitous_language>

<business_rules>
## Regole di Business

<!-- Regole invarianti che NON possono essere violate dal codice -->

### Regole Critiche (MAI violare)
- [Regola 1]: [descrizione + conseguenza della violazione]
- [Regola 2]: [descrizione + conseguenza della violazione]

### Regole Derivate (calcolate, non hardcodate)
- [Regola derivata]: [formula o logica]

### Eccezioni Note
- [Caso eccezionale]: [quando si applica e come gestirlo]
</business_rules>

<system_boundaries>
## Confini del Sistema

### In Scope
- [Cosa questo sistema fa e possiede]

### Out of Scope
- [Cosa questo sistema NON fa — e chi lo fa invece]

### Integrazioni Esterne
- [Sistema X]: [cosa fornisce / cosa consuma] — [protocollo]
- [Sistema Y]: [cosa fornisce / cosa consuma] — [protocollo]
</system_boundaries>

<architecture_summary>
## Sintesi Architetturale

### Decisioni Prese (vedi docs/adr/ per dettagli)
- ADR-001: [Decisione] — [rationale una riga]
- ADR-002: [Decisione] — [rationale una riga]
- ADR-003: [Decisione] — [rationale una riga]

### Pattern Architetturali in Uso
- [Pattern]: [dove e perché]

### Anti-Pattern Esplicitamente Esclusi
- [Anti-pattern]: [perché NON lo usiamo — evita reintroduzione]
</architecture_summary>

<change_log>
## Changelog CONTEXT.md

| Data | Modifica | Autore |
|------|----------|--------|
| [YYYY-MM-DD] | Creazione iniziale | [nome/agente] |
| [YYYY-MM-DD] | Aggiornamento ubiquitous language — [topic] | [nome/agente] |
</change_log>
