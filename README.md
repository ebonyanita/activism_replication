# Replication Package: Activism and Prosocial Behaviour

Authors: Söhnke Bergmann, Ebony Granada, Shaye-Ann Hopkins

Institution: WU Vienna University of Economics and Business

This package contains the experimental software, the pilot data, and the
analysis code behind the figures and results reported in the paper.

## Repository layout

```
activism_replication/
├── study_documents.pdf          ethics reflection, pre-analysis plan, power
│                                analysis & budget, experimenter script
├── instructions_activism.docx   participant instructions (Part 1 on paper)
├── screenshots_activism.docx    one screenshot per decision screen, in order
├── otree_activism/              the oTree experiment
└── analysis/                    data, scripts, figures
```

### 1. Pre-registration and power analysis
- `study_documents.pdf` — a single document containing, in order:
  Part I Ethics Reflection, Part II Pre-Analysis Plan, Part III Power Analysis
  & Budget, Part IV Experimenter Script.

### 2. Instructions
- `instructions_activism.docx` — full participant instructions for Part 1
  (points-to-euro rate, group formation, effort task, contribution stage).
  Part 2 instructions are shown on screen and live in the oTree app
  (`otree_activism/activism/InstructionsPart2_html.py`).

Note: there is no separate comprehension-questions file in this package.

### 3. Software
- `otree_activism/` — the complete oTree application.
  - `settings.py` — session configs `activism_pet_first` and
    `activism_demo_first` (treatment order counterbalanced), rooms `test`,
    `lab_s1`, `lab_s2`, participation fee €5.00.
  - `activism/` — the main app: 14 rounds (7 baseline + 7 treatment-phase),
    4 players per group, real-effort counting task, public-goods contribution.
    - `__init__.py` — constants, models, hooks, page classes, `page_sequence`
      (SeatNumber → WaitForSeats → InstructionsPart2 → ActivismChoice →
      WaitForActivism → EffortTask → Contribute → WaitForResults →
      RoundResults → Conclusion).
    - `*_html.py` — the per-page templates (oTree 6 Python-authored HTML).
    - `effort_task.js`, `soft_timer.js`, `clear_form.js` — client-side logic.
    - `tests.py` — bot test for the app.
  - `questionnaire/` — post-experiment questionnaire app
    (Questionnaire → FinalPayoff → ThankYou), incl. motivation items, perceived
    cost/extremity/legitimacy, social identification, and emotion items.
  - `_templates/`, `_static/` — global page chrome, CSS and JS.
  - `renderers.py`, `shared_out.py`, `units.py`, `project.py` — helpers and
    currency definition (points, €0.15 per point).
  - `requirements.txt` — `otree==6.0.15`, `psycopg2-binary==2.9.9`.
  - `.python-version` — Python 3.10.
  - `Procfile` — process definition for deployment.
  - `db.sqlite3` — local development database (not the analysis data).

There is no Qualtrics survey: the questionnaire is implemented as an oTree app.

Key design parameters (`otree_activism/activism/__init__.py`, class `C`):
14 rounds (7 + 7), 4 players/group, 45 s effort task, 10 points per correct
grid, MPCR 0.4, petition cost 0, demonstration cost −10 s to self, roadblock
cost −10 s to self and −5 s to every other group member.

### 4. Screenshots
- `screenshots_activism.docx` — one image per decision screen in the order
  participants encountered them: real-effort task, contribution stage, results,
  Part 2 instructions, Part 2 activism decision, Part 2 effort task, Part 2
  contribution, Part 2 results, end of Part 2, payment-round selection, final
  page.

### 5. Data, Code, Figures
- see Analysis folder

## How to run the experiment

```
cd otree_activism
pip install -r requirements.txt
otree devserver
```

Then open the admin interface and start a session with `activism_pet_first` or
`activism_demo_first` (8 demo participants by default). Set
`OTREE_ADMIN_PASSWORD` and `OTREE_SECRET_KEY` in the environment before running
anything other than a local devserver.

## Software environment

Pilot analysis: R, macOS. oTree 6.0.15 on Python 3.10. Data collected
2026-06-09 across two lab sessions: 56 participants in 14 groups of 4.
