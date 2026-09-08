# Activism Study — Power Analysis Simulation Notes

## Research Question

Does each form of activism (demonstration, petition, roadblock) change how much
participants contribute, relative to a no-treatment control? The study is sized so
that the **petition-vs-control** and **roadblock-vs-control** effects can be
detected; the demonstration effect is small and treated as exploratory.

## Design

A **4-arm** between-groups design with a within-group before/after structure:

| Arm | Rounds 1–10 (baseline) | Rounds 11–20 (treatment phase) |
|---|---|---|
| **Control** (reference) | normal play | normal play, no intervention |
| Demonstration | normal play | activism intervention |
| Petition | normal play | activism intervention |
| Roadblock | normal play | activism intervention |

- **Unit of randomisation: the group** (4 participants per group). Whole groups
  are assigned to an arm.
- **20 rounds per participant** (10 baseline + 10 treatment-phase).
- Outcome: `relative_contribution` = contribution ÷ wage × 100 (percent of wage
  contributed), treated as continuous.
- The control group plays all 20 rounds untreated, giving an **observed
  counterfactual** trajectory.

## Contrasts / Hypotheses

Each treatment is compared to control as a **difference-in-differences** (the
treatment's before→after change minus control's before→after change):

- **H1 (petition):** petition's before→after change > control's
- **H2 (roadblock):** roadblock's before→after change > control's
- **H3 (demonstration, exploratory):** demonstration's change > control's

In the model these are the `treatment × is_treatment_round` interaction terms with
control as the reference. **Roadblock is the binding contrast** (smaller effect
than petition), so it drives the required sample size.

## Key Differences from the Original (simr) Power Analysis

The original analysis is the `power` chunk in `ActivismPilotAnalysis.Rmd` (an R
`simr` simulation of a mixed model). This analysis differs in five ways:

1. **A 4th no-treatment control arm, used as the reference.** The original had 3
   arms with demonstration as reference and no untreated control ("baseline" was
   each group's own pre-treatment rounds). A real control that plays all 20 rounds
   untreated is an **observed** counterfactual, so we no longer rely on the
   `period` covariate to represent what would have happened without treatment.
2. **20 rounds (10+10) instead of 14 (7+7)** — more within-person information.
3. **Each treatment-vs-control contrast is powered separately**, rather than the
   single omnibus interaction (which the large petition effect dominated, hiding
   that roadblock needs a bigger sample).
4. **The analysis estimator matches the paper: OLS + CR2 cluster-robust SEs**
   (see Statistical Test), simulated — not the mixed-model LR test the original
   used.
5. **Group-level treatment-effect heterogeneity (`tau`) is swept** as a
   sensitivity parameter — the original random-intercept model implicitly assumed
   `tau = 0` (every group responds identically).

## Data Generating Process

Each simulated experiment is built to match the planned design:

1. For a given number of groups per condition `G`, create 4 arms × `G` groups ×
   4 participants × 20 rounds.
2. Draw random effects and noise:
   - one **group** intercept per group `~ Normal(0, 124.91)`
   - one **participant** intercept per person `~ Normal(0, 111.86)`
   - a **residual** for every observation `~ Normal(0, 403.15)`
   - (if `tau > 0`) one **group treatment-effect deviation** per group
     `~ Normal(0, tau²)`, applied only to the treatment-phase rounds
3. Build the outcome: baseline level + a common `period` decline + each arm's
   treatment effect in rounds 11–20 (control's = 0) + the draws above.

Because the group and participant intercepts are constant within their units, they
add the same amount to a person's before and after rounds and largely **cancel out
of the before→after change** — which is why the treatment effect is precise and why
the estimator choice barely matters (see auxiliary note below).

## Assumptions Built Into the Simulation

| Parameter | Value | Source / Rationale |
|---|---|---|
| Group variance | 124.91 | Pilot fit (`df_long_clean`, 9 groups) |
| Participant variance | 111.86 | Pilot fit |
| Residual variance | 403.15 | Pilot fit |
| Demonstration effect | 3.68 pp | Pilot pre→post effect (7.36), **halved** |
| Petition effect | 14.46 pp | Pilot pre→post effect (28.91), **halved** |
| Roadblock effect | 8.99 pp | Pilot pre→post effect (17.98), **halved** |
| Control net change | 0 pp | Untreated control: no treatment shift (only the common `period` trend) |
| `tau` (heterogeneity) | 0, 3, 5, 8 pp | Unknown (pilot too small to estimate); swept as sensitivity |
| Participants per group | 4 | Study design |
| Rounds per participant | 20 (10 + 10) | Study design |
| Allocation | equal across 4 arms | Balanced design |
| Significance level | α = 0.05, two-sided | Standard |

Effects are **raw percentage-point differences**, not standardised effect sizes.
Halving guards against small-pilot effect-size inflation.

## Statistical Test

**Preferred (and what the paper reports): OLS with CR2 cluster-robust SEs.** Each
replicate is analysed with

```
relative_contribution ~ treatment * is_treatment_round + period
```

fitted by OLS, with **cluster-robust standard errors clustered by group** using the
**CR2** (Bell–McCaffrey) small-sample correction and a Satterthwaite-type reference
distribution. This matches `model_h1_ols` / `model_h1b_ols`
(`lm` + `lm_robust(se_type="CR2")` / `vcovCL(cluster = ~ group_id)`) in
`ActivismPilotAnalysis.Rmd`. Clustering by group makes no assumption about the
within-group correlation structure and absorbs within-participant correlation
(participants are nested in groups). The p-value of each treatment-vs-control
interaction is extracted; power = fraction of replicates with p < 0.05.

**Auxiliary (cross-check only): analytic GLS.** The same design also has a
closed-form mixed-model (known-variance) power, `Cov(β̂) = (X'V⁻¹X)⁻¹`. It agrees
with OLS+CR2 to within Monte-Carlo error at these cluster counts (the treatment ×
round effect is a *within-group* contrast, where OLS is about as efficient as GLS,
and CR2 is well-behaved with dozens of clusters). It is kept as a fast reference
(`--analytic`), not the headline. It would diverge from CR2 only if the true
within-group correlation were not the random-intercept form assumed here (e.g.
serial correlation across rounds) — in which case CR2 is the one to trust.

## Why Not Cohen's *h*?

The outcome *is* a proportion — `relative_contribution` is the share of wage
contributed. So Cohen's *h* (the arcsine effect size for the difference between
two proportions), with a two-proportion power calculation, looks superficially
applicable. We rejected it because of what its two-proportion framework *assumes*,
for three reasons:

1. **It collapses each arm to a single fixed proportion.** The two-proportion test
   assumes each arm has one true proportion `p` and the data are independent draws
   around it. But the contribution share is measured for every participant in every
   round, and it genuinely varies across participants, rounds, and groups — there
   is no single "arm proportion." Cohen's *h* throws that variation away, which is
   exactly the variation that determines how hard the effect is to detect.

2. **Its assumed uncertainty is both the wrong size and the wrong kind.** Because it
   treats each arm as one binomial proportion, the variance is fixed at `p(1−p)`
   (an SD of ≈46% at `p ≈ 0.3`), whereas the observed share has an SD of ≈26%.
   More importantly, the variance that actually matters for the treatment
   comparison is the **between-group / between-participant** variance (we randomise
   groups), not the binomial sampling variance of a single proportion.

3. **It ignores the design structure.** The two-proportion test treats each
   participant as a *single* observation, discarding the 20 repeated rounds per
   person, the nesting of participants within groups, and the difference-in-
   differences (before→after, versus control) that the actual analysis uses. Its
   implied sample sizes (hundreds to thousands per arm) could not be reconciled
   with the design-appropriate analysis even after adjusting for repeated measures
   — because it answers a different question (a marginal two-group proportion
   contrast under binomial assumptions), not the within-group, clustered
   difference-in-differences on many per-participant proportions that we estimate.

We therefore power the **estimator we actually use** (OLS + CR2 on the DiD) by
simulation, which carries the many per-participant proportions, the repeated
measures, the group clustering, and the control comparison.

## `tau` — group treatment-effect heterogeneity

`tau` is the standard deviation, **in percentage points of contribution**, of the
treatment effect across groups. If the roadblock effect averages +9pp:

- `tau = 0` → every roadblock group shifts by exactly +9pp (perfectly uniform).
- `tau = 5` → group shifts are spread ±5pp around +9pp (~68% of groups between +4
  and +14pp) — real, moderate heterogeneity (spread ≈ half the effect).

It matters because groups are the randomisation unit: wider group-to-group spread
means each group is a noisier estimate of the average effect, so more groups are
needed. This spread does **not** cancel out of the before→after change the way the
group/participant *levels* do. It is also where the pilot's imprecise group
variance mostly shows up, so sweeping `tau` is the honest way to express that
uncertainty.

## Sanity Check (ICC)

Before simulating, the script refits the pilot mixed model in Python and reports the
intraclass correlation, which must match the R/`lme4` value from the original
analysis — confirming the same model is being estimated:

| Quantity | Value |
|---|---|
| Group variance | 124.91 |
| Participant variance | 111.86 |
| Residual variance | 403.15 |
| **ICC (Python)** | **0.370** |
| **ICC (R / lme4)** | **0.368** |
| Match (tolerance 0.01) | ✅ |

The treatment effects used in the simulation are also taken from this same fit
(not hardcoded), so the analysis is internally consistent with the pilot.

## Code Structure

Single script: **`power_analysis.py`**.

### `fit_pilot()`
Loads `1.data/clean/df_long.csv`, restricts to complete sessions (`df_long_clean`),
refits the pilot mixed model, prints the **ICC sanity check**, and returns the
variance components and the (halved) treatment effects.

### `build_full_design(G)` / `precompute_cr2(G)`
Build the 4-arm OLS design matrix, and precompute the CR2 (Bell–McCaffrey)
adjustment matrix per condition. Because the design is balanced, the adjustment is
identical for all groups in a condition, so it is computed once — making the
simulation fast.

### `simulate_power_cr2(G, vc, tau, eff, nsim, rng)`
One power estimate: repeatedly generate a dataset (Data Generating Process above),
fit OLS, form the CR2 cluster-robust covariance, and test the roadblock- and
petition-vs-control interactions. Returns the rejection rate for each.

### `table_cr2(...)` — primary
Runs `simulate_power_cr2` across the groups/condition grid × `tau` grid and prints
the power tables and the required groups/condition for 80% and 95% power.

### `cov_beta / power_of / groups_needed / table4 / table5 / table6` — auxiliary
The analytic GLS cross-check (`--analytic`): required-N over the full `tau` range
(Table 4), a variance-level sensitivity (Table 5), and a direct GLS-vs-CR2
agreement table (Table 6).

## Results

OLS + CR2 cluster-robust power (simulated, `nsim = 500`), halved effects. Total
participants = groups/condition × 16 (4 arms × 4 per group).

### Roadblock vs control (binding contrast) — power

| G/cond | Participants | tau=0 | tau=3 | tau=5 | tau=8 |
|---:|---:|:---:|:---:|:---:|:---:|
| 6 | 96 | 0.896 | 0.784 | 0.584 | 0.362 |
| 8 | 128 | 0.976 | 0.868 | 0.728 | 0.518 |
| 10 | 160 | 0.996 | 0.946 | 0.838 | 0.576 |
| 12 | 192 | 1.000 | 0.982 | 0.882 | 0.622 |
| 16 | 256 | 1.000 | 0.998 | 0.972 | 0.774 |
| 20 | 320 | 1.000 | 0.998 | 0.988 | 0.856 |
| 24 | 384 | 1.000 | 1.000 | 0.994 | 0.900 |
| 28 | 448 | 1.000 | 1.000 | 0.998 | 0.962 |

### Petition vs control — power

| G/cond | Participants | tau=0 | tau=3 | tau=5 | tau=8 |
|---:|---:|:---:|:---:|:---:|:---:|
| 6 | 96 | 0.998 | 0.996 | 0.926 | 0.722 |
| 8 | 128 | 1.000 | 1.000 | 0.984 | 0.854 |
| 12 | 192 | 1.000 | 1.000 | 1.000 | 0.960 |
| 16 | 256 | 1.000 | 1.000 | 1.000 | 0.994 |

### Required groups/condition (total participants)

| Contrast | Power | tau=0 | tau=3 | tau=5 | tau=8 |
|---|---|:---:|:---:|:---:|:---:|
| Roadblock vs control | 80% | 6 (96) | 8 (128) | 10 (160) | 20 (320) |
| Roadblock vs control | 95% | 8 (128) | 12 (192) | 16 (256) | 28 (448) |
| Petition vs control | 80% | 6 (96) | 6 (96) | 6 (96) | 8 (128) |
| Petition vs control | 95% | 6 (96) | 6 (96) | 8 (128) | 12 (192) |

**Interpretation.** Roadblock is the binding contrast. Under the optimistic
`tau = 0` assumption, ~128 participants give 95% power — but that assumes all groups
respond identically. With moderate heterogeneity (`tau ≈ 5pp`, spread ≈ half the
effect) the requirement roughly doubles to ~256 (95%) / ~160 (80%). The central
planning figure should be anchored on a defensible `tau`, with the range reported
as a sensitivity. Petition is comfortably powered throughout; demonstration is not
a sizing target (its halved effect is small).

## How to Run

```bash
cd analysis
python3 2.scripts/power_analysis.py                 # primary: OLS + CR2 simulation
python3 2.scripts/power_analysis.py --nsim 1000      # more replicates (less noise)
python3 2.scripts/power_analysis.py --analytic       # also the GLS cross-check tables
```

Design constants (arms, rounds, participants per group), the `tau` grid, and the
groups/condition grid are at the top of the script. Requires `numpy`, `pandas`,
`scipy`, `statsmodels`.
