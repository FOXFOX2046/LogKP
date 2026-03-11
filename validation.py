from __future__ import annotations

from math import exp, log, radians, sin
from pathlib import Path

import pandas as pd

from solver import PassivePressureInput, evaluate_xi, scan_xi


DATA_DIR = Path(__file__).resolve().parent / "data"
PAPER_CONCLUSION_TABLES = {
    6: 40.0,
    7: 35.0,
    8: 30.0,
    9: 25.0,
}
TABLE_COLUMNS = [
    "w=0_b=0",
    "w=0_b=5",
    "w=0_b=10",
    "w=0_b=15",
    "w=5_b=0",
    "w=5_b=5",
    "w=5_b=10",
    "w=5_b=15",
    "w=10_b=0",
    "w=10_b=5",
    "w=10_b=10",
    "w=10_b=15",
    "w=15_b=0",
    "w=15_b=5",
    "w=15_b=10",
    "w=15_b=15",
]
PAPER_CONCLUSION_VALUES = {
    6: {
        "0": [4.61, 5.47, 6.45, 7.55, 4.10, 4.80, 5.61, 6.54, 3.70, 4.32, 5.00, 5.78, 3.46, 4.03, 4.65, 5.31],
        "1/3": [7.58, 9.27, 11.20, 13.50, 6.44, 7.84, 9.50, 11.50, 5.56, 6.76, 8.17, 9.72, 4.86, 5.92, 7.13, 8.50],
        "1/2": [9.74, 12.20, 14.60, 17.40, 8.14, 10.00, 12.30, 14.70, 6.97, 8.56, 10.50, 12.50, 6.03, 7.42, 9.05, 10.90],
        "2/3": [12.20, 15.20, 18.60, 22.60, 10.30, 12.70, 15.50, 18.80, 8.67, 10.80, 13.20, 16.00, 7.46, 9.30, 11.50, 13.80],
        "1": [18.80, 23.70, 29.70, 35.90, 15.60, 19.50, 24.20, 29.60, 13.00, 16.30, 20.30, 25.80, 11.00, 13.90, 17.20, 21.00],
    },
    7: {
        "0": [3.70, 4.29, 4.95, 5.63, 3.34, 3.86, 4.42, 5.02, 3.10, 3.56, 4.06, 4.58, 2.90, 3.36, 3.83, 4.30],
        "1/3": [5.42, 6.44, 7.54, 8.70, 4.75, 5.64, 6.60, 7.64, 4.21, 5.00, 5.86, 6.78, 3.79, 4.50, 5.29, 6.12],
        "1/2": [6.54, 7.85, 9.36, 10.90, 5.67, 6.78, 8.01, 9.37, 5.00, 6.00, 7.06, 8.20, 4.46, 5.34, 6.31, 7.36],
        "2/3": [7.80, 9.36, 11.10, 13.00, 6.76, 8.12, 9.62, 11.20, 5.92, 7.16, 8.48, 9.90, 5.22, 6.30, 7.52, 8.85],
        "1": [10.80, 13.10, 15.70, 18.50, 9.20, 11.20, 13.40, 15.80, 8.26, 9.69, 11.60, 13.70, 7.13, 8.75, 10.60, 12.10],
    },
    8: {
        "0": [3.00, 3.43, 3.86, 4.29, 2.76, 3.15, 3.54, 3.92, 2.59, 2.96, 3.33, 3.68, 2.47, 2.83, 3.19, 3.53],
        "1/3": [4.02, 4.66, 5.33, 5.97, 3.61, 4.20, 4.79, 5.37, 3.28, 3.81, 4.37, 4.90, 3.02, 3.52, 4.04, 4.54],
        "1/2": [4.62, 5.40, 6.20, 7.00, 4.13, 4.81, 5.53, 6.23, 3.73, 4.36, 5.02, 5.66, 3.41, 4.00, 4.61, 5.21],
        "2/3": [5.27, 6.17, 7.11, 8.03, 4.71, 5.52, 6.36, 7.18, 4.22, 4.69, 5.75, 6.52, 3.83, 4.51, 5.23, 5.93],
        "1": [6.68, 7.90, 9.20, 10.40, 5.88, 6.97, 8.10, 9.22, 5.34, 6.35, 7.41, 8.47, 4.78, 5.70, 6.65, 7.60],
    },
    9: {
        "0": [2.47, 2.77, 3.06, 3.30, 2.31, 2.60, 2.87, 3.11, 2.19, 2.48, 2.75, 3.00, 2.12, 2.41, 2.68, 2.91],
        "1/3": [3.06, 3.48, 3.88, 4.20, 2.81, 3.20, 3.57, 3.88, 2.61, 3.00, 3.34, 3.63, 2.46, 2.81, 3.15, 3.44],
        "1/2": [3.40, 3.86, 4.32, 4.70, 3.10, 3.55, 3.97, 4.33, 2.87, 3.29, 3.70, 4.02, 2.68, 3.08, 3.47, 3.80],
        "2/3": [3.73, 4.28, 4.81, 5.24, 3.41, 3.91, 4.40, 4.80, 3.13, 3.60, 4.05, 4.43, 2.92, 3.37, 3.80, 4.16],
        "1": [4.52, 5.21, 5.88, 6.43, 4.05, 4.68, 5.29, 5.79, 3.70, 4.27, 4.83, 5.30, 3.40, 3.95, 4.48, 4.91],
    },
}
FIG15_DELTA_RATIOS = (0.0, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0)


def load_table2() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "table2_validation.csv")


def load_table4() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "table4_validation.csv")


def evaluate_table2() -> pd.DataFrame:
    df = load_table2().copy()
    calculated = []
    errors = []
    for row in df.itertuples(index=False):
        inputs = PassivePressureInput(
            H=row.H_m,
            gamma=row.gamma_kN_m3,
            phi_deg=row.phi_deg,
            delta_deg=row.delta_deg,
            beta_deg=row.beta_deg,
            omega_deg=row.omega_deg,
            q=row.q_kPa,
        )
        result = evaluate_xi(inputs, row.xi_m)
        calculated_force_n = result.passive_force * 1000.0
        calculated.append(calculated_force_n)
        errors.append(100.0 * (calculated_force_n - row.measured_force) / row.measured_force)
    df["calculated_force_current_solver_N"] = calculated
    df["error_pct_current_solver"] = errors
    return df


def build_conclusion_table(phi_deg: float, xi_min: float = -20.0, xi_max: float = 5.0, n_xi: int = 1800) -> pd.DataFrame:
    delta_ratios = [0.0, 1.0 / 3.0, 1.0 / 2.0, 2.0 / 3.0, 1.0]
    betas = [0.0, 5.0, 10.0, 15.0]
    omegas = [0.0, 5.0, 10.0, 15.0]

    rows: list[dict[str, float | str]] = []
    for ratio in delta_ratios:
        delta_deg = phi_deg * ratio
        row: dict[str, float | str] = {"delta_over_phi": _ratio_label(ratio)}
        for omega_deg in omegas:
            for beta_deg in betas:
                inputs = PassivePressureInput(
                    H=1.0,
                    gamma=1.0,
                    phi_deg=phi_deg,
                    delta_deg=delta_deg,
                    beta_deg=beta_deg,
                    omega_deg=omega_deg,
                    q=0.0,
                )
                _, best = scan_xi(inputs, xi_min=xi_min, xi_max=xi_max, n_xi=n_xi)
                kp = 2.0 * best.passive_force / (inputs.gamma * inputs.H**2)
                row[f"w={int(omega_deg)}_b={int(beta_deg)}"] = round(kp, 2)
        rows.append(row)
    return pd.DataFrame(rows)


def get_paper_conclusion_table(table_number: int) -> tuple[float, pd.DataFrame]:
    if table_number not in PAPER_CONCLUSION_TABLES:
        raise ValueError(f"Unsupported paper table number: {table_number}")
    phi_deg = PAPER_CONCLUSION_TABLES[table_number]
    return phi_deg, build_conclusion_table(phi_deg)


def load_published_conclusion_table(table_number: int) -> pd.DataFrame:
    if table_number not in PAPER_CONCLUSION_VALUES:
        raise ValueError(f"Unsupported paper table number: {table_number}")
    rows: list[dict[str, float | str]] = []
    for ratio_label, values in PAPER_CONCLUSION_VALUES[table_number].items():
        row = {"delta_over_phi": ratio_label}
        row.update(dict(zip(TABLE_COLUMNS, values)))
        rows.append(row)
    return pd.DataFrame(rows)


def evaluate_conclusion_table(table_number: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    _, calculated_df = get_paper_conclusion_table(table_number)
    published_df = load_published_conclusion_table(table_number)

    comparison = published_df[["delta_over_phi"]].copy()
    for column in TABLE_COLUMNS:
        comparison[column] = calculated_df[column] - published_df[column]

    summary_rows = []
    diff_values = comparison[TABLE_COLUMNS]
    summary_rows.append(
        {
            "metric": "max_abs_diff",
            "value": round(float(diff_values.abs().to_numpy().max()), 4),
        }
    )
    summary_rows.append(
        {
            "metric": "mean_abs_diff",
            "value": round(float(diff_values.abs().to_numpy().mean()), 4),
        }
    )
    summary_rows.append(
        {
            "metric": "matching_cells_within_0.05",
            "value": int((diff_values.abs() <= 0.05).sum().sum()),
        }
    )
    summary_rows.append(
        {
            "metric": "total_cells",
            "value": int(diff_values.size),
        }
    )
    return pd.DataFrame(summary_rows), comparison


def build_wall_friction_approximation_table() -> pd.DataFrame:
    phi_values = [40.0, 35.0, 30.0, 25.0]
    delta_ratios = [0.0, 1.0 / 3.0, 1.0 / 2.0, 2.0 / 3.0, 1.0]

    rows: list[dict[str, float | str]] = []
    for ratio in delta_ratios:
        row: dict[str, float | str] = {"delta_over_phi": _ratio_label(ratio)}
        for phi_deg in phi_values:
            phi_rad = radians(phi_deg)
            log_rankine_kp = log((1.0 + sin(phi_rad)) / (1.0 - sin(phi_rad)))
            log_kp = log_rankine_kp * (1.443 * ratio * sin(phi_rad) + 1.0)
            row[f"phi={int(phi_deg)}"] = round(exp(log_kp), 2)
        rows.append(row)
    return pd.DataFrame(rows)


def build_wall_friction_approximation_table_for_phi(phi_deg: float) -> pd.DataFrame:
    full_table = build_wall_friction_approximation_table()
    column = f"phi={int(phi_deg)}"
    return full_table[["delta_over_phi", column]].rename(columns={column: "w=0_b=0"})


def build_fig15_scan_data(
    phi_deg: float = 30.0,
    beta_deg: float = 0.0,
    omega_deg: float = 0.0,
    H: float = 1.0,
    gamma: float = 19.0,
    q: float = 0.0,
    xi_min: float = -5.0,
    xi_max: float = 1.0,
    n_xi: int = 1200,
    delta_ratios: tuple[float, ...] = FIG15_DELTA_RATIOS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    scan_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, float | str]] = []

    for ratio in delta_ratios:
        delta_deg = phi_deg * ratio
        inputs = PassivePressureInput(
            H=H,
            gamma=gamma,
            phi_deg=phi_deg,
            delta_deg=delta_deg,
            beta_deg=beta_deg,
            omega_deg=omega_deg,
            q=q,
        )
        scan_df, best = scan_xi(inputs, xi_min=xi_min, xi_max=xi_max, n_xi=n_xi)
        plot_df = scan_df.copy()
        plot_df["delta_over_phi"] = _ratio_label(ratio)
        plot_df["delta_ratio"] = ratio
        plot_df["delta_deg"] = delta_deg
        plot_df["passive_force_N"] = plot_df["passive_force"] * 1000.0
        scan_frames.append(plot_df)

        summary_rows.append(
            {
                "delta_over_phi": _ratio_label(ratio),
                "delta_ratio": ratio,
                "delta_deg": delta_deg,
                "critical_xi": best.xi,
                "case": best.case,
                "minimum_pp": best.passive_force,
                "minimum_pp_N": best.passive_force * 1000.0,
                "kp": 2.0 * best.passive_force / (gamma * H**2),
            }
        )

    scan_data = pd.concat(scan_frames, ignore_index=True)
    summary_df = pd.DataFrame(summary_rows)
    return scan_data, summary_df


def _ratio_label(value: float) -> str:
    if abs(value - 0.5) < 1e-9:
        return "0.5"
    if abs(value - 0.75) < 1e-9:
        return "0.75"
    if abs(value - 1.25) < 1e-9:
        return "1.25"
    if abs(value - 1.5) < 1e-9:
        return "1.5"
    if abs(value - 0.0) < 1e-9:
        return "0"
    if abs(value - (1.0 / 3.0)) < 1e-9:
        return "1/3"
    if abs(value - (2.0 / 3.0)) < 1e-9:
        return "2/3"
    if abs(value - 1.0) < 1e-9:
        return "1"
    if abs(value - 2.0) < 1e-9:
        return "2"
    return f"{value:.2f}"
