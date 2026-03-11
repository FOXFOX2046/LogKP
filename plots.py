from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from solver import PassivePressureResult


def plot_passive_force_scan(scan_df: pd.DataFrame, best: PassivePressureResult):
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    colors = scan_df["case"].map({"A": "#d97706", "B": "#2563eb"})
    ax.scatter(scan_df["xi"], scan_df["passive_force"], c=colors, s=20, alpha=0.75)
    ax.plot(scan_df["xi"], scan_df["passive_force"], color="#334155", linewidth=1)
    ax.scatter([best.xi], [best.passive_force], color="#dc2626", s=70, zorder=4)
    ax.set_xlabel("xi")
    ax.set_ylabel("Passive force Pp")
    ax.set_title("Passive Force vs ξ", fontsize=14)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig


def plot_geometry(result: PassivePressureResult):
    g = result.geometry
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    wall_x = [g.a[0], g.b[0]]
    wall_y = [g.a[1], g.b[1]]
    tangent_x = [g.g[0], g.f[0]]
    tangent_y = [g.g[1], g.f[1]]
    backfill_x = [g.a[0], g.f_prime[0]]
    backfill_y = [g.a[1], g.f_prime[1]]

    # Construction lines similar to the paper's geometry sketches.
    ax.plot([0.0, g.a[0]], [0.0, g.a[1]], color="#94a3b8", linewidth=1.2, linestyle="--", label="Oa")
    ax.plot([0.0, g.b[0]], [0.0, g.b[1]], color="#cbd5e1", linewidth=1.0, linestyle="--", label="Ob")
    ax.plot([0.0, g.g[0]], [0.0, g.g[1]], color="#64748b", linewidth=1.2, linestyle="--", label="Og")

    ax.plot(wall_x, wall_y, color="#0f172a", linewidth=3, label="Wall ab")
    ax.plot(g.spiral_points[:, 0], g.spiral_points[:, 1], color="#1d4ed8", linewidth=2.5, label="Log spiral bg")
    ax.plot(tangent_x, tangent_y, color="#ea580c", linewidth=2.2, label="Tangent gf")
    ax.plot(backfill_x, backfill_y, color="#16a34a", linewidth=2.2, label="Backfill af'")

    polygon = g.wedge_polygon
    ax.fill(polygon[:, 0], polygon[:, 1], color="#93c5fd", alpha=0.25, label="Slip mass abge")
    ax.scatter([0.0], [0.0], color="#dc2626", s=55, zorder=6, label="Pole O")
    point_x = [g.a[0], g.b[0], g.g[0], g.f[0], g.f_prime[0]]
    point_y = [g.a[1], g.b[1], g.g[1], g.f[1], g.f_prime[1]]
    ax.scatter(point_x, point_y, color="#111827", s=18, zorder=5)

    labels = {
        "O": (0.0, 0.0),
        "a": g.a,
        "b": g.b,
        "g": g.g,
        "f": g.f,
        "f'": g.f_prime,
    }
    for name, (x, y) in labels.items():
        ax.text(x, y, f" {name}", fontsize=10, ha="left", va="bottom")

    all_x = np.concatenate([polygon[:, 0], g.spiral_points[:, 0], np.array([0.0, g.f_prime[0]])])
    all_y = np.concatenate([polygon[:, 1], g.spiral_points[:, 1], np.array([0.0, g.f_prime[1]])])
    x_span = max(all_x.max() - all_x.min(), 1e-6)
    y_span = max(all_y.max() - all_y.min(), 1e-6)
    x_pad = 0.06 * x_span
    y_pad = 0.06 * y_span
    ax.set_xlim(all_x.min() - x_pad, all_x.max() + x_pad)
    ax.set_ylim(all_y.min() - y_pad, all_y.max() + y_pad)
    ax.invert_yaxis()

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(
        f"Dynamic Fig. 2 - Pole {'Outside' if result.case == 'A' else 'Inside'} Soil Mass (Case {result.case})",
        fontsize=11,
    )
    ax.grid(alpha=0.25)
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        borderaxespad=0.0,
        fontsize=8,
    )
    fig.tight_layout(rect=(0.0, 0.0, 0.82, 1.0))
    return fig
