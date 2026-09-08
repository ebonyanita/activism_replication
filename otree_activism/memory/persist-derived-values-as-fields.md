---
name: persist-derived-values-as-fields
description: Prefer storing computed experiment values as model CurrencyFields rather than local variables
metadata:
  type: feedback
---

For this oTree experiment, the user prefers group/player-level computed values (e.g. `total_contribution`) to be stored as model fields (matching the type of related fields, e.g. `CurrencyField`) rather than left as throwaway local variables.

**Why:** This is a research experiment — persisted fields appear in the admin Data tab and CSV exports, so they can be analyzed directly instead of re-derived from individual players. Also keeps field types consistent across the model.

**How to apply:** When a payoff/aggregate is computed in a page hook (e.g. `after_all_players_arrive`), assign it to a model field (`group.x`/`player.x`) declared on the model, not a local. Consider also adding it to `C.ADMIN_VIEW_FIELDS`.
