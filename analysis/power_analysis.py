import numpy as np
from itertools import combinations


# --- Assumed true means ---
# H1: relative contributions (%)
# H2a: individual activism turnout (%)
# BASE excluded from H2a (no activism in baseline)

SCENARIOS = {
    "S1 (RB=24, DEMO_a=40)": {
        "q": {"BASE": 25, "PET": 25, "DEMO": 35.5, "RB": 24},
        "a": {"PET": 50, "DEMO": 40, "RB": 5.3},
    },
    "S2 (RB=24, DEMO_a=10)": {
        "q": {"BASE": 25, "PET": 25, "DEMO": 35.5, "RB": 24},
        "a": {"PET": 50, "DEMO": 10, "RB": 5.3},
    },
    "S3 (RB=20, DEMO_a=40)": {
        "q": {"BASE": 25, "PET": 25, "DEMO": 35.5, "RB": 20},
        "a": {"PET": 50, "DEMO": 40, "RB": 5.3},
    },
    "S4 (RB=20, DEMO_a=10)": {
        "q": {"BASE": 25, "PET": 25, "DEMO": 35.5, "RB": 20},
        "a": {"PET": 50, "DEMO": 10, "RB": 5.3},
    },
}

# Within-group SDs — adjust if better estimates are available
SIGMA_Q = 15.0   # within-group SD for contributions (%)
SIGMA_A = 20.0   # within-group SD for activism turnout (%)


def cohens_f(means, sigma_within):
    """Cohen's f = std of group means / within-group SD."""
    arr = np.array(list(means.values()))
    return np.std(arr, ddof=0) / sigma_within


def cohens_d(mu1, mu2, sigma_within):
    """Cohen's d = absolute difference / within-group SD."""
    return abs(mu1 - mu2) / sigma_within


def benchmark_f(f):
    if f < 0.10:
        return "< small"
    elif f < 0.25:
        return "small"
    elif f < 0.40:
        return "medium"
    else:
        return "large"


def benchmark_d(d):
    if d < 0.20:
        return "< small"
    elif d < 0.50:
        return "small"
    elif d < 0.80:
        return "medium"
    else:
        return "large"


def print_pairwise(means, sigma_within):
    """Print Cohen's d for all pairwise contrasts."""
    arms = list(means.keys())
    col = 20
    print(f"  {'Contrast':<{col}} {'d':>6}  {'Benchmark'}")
    print(f"  {'-'*40}")
    for a, b in combinations(arms, 2):
        d = cohens_d(means[a], means[b], sigma_within)
        print(f"  {a+' vs '+b:<{col}} {d:>6.3f}  {benchmark_d(d)}")


if __name__ == "__main__":
    print(f"Within-group SD assumptions: σ_q={SIGMA_Q}, σ_a={SIGMA_A}\n")

    # --- Omnibus Cohen's f ---
    print(f"{'Scenario':<30} {'f (H1)':<12} {'Benchmark':<12} {'f (H2a)':<12} {'Benchmark'}")
    print("-" * 80)
    for name, s in SCENARIOS.items():
        f_q = cohens_f(s["q"], SIGMA_Q)
        f_a = cohens_f(s["a"], SIGMA_A)
        print(f"{name:<30} {f_q:<12.3f} {benchmark_f(f_q):<12} {f_a:<12.3f} {benchmark_f(f_a)}")

    # --- Pairwise Cohen's d ---
    for name, s in SCENARIOS.items():
        print(f"\n{name}")
        print(f"  H1 (contributions, σ={SIGMA_Q}):")
        print_pairwise(s["q"], SIGMA_Q)
        print(f"  H2a (turnout, σ={SIGMA_A}):")
        print_pairwise(s["a"], SIGMA_A)
