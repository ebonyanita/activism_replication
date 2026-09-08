# Replication Package: Petition or Protest? Activism and Prosocial Behaviour

Authors: Ebony Granada, Shaye-Ann Hopkins, Söhnke Bergmann
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
- `analysis/2.scripts/power_analysis.py` — simulation-based power/sample-size
  analysis for the planned 4-arm study (control + demonstration + petition +
  roadblock, 20 rounds). Refits the pilot mixed model, then simulates power for
  the estimator actually reported (OLS with CR2 cluster-robust SEs, clustered by
  group), sweeping group-level treatment-effect heterogeneity `tau`.
- `analysis/2.scripts/power_analysis_notes.md` — full rationale, design table,
  assumptions, and results narrative for the above.
- `analysis/power_analysis.py` — earlier, simpler scenario-based power
  calculation over assumed treatment means (superseded by the version in
  `2.scripts/`; kept for reference).
- A conservative power simulation using the pilot data also runs at the end of
  `analysis/2.scripts/ActivismPilotAnalysis.Rmd` (§ "Primary analysis uses
  df_long_clean", power curve for 12–40 groups).

### 2. Instructions
- `instructions_activism.docx` — full participant instructions for Part 1
  (points-to-euro rate, group formation, effort task, contribution stage).
  Part 2 instructions are shown on screen and live in the oTree app
  (`otree_activism/activism/InstructionsPart2_html.py`).
- `study_documents.pdf`, Part IV — experimenter script / session protocol.

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

### 5. Data
- `analysis/1.data/` — raw oTree exports, two lab sessions (56 participants in
  14 groups of 4, after dropping demo rows):
  - `raw_s1_all_apps_wide_2026-06-09-2.csv` (36 rows × 258 columns)
  - `raw_s2_all_apps_wide-2026-06-09-2.csv` (28 rows × 272 columns)
  - `raw_s1_PageTimes-2026-06-09.csv`, `raw_s2_PageTimes-2026-06-09-2.csv` —
    page-level timing exports
  - `s1.numbers`, `s2.numbers`, `s1-pagetimes.numbers`, `s2-pagetimes.numbers` —
    Apple Numbers copies of the same exports, for inspection only
  - `data-overview.csv` — the session 2 export in oTree's wide format, used as a
    quick overview of every exported variable
- `analysis/1.data/clean/` — produced by the analysis script:
  - `clean_dfs.RData` — `df_wide`, `df_clean`, `df_long`, `df_long_clean`,
    `df_participant`, `df_questionnaire`
  - `df_long.csv` — participant × round panel, 56 participants × up to 14
    rounds (612 rows), the dataset all reported results are computed on

Session 2 has more columns than session 1 because
`group.total_contribution` was not logged in session 1. The panel is unbalanced:
36 participants (9 groups) completed all 14 rounds, while five groups hit
technical failures and stopped at round 3, 5, or 7. Their logged responses are
kept in `df_long`; `df_long_clean` drops the five affected groups, leaving the
36 participants who also completed the questionnaire. The primary analysis uses
`df_long_clean`, and `df_long` is retained for a robustness comparison.

There is no standalone variable dictionary file. The constructed analysis
variables are defined in the cleaning chunks of
`analysis/2.scripts/ActivismPilotAnalysis.Rmd` (§ "Cleaning & Main Outcomes")
and include, among others:

| Variable | Definition |
|---|---|
| `relative_contribution` | contribution ÷ wage × 100 (percent of wage contributed) |
| `chose_activism` / `activism_rate` | individual and group-level activism turnout |
| `is_treatment_round` | 0 for rounds 1–7, 1 for rounds 8–14 |
| `condition` | assigned arm: petition, demonstration, roadblock |
| `welfare`, `norm_welfare`, `welfare_fullcoop` | group earnings per round, raw, time-normalised, and relative to full cooperation |
| `efficiency` | realised welfare as a share of the full-cooperation benchmark |
| `others_contribution`, `NegDev`, `PosDev` (and `_lag` variants) | peer contributions and signed deviations from them |

### 6. Code
- `analysis/2.scripts/ActivismPilotAnalysis.Rmd` — the single end-to-end
  analysis script: setup → cleaning → descriptives → H1/H2/H3 → exploratory
  analyses → mixed models → power simulation.
- `analysis/2.scripts/ActivismPilotAnalysis.html` — knitted output of the above,
  with every table and figure inline.
- `analysis/2.scripts/power_analysis.py`, `power_analysis_notes.md` — see § 1.

There is no `run_all` master script; the `.Rmd` is the pipeline. Raw → clean is
the "Cleaning" section, and clean → results is everything after it.

### 7. Figures
`analysis/3.figs/` holds the exported figures. They correspond to sections of
the `.Rmd` as follows:

| Figure file | Section in `ActivismPilotAnalysis.Rmd` |
|---|---|
| `1.1.contribution.png`, `1.1b.contribution.png` | H1 → Figs: Contribution Rate |
| `1.2.contributionprepost.png` | H1, pre/post treatment phase |
| `1.3.contributionovertimecontrol.png`, `1.4.contributionovertime.png` | H1, contribution over rounds |
| `2.1.activismrate.png`, `2.1.activismrateovertime.png` | H2 → Figs: Turnout |
| `3.1.welfare.png`, `3.2.welfarenormprepost.png`, `3.3.welfareprepost.png`, `3.4.welfarenormprepost.png` | H3 → Figs: Welfare |
| `3.5.welfareovertimecontrol.png`, `3.6.welfareovertime.png` | H3, welfare over rounds |
| `4.activism&cont.png` | Exploratory → Activist vs. Non-Activist Contributions |
| `5.efficiency.png` | Exploratory → Efficiency |

Figures are rendered by the `.Rmd` chunks; the `.png` files are exports of those
chunk outputs rather than the product of `ggsave()` calls in the script.

## How to reproduce the analysis

1. Install R (≥ 4.2) and RStudio, plus the packages the script loads. They must
   already be installed — the script calls `library()` directly and only
   installs `pacman` itself if missing:

   `AER`, `clubSandwich`, `corrplot`, `devtools`, `dplyr`, `effectsize`,
   `emmeans`, `estimatr`, `fixest`, `fwildclusterboot`, `ggeffects`, `ggpubr`,
   `ggsignif`, `ggthemes`, `gtsummary`, `here`, `interactions`, `kableExtra`,
   `lme4`, `lmerTest`, `modelsummary`, `pacman`, `paletteer`, `patchwork`,
   `performance`, `psych`, `rempsyc`, `report`, `sandwich`, `simr`, `sjPlot`,
   `tidyverse`.
2. Open `analysis/2.scripts/ActivismPilotAnalysis.Rmd` and change the `setwd()`
   line in the `setup` chunk to point at your local `analysis/` directory. All
   other paths in the script are relative to `analysis/` and need no editing.
3. Knit the document. It reads from `1.data/`, writes `1.data/clean/`, and
   produces every table and figure inline.

For the power analysis: Python 3.10+ with `numpy`, `pandas`, `scipy`, and
`statsmodels`. Run `python analysis/2.scripts/power_analysis.py`
(add `--analytic` for the GLS cross-check).

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
