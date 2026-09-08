"""
Power / sample-size analysis for the planned 4-ARM activism study.
See power_analysis_notes.md for full detail and rationale.

Design: control (reference) + demonstration + petition + roadblock; 20 rounds
(10 baseline + 10 treatment); 4 participants/group; groups are randomised.
Sizing targets: petition- and roadblock-vs-control (demonstration exploratory).

Steps:
  1. Refit the pilot mixed model -> variance components + treatment effects.
     Sanity check: ICC must match the R/lme4 value (0.368).
  2. PRIMARY: simulate power under the estimator the paper actually uses --
     OLS + CR2 cluster-robust SEs clustered by group (matches model_h1_ols /
     model_h1b_ols / lm_robust(se_type="CR2") in ActivismPilotAnalysis.Rmd).
     Data are generated from the pilot's random-effects world; each replicate is
     analysed with OLS + CR2 and the treatment-vs-control interaction is tested.
     Reports power and required groups/condition across tau.
  3. (--analytic) Auxiliary cross-check: the analytic GLS (mixed-model,
     known-variance) power. It agrees with CR2 at these cluster counts and is
     kept only as a fast reference, not the headline.

Key points vs the original simr analysis (ActivismPilotAnalysis.Rmd):
  - adds a no-treatment control arm as reference (cleaner DiD identification)
  - 20 rounds not 14; powers each treatment-vs-control contrast, not the omnibus
  - analyses with OLS + CR2 (the reported estimator), via simulation
  - sweeps group-level treatment-effect heterogeneity `tau` (original assumed 0)

Main assumptions: effects HALVED for conservatism; control's net pre->post
change ~0 (so each DiD = that treatment's own pilot effect); pilot variance
components carry over; balanced allocation; group-clustered CR2 inference.
"""

import os
import argparse
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------------
# Planned 4-arm design constants
# ----------------------------------------------------------------------------
CONDS = ["control", "demonstration", "petition", "roadblock"]  # control = reference
N_PART = 4          # participants per group
N_ROUND = 20        # rounds per participant
TREAT_FROM = 11     # is_treatment_round = 1 for rounds >= 11  (10 baseline + 10)

PARAMS = ["Intercept", "demonstration", "petition", "roadblock",
          "itr", "demo:itr", "pet:itr", "road:itr", "period"]
N_FIXED = len(PARAMS)
IDX = {p: i for i, p in enumerate(PARAMS)}

ICC_R = 0.368       # value reported by R/lme4 in ActivismPilotAnalysis.Rmd
TAUS = [0, 3, 5, 8, 12]      # assumed group treatment-effect heterogeneity (pp)
SIM_TAUS = [0, 3, 5, 8]      # tau values simulated for the primary CR2 table
SIM_GS = [6, 8, 10, 12, 14, 16, 20, 24, 28, 32]   # groups/condition grid (CR2 sim)
VAR_SCALES = [0.75, 1.0, 1.5, 2.0]   # multiplier on ALL variance components
                                     # (overall noise level; ICC held fixed)


# ----------------------------------------------------------------------------
# Step 1: refit the pilot model  ->  variance components, effects, ICC check
# ----------------------------------------------------------------------------
def fit_pilot():
    here = os.path.dirname(os.path.abspath(__file__))
    csv = os.path.join(here, "..", "1.data", "clean", "df_long.csv")
    d = pd.read_csv(csv)
    # df_long_clean = complete sessions only (matches the R primary analysis)
    dc = d[d["questionnaire.1.player.q3_personal_cost"].notna()].copy()
    dc["pcode"] = dc["participant.code"].astype(str)
    dc["ta"] = pd.Categorical(dc["treatment_assigned"],
                              categories=["demonstration", "petition", "roadblock"])

    md = smf.mixedlm("relative_contribution ~ ta*is_treatment_round + period",
                     dc, groups=dc["group_id"], re_formula="1",
                     vc_formula={"pcode": "0 + C(pcode)"})
    mf = md.fit(reml=True, method="lbfgs", maxiter=500)

    v_g = float(mf.cov_re.iloc[0, 0])          # group intercept variance
    v_p = float(mf.vcomp[0])                    # participant intercept variance
    v_e = float(mf.scale)                       # residual variance
    icc = (v_g + v_p) / (v_g + v_p + v_e)

    # treatment-vs-control effects = each treatment's own pre->post effect
    # (the untreated control's net change is ~0, so DiD-vs-control = simple effect)
    p = mf.params
    eff_full = {
        "demonstration": float(p["is_treatment_round"]),
        "petition":      float(p["is_treatment_round"] + p["ta[T.petition]:is_treatment_round"]),
        "roadblock":     float(p["is_treatment_round"] + p["ta[T.roadblock]:is_treatment_round"]),
    }

    print("=" * 70)
    print("STEP 1  -  PILOT MODEL REFIT  (sanity check vs R/lme4)")
    print("=" * 70)
    print(f"  data: df_long_clean  ({dc['group_id'].nunique()} groups, "
          f"{dc['participant.code'].nunique()} participants, {len(dc)} rows)")
    print(f"  variance components:  group={v_g:.2f}  participant={v_p:.2f}  "
          f"residual={v_e:.2f}")
    print(f"  ICC (Python) = {icc:.3f}   vs   ICC (R/lme4) = {ICC_R:.3f}   "
          f"-> {'MATCH' if abs(icc - ICC_R) < 0.01 else 'MISMATCH!'}")
    print(f"  pilot treatment effects (pp, full):  "
          + "  ".join(f"{k}={v:.2f}" for k, v in eff_full.items()))
    print(f"  -> HALVED for the power calc:         "
          + "  ".join(f"{k}={v/2:.2f}" for k, v in eff_full.items()))
    return v_g, v_p, v_e, {k: v / 2 for k, v in eff_full.items()}


# ----------------------------------------------------------------------------
# Step 2: analytic power machinery for the 4-arm design
# ----------------------------------------------------------------------------
def group_design(cond):
    """Fixed-effect design rows for one group in a given condition."""
    d = int(cond == "demonstration"); p = int(cond == "petition"); r = int(cond == "roadblock")
    rows = []
    for _ in range(N_PART):
        for period in range(1, N_ROUND + 1):
            itr = 1 if period >= TREAT_FROM else 0
            rows.append([1, d, p, r, itr, d*itr, p*itr, r*itr, period])
    return np.array(rows, float)


def group_Vinv(v_g, v_p, v_e, tau):
    """Inverse within-group covariance block. tau = SD of the GROUP-level random
    slope on is_treatment_round (treatment-effect heterogeneity across groups)."""
    n = N_PART * N_ROUND
    V = np.full((n, n), v_g)                        # group intercept
    for k in range(N_PART):                         # participant intercepts
        s = slice(k*N_ROUND, (k+1)*N_ROUND)
        V[s, s] += v_p
    if tau > 0:                                     # group random slope on itr
        itr = np.array([1.0 if (t + 1) >= TREAT_FROM else 0.0
                        for _ in range(N_PART) for t in range(N_ROUND)])
        V += (tau**2) * np.outer(itr, itr)
    V += v_e * np.eye(n)                            # residual
    return np.linalg.inv(V)


def cov_beta(G, v_g, v_p, v_e, tau):
    """Cov(beta_hat) = (X' V^-1 X)^-1 for G groups PER CONDITION (balanced)."""
    Vinv = group_Vinv(v_g, v_p, v_e, tau)
    M = np.zeros((N_FIXED, N_FIXED))
    for cond in CONDS:
        Xg = group_design(cond)
        M += G * (Xg.T @ Vinv @ Xg)
    return np.linalg.inv(M)


def power_of(effect, se, df, alpha=0.05):
    """Two-sided power for a single contrast, small-sample t-reference."""
    ncp = effect / se
    tc = stats.t.ppf(1 - alpha/2, df)
    return stats.nct.sf(tc, df, ncp) + stats.nct.cdf(-tc, df, ncp)


CONTRAST_COL = {"petition": IDX["pet:itr"], "roadblock": IDX["road:itr"]}


def groups_needed(effect, col, vc, tau, target, alpha=0.05, cap=200):
    v_g, v_p, v_e = vc
    for G in range(2, cap):
        cov = cov_beta(G, v_g, v_p, v_e, tau)
        se = float(np.sqrt(cov[col, col]))
        if power_of(effect, se, 4*G - N_FIXED, alpha) >= target:
            return G
    return None


# ----------------------------------------------------------------------------
# Step 3: build Table 4
# ----------------------------------------------------------------------------
def table4(vc, eff):
    print("\n" + "=" * 70)
    print("TABLE 4  -  required sample size vs group treatment-effect")
    print("           heterogeneity (tau).  HALVED effects, t-reference.")
    print("=" * 70)
    print("  4 conditions x 4 participants/group.  'g/cond' = groups per condition;")
    print("  total participants = g/cond x 4 conditions x 4 participants = g x 16.")
    print(f"  effects (pp, halved):  petition={eff['petition']:.2f}  "
          f"roadblock={eff['roadblock']:.2f}\n")

    for target in (0.80, 0.95):
        print(f"  --- {int(target*100)}% power ---")
        print(f"  {'tau(pp)':>7} | {'roadblock vs control':>22} | {'petition vs control':>22}")
        print("  " + "-" * 56)
        for tau in TAUS:
            cells = []
            for trt in ("roadblock", "petition"):
                g = groups_needed(eff[trt], CONTRAST_COL[trt], vc, tau, target)
                cells.append(f"{g}/cond -> {g*16} ppl" if g else ">200/cond")
            print(f"  {tau:>7} | {cells[0]:>22} | {cells[1]:>22}")
        print()


# ----------------------------------------------------------------------------
# Simulation matching the ACTUAL analysis estimator:
#   OLS  +  CR2 cluster-robust SEs clustered by group  (= lm + lm_robust CR2)
# Data are generated from the realistic random-effects world (group + participant
# + residual + tau slope); each replicate is then analysed with OLS/CR2, exactly
# as the preregistered model does. The analytic GLS tables above are the (more
# optimistic) known-variance reference.
# ----------------------------------------------------------------------------
def build_full_design(G):
    """Full 4-arm design matrix, with group- and participant-id per row."""
    blocks, cluster, part, gid, pid = [], [], [], 0, 0
    for c in CONDS:
        for _ in range(G):
            blocks.append(group_design(c))
            cluster += [gid] * (N_PART * N_ROUND)
            for _ in range(N_PART):
                part += [pid] * N_ROUND
                pid += 1
            gid += 1
    return np.vstack(blocks), np.array(cluster), np.array(part)


def precompute_cr2(G):
    """Design-only quantities for OLS + CR2. Because the design is balanced, the
    CR2 adjustment A = (I - H_gg)^{-1/2} is identical for all groups in a
    condition, so it is computed once per condition (fast)."""
    X, cluster, part = build_full_design(G)
    XtX_inv = np.linalg.inv(X.T @ X)
    A_cond, XgT_cond = {}, {}
    for c in CONDS:
        Xg = group_design(c)
        H = Xg @ XtX_inv @ Xg.T                       # cluster leverage block
        w, V = np.linalg.eigh(np.eye(len(Xg)) - H)
        w = np.clip(w, 1e-10, None)
        A_cond[c] = (V * (1.0 / np.sqrt(w))) @ V.T     # (I - H)^{-1/2}, Bell-McCaffrey
        XgT_cond[c] = Xg.T
    cond_of = [c for c in CONDS for _ in range(G)]
    rows_of = [np.where(cluster == g)[0] for g in range(len(cond_of))]
    return X, XtX_inv, cluster, part, A_cond, XgT_cond, cond_of, rows_of


def _beta_true(eff):
    b = np.zeros(N_FIXED)
    b[IDX["Intercept"]] = 34.0          # baseline level (irrelevant to interaction power)
    b[IDX["period"]] = -2.946           # common time trend
    b[IDX["demo:itr"]] = eff["demonstration"]
    b[IDX["pet:itr"]] = eff["petition"]
    b[IDX["road:itr"]] = eff["roadblock"]
    return b


def simulate_power_cr2(G, vc, tau, eff, nsim, rng, alpha=0.05):
    """Rejection rate for roadblock- and petition-vs-control interactions under
    OLS + CR2, data generated from the mixed-effects world."""
    v_g, v_p, v_e = vc
    X, XtX_inv, cluster, part, A_cond, XgT_cond, cond_of, rows_of = precompute_cr2(G)
    n_clusters, n_parts = len(cond_of), part.max() + 1
    df = n_clusters - N_FIXED                          # Satterthwaite ~ n_clusters-k here
    tcrit = stats.t.ppf(1 - alpha/2, df)
    beta_t = _beta_true(eff)
    itr = X[:, IDX["itr"]]
    col = {"roadblock": IDX["road:itr"], "petition": IDX["pet:itr"]}
    rej = {k: 0 for k in col}
    for _ in range(nsim):
        y = (X @ beta_t
             + rng.normal(0, v_g**0.5, n_clusters)[cluster]
             + rng.normal(0, v_p**0.5, n_parts)[part]
             + rng.normal(0, v_e**0.5, len(X)))
        if tau > 0:
            y = y + rng.normal(0, tau, n_clusters)[cluster] * itr
        beta = XtX_inv @ (X.T @ y)
        resid = y - X @ beta
        meat = np.zeros((N_FIXED, N_FIXED))
        for g in range(n_clusters):
            c = cond_of[g]
            w = XgT_cond[c] @ (A_cond[c] @ resid[rows_of[g]])
            meat += np.outer(w, w)
        V = XtX_inv @ meat @ XtX_inv
        for k, j in col.items():
            if abs(beta[j] / np.sqrt(V[j, j])) > tcrit:
                rej[k] += 1
    return {k: rej[k] / nsim for k in col}, df


def table_cr2(vc, eff, nsim, Gs=SIM_GS, taus=SIM_TAUS, seed=42):
    """PRIMARY RESULT. OLS + CR2 cluster-robust power (the estimator the paper
    reports), simulated across groups/condition x tau, for roadblock- and
    petition-vs-control. Prints the power grid and the required groups/condition
    (and total participants) for 80% and 95% power."""
    rng = np.random.default_rng(seed)
    res = {}
    for G in Gs:
        for tau in taus:
            p, _ = simulate_power_cr2(G, vc, tau, eff, nsim, rng)
            res[(G, tau)] = p
    print("\n" + "=" * 70)
    print(f"OLS + CR2 CLUSTER-ROBUST POWER (simulated, nsim={nsim}).  HALVED effects.")
    print("           Estimator = the preregistered model (clustered by group).")
    print("=" * 70)
    for contrast in ("roadblock", "petition"):
        print(f"\n  {contrast.capitalize()} vs control  -  power   (ppl = groups/cond x 16)")
        print("  " + f"{'G/cond':>6} {'ppl':>5} |" + "".join(f"{'tau='+str(t):>8}" for t in taus))
        print("  " + "-" * (14 + 8 * len(taus)))
        for G in Gs:
            cells = "".join(f"{res[(G, t)][contrast]:>8.3f}" for t in taus)
            print("  " + f"{G:>6} {16*G:>5} |" + cells)

    print("\n  Required groups/condition (total participants) for target power:")
    for contrast in ("roadblock", "petition"):
        print(f"    {contrast} vs control:")
        for target in (0.80, 0.95):
            parts = []
            for tau in taus:
                g = next((G for G in Gs if res[(G, tau)][contrast] >= target), None)
                parts.append(f"tau{tau}={g} ({16*g})" if g else f"tau{tau}=>{max(Gs)}")
            print(f"      {int(target*100)}%:  " + "   ".join(parts))
    return res


def table6(vc, eff, nsim, seed=42):
    """Auxiliary cross-check: OLS+CR2 simulated power vs analytic GLS
    (reference), for roadblock & petition vs control, at tau = 0 and 5."""
    rng = np.random.default_rng(seed)
    v_g, v_p, v_e = vc
    Gs = [6, 8, 10, 12, 16, 20, 24]
    print("\n" + "=" * 70)
    print(f"TABLE 6  -  power under the ACTUAL estimator (OLS + CR2 cluster-robust")
    print(f"           by group), simulated, nsim={nsim}.  'GLS' = analytic reference.")
    print("=" * 70)
    print("  HALVED effects.  ppl = groups/cond x 16.\n")
    for tau in (0, 5):
        print(f"  --- tau = {tau} pp ---")
        print(f"  {'G/cond':>6} {'ppl':>5} | {'road GLS':>9} {'road CR2':>9} | "
              f"{'pet GLS':>8} {'pet CR2':>8}")
        print("  " + "-" * 54)
        for G in Gs:
            cov = cov_beta(G, v_g, v_p, v_e, tau); dfa = 4*G - N_FIXED
            gls = {k: power_of(eff[k], np.sqrt(cov[CONTRAST_COL[k], CONTRAST_COL[k]]), dfa)
                   for k in ("roadblock", "petition")}
            sim, _ = simulate_power_cr2(G, vc, tau, eff, nsim, rng)
            print(f"  {G:>6} {16*G:>5} | {gls['roadblock']:>9.3f} {sim['roadblock']:>9.3f} | "
                  f"{gls['petition']:>8.3f} {sim['petition']:>8.3f}", flush=True)
        print()


def table5(vc, eff):
    """Second sensitivity: required N for ROADBLOCK (the binding contrast) as the
    overall noise level (all variance components scaled, ICC fixed) is varied,
    crossed with tau. Cells = groups per condition (x16 for total participants)."""
    v_g, v_p, v_e = vc
    print("\n" + "=" * 70)
    print("TABLE 5  -  variance-component sensitivity (ROADBLOCK vs control).")
    print("           Rows = noise multiplier on all variances (ICC held fixed);")
    print("           columns = tau.  Cells = groups/condition.  HALVED effects.")
    print("=" * 70)
    print("  total participants = groups/condition x 16.   '>200' = off the grid.\n")
    for target in (0.80, 0.95):
        print(f"  --- {int(target*100)}% power ---")
        print("  " + f"{'var x':>6} |" + "".join(f"{'tau='+str(t):>8}" for t in TAUS))
        print("  " + "-" * (8 + 8 * len(TAUS)))
        for s in VAR_SCALES:
            vcs = (s * v_g, s * v_p, s * v_e)
            cells = []
            for tau in TAUS:
                g = groups_needed(eff["roadblock"], CONTRAST_COL["roadblock"],
                                  vcs, tau, target)
                cells.append(f"{g}" if g else ">200")
            print("  " + f"{s:>6.2f} |" + "".join(f"{c:>8}" for c in cells))
        print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsim", type=int, default=500)
    ap.add_argument("--analytic", action="store_true",
                    help="also print the analytic GLS cross-check tables (fast)")
    a = ap.parse_args()

    v_g, v_p, v_e, eff = fit_pilot()
    vc = (v_g, v_p, v_e)
    table_cr2(vc, eff, a.nsim)            # PRIMARY: OLS + CR2 (the reported estimator)
    if a.analytic:
        table4(vc, eff)                  # auxiliary: analytic GLS required-N (full tau range)
        table5(vc, eff)                  # auxiliary: analytic variance sensitivity
        table6(vc, eff, a.nsim)          # auxiliary: GLS-vs-CR2 agreement check
