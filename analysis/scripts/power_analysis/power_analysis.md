# Power Analysis and Analysis Workflow

## Hypotheses

$$\bar{q}_{RB} < \bar{q}_{BASE} < \bar{q}_{PET} < \bar{q}_{DEMO} \quad \text{(H1: contributions)}$$

$$\bar{a}_{RB} < \bar{a}_{DEMO} < \bar{a}_{PET} \quad \text{(H2: individual turnout)}$$

$$\bar{W}_{RB} < \bar{W}_{DEMO} < \bar{W}_{BASE} \leq \bar{W}_{PET} \quad \text{(H3: welfare)}$$

---

## Phase 1: Power Analysis (pre-data)

### Step 1: Assume true means per arm

| Arm  | $\bar{q}$ (H1) | $\bar{a}$ (H2) | $\bar{W}$ (H3) |
|------|----------------|----------------|----------------|
| BASE | 25             | —              | ?              |
| PET  | 25             | 50             | ?              |
| DEMO | 35.5           | 40 / 10        | ?              |
| RB   | 24 / 20        | 5.3            | ?              |

Note: $\bar{a}_{k}$ is the average individual probability of engaging in arm $k$.

### Step 2: Required sample size (`power.prop.test`)

For each pairwise contrast we use `power.prop.test` to find the minimum number of observations per group required to detect the difference at $\alpha = 0.05$, power $= 0.80$, one-sided. This is preferred over Cohen's $d$ for proportion outcomes because variance depends on the mean — `power.prop.test` accounts for this via the arcsine transformation.

| Hypothesis | Contrast            | $p_1$ | $p_2$ | $n$ per group |
|------------|---------------------|-------|-------|---------------|
| H1         | BASE vs DEMO        | 0.25  | 0.355 | 236           |
| H1         | BASE vs RB (RB=20)  | 0.25  | 0.20  | 862           |
| H1         | BASE vs RB (RB=24)  | 0.25  | 0.24  | 22,872        |
| H2         | PET vs RB           | 0.50  | 0.053 | 12            |
| H2         | PET vs DEMO (40%)   | 0.50  | 0.40  | 305           |
| H2         | PET vs DEMO (10%)   | 0.50  | 0.10  | 16            |

Key findings:

- **BASE vs RB (RB=24)** requires $n = 22{,}872$ per group — infeasible, confirming RB=24 is too close to baseline to detect
- **BASE vs RB (RB=20)** requires $n = 862$ — still well above the planned sample, so this contrast will be underpowered
- **PET vs DEMO (40%)** requires $n = 305$ — also above the planned sample
- **PET vs RB** and **PET vs DEMO (10%)** require only $n = 12$ and $n = 16$ — easily detectable

### Step 3: Simulation

For each scenario and iteration:

1. Generate a fake dataset: 4 groups per arm, 4 people per group, multiple periods per person, with outcomes drawn from the assumed means in Step 1
2. Sanity check: verify simulated means $\approx$ assumed means
3. Run the relevant regression (see Phase 2) with SEs clustered at group level and record $p$-value
4. Repeat 1000 times

$$\text{Power} = \frac{\text{iterations where } p < 0.05}{\text{1000}}$$

---

## Phase 2: Analysis (post-data)

### Step 4: Raw means

Report observed means per arm for $q_{it}$, $\bar{a}_{it}$, and $W_{it}$.

### Step 5: Regressions

**H1 and H3** — OLS with period fixed effects, SEs clustered at group level:

$$y_{it} = \beta_0 + \beta_1 \cdot PET_i + \beta_2 \cdot DEMO_i + \beta_3 \cdot RB_i + \gamma_t + \varepsilon_{it}$$

where $y_{it} = q_{it}$ for H1 and $y_{it} = W_{it}$ for H3. Test $H_0: \beta_1 = \beta_2 = \beta_3 = 0$.

**H2** (individual level) — OLS with period fixed effects, SEs clustered at group level:

$$\bar{a}_{it} = \alpha + \beta_1 \bar{q}_{-i,t} + \beta_2 NegDev_{it} + \beta_3 PosDev_{it} + \beta_4 Treatment_i + \gamma_t + \varepsilon_{it}$$

Test $H_0: \beta_4 = 0$.
