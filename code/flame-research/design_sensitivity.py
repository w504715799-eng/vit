"""Analytic design sensitivity only; no model inference or observed research data.

Normal approximations for one prespecified paired comparison. These are not
power guarantees for clustered data, multiple gates, or the full protocol.
Run: python3 code/flame-research/design_sensitivity.py
"""
import json
from math import ceil, sqrt
from statistics import NormalDist


def design_report():
    normal = NormalDist()
    z_alpha = normal.inv_cdf(0.95)
    z_power = normal.inv_cdf(0.80)
    iou_delta = 0.03
    fpr_delta = 0.05
    return {
        "kind": "analytic_sensitivity_not_experimental_results",
        "alpha_one_sided": 0.05,
        "target_power": 0.80,
        "iou_assumptions": [
            {
                "paired_difference_sd": sd,
                "n_approx": ceil(((z_alpha + z_power) * sd / iou_delta) ** 2),
                "power_at_n59_approx": round(
                    normal.cdf(iou_delta * sqrt(59) / sd - z_alpha), 4
                ),
            }
            for sd in (0.10, 0.15, 0.20)
        ],
        "fpr_assumptions": [
            {
                "paired_discordance_rate": q,
                "n_approx": ceil(
                    (z_alpha + z_power) ** 2
                    * (q - fpr_delta ** 2) / fpr_delta ** 2
                ),
            }
            for q in (0.05, 0.10, 0.20)
        ],
        "tpr_difference_one_sided_halfwidth_n200_q004": (
            z_alpha * sqrt(0.04 / 200)
        ),
        "assumptions": [
            "Independent paired units; unknown variances supplied as scenarios.",
            "Binary difference variance is q minus delta squared.",
            "Known-variance normal approximation, not exact McNemar power.",
            "No allowance for multiple baselines or sequential gate passage.",
            "No estimated parameter comes from the fire datasets.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(design_report(), ensure_ascii=False, indent=2))
