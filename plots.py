from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

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


def plot_fig15_relationship(
    scan_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    x_range: tuple[float, float] | None = None,
    y_range: tuple[float, float] | None = None,
):
    cmap = plt.get_cmap("viridis")
    ratios = summary_df["delta_ratio"].tolist()
    colors = [cmap(idx) for idx in np.linspace(0.1, 0.9, max(len(ratios), 2))]
    color_map = {
        ratio: f"rgba({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)}, 1.0)"
        for ratio, color in zip(ratios, colors)
    }
    fig = go.Figure()

    for ratio in ratios:
        ratio_scan = scan_df.loc[scan_df["delta_ratio"] == ratio]
        ratio_summary = summary_df.loc[summary_df["delta_ratio"] == ratio].iloc[0]
        color = color_map[ratio]
        fig.add_trace(
            go.Scatter(
                x=ratio_scan["xi"],
                y=ratio_scan["passive_force_N"],
                mode="lines",
                name=f"δ/φ={ratio_summary['delta_over_phi']}",
                line={"color": color, "width": 2},
                hovertemplate="δ/φ=%{fullData.name}<br>ξ=%{x:.4f}<br>Pp=%{y:.1f} N<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[ratio_summary["critical_xi"]],
                y=[ratio_summary["minimum_pp_N"]],
                mode="markers+text",
                name=f"Minimum {ratio_summary['delta_over_phi']}",
                text=["Minimum"],
                textposition="top right",
                marker={"color": color, "size": 9, "line": {"color": "#0f172a", "width": 1}},
                showlegend=False,
                hovertemplate="Minimum<br>ξ=%{x:.4f}<br>Pp=%{y:.1f} N<extra></extra>",
            )
        )

    fig.add_vline(x=0.0, line_width=1.2, line_dash="dash", line_color="#64748b")
    fig.add_annotation(xref="paper", yref="paper", x=0.01, y=0.98, text="Pole inside soil", showarrow=False)
    fig.add_annotation(xref="paper", yref="paper", x=0.99, y=0.98, text="Pole outside soil", showarrow=False, xanchor="right")
    fig.update_layout(
        title="Rebuilt Fig. 15 - Interface Friction vs Pole Location",
        xaxis_title="ξ",
        yaxis_title="Passive force (N)",
        template="plotly_white",
        legend={"x": 1.02, "y": 1.0, "xanchor": "left", "yanchor": "top"},
        margin={"l": 60, "r": 140, "t": 60, "b": 50},
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.25)")
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.25)",
        tickformat=".0f",
        exponentformat="none",
        separatethousands=False,
    )
    if x_range is not None:
        fig.update_xaxes(range=[x_range[0], x_range[1]])
    if y_range is not None:
        fig.update_yaxes(range=[y_range[0], y_range[1]])
    return fig
