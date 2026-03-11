from __future__ import annotations

from dataclasses import asdict, dataclass
from math import cos, degrees, sin

import numpy as np
import pandas as pd

from geometry import GeometryState, build_geometry, polygon_area_centroid, rankine_kp


@dataclass(frozen=True)
class PassivePressureInput:
    H: float
    gamma: float
    phi_deg: float
    delta_deg: float
    beta_deg: float = 0.0
    omega_deg: float = 0.0
    q: float = 0.0


@dataclass(frozen=True)
class PassivePressureResult:
    case: str
    xi: float
    passive_force: float
    lever_arm: float
    weight_moment: float
    rankine_force: float
    rankine_moment: float
    surcharge_force: float
    surcharge_moment: float
    rankine_surcharge_force: float
    rankine_surcharge_moment: float
    wedge_area: float
    wedge_centroid_x: float
    geometry: GeometryState
    trace: dict[str, float | str]


def _radians(inputs: PassivePressureInput) -> tuple[float, float, float, float]:
    return np.radians([inputs.phi_deg, inputs.delta_deg, inputs.beta_deg, inputs.omega_deg])


def evaluate_xi(inputs: PassivePressureInput, xi: float) -> PassivePressureResult:
    phi, delta, beta, omega = _radians(inputs)
    geometry = build_geometry(inputs.H, phi, beta, omega, xi)
    kp = rankine_kp(phi, beta)
    v = geometry.eta - delta + omega
    wall_length = geometry.wall_length

    if geometry.case == "A":
        l1 = abs(xi) * sin(v) + (2.0 / 3.0) * wall_length * cos(delta)
        lrw = geometry.rg * sin(geometry.alpha_1) - geometry.fg / 3.0
        lq = geometry.rg * sin(geometry.alpha_1) - geometry.fg / 2.0
        af = abs(geometry.f[0] - geometry.a[0]) / max(cos(beta), 1e-12)
        af_prime = af + geometry.fg * np.tan(beta)
        surcharge_force = inputs.q * af_prime
        surcharge_moment = surcharge_force * abs((geometry.a[0] + geometry.f_prime[0]) / 2.0)
    else:
        l1 = (2.0 / 3.0) * wall_length * cos(delta) - abs(xi) * sin(v)
        lrw = (2.0 / 3.0) * geometry.fg - abs(xi) * sin(geometry.alpha_1)
        lq = 0.5 * geometry.fg - abs(xi) * sin(geometry.alpha_1)
        af = geometry.ag * cos(geometry.alpha_1)
        af_prime = af + geometry.fg * np.tan(beta)
        surcharge_force = inputs.q * af_prime
        surcharge_moment = surcharge_force * abs((abs(geometry.a[0]) + abs(geometry.f_prime[0])) / 2.0 - abs(geometry.a[0]))

    if l1 <= 0:
        raise ValueError("Unstable geometry produced a non-positive lever arm.")

    wedge_area, wedge_centroid = polygon_area_centroid(geometry.wedge_polygon)
    weight_force = wedge_area * inputs.gamma
    weight_moment = weight_force * wedge_centroid[0]

    rankine_force = 0.5 * kp * inputs.gamma * geometry.hrw**2 * cos(beta)
    rankine_moment = rankine_force * lrw
    rankine_surcharge_force = inputs.q * cos(beta) * kp * geometry.hrw
    rankine_surcharge_moment = rankine_surcharge_force * lq

    passive_force = (
        weight_moment
        + rankine_moment
        + surcharge_moment
        + rankine_surcharge_moment
    ) / l1

    trace = {
        "case": geometry.case,
        "xi": xi,
        "alpha_1_deg": degrees(geometry.alpha_1),
        "alpha_2_deg": degrees(geometry.alpha_2),
        "eta_deg": degrees(geometry.eta),
        "r0": geometry.r0,
        "rg": geometry.rg,
        "theta_g_deg": degrees(geometry.theta_g),
        "fg": geometry.fg,
        "HRW": geometry.hrw,
        "kp_rankine": kp,
        "L1": l1,
        "LRW": lrw,
        "Lq": lq,
        "wedge_area": wedge_area,
        "wedge_centroid_x": wedge_centroid[0],
        "weight_moment": weight_moment,
        "rankine_force": rankine_force,
        "rankine_moment": rankine_moment,
        "surcharge_force": surcharge_force,
        "surcharge_moment": surcharge_moment,
        "rankine_surcharge_force": rankine_surcharge_force,
        "rankine_surcharge_moment": rankine_surcharge_moment,
        "passive_force": passive_force,
    }

    return PassivePressureResult(
        case=geometry.case,
        xi=xi,
        passive_force=passive_force,
        lever_arm=l1,
        weight_moment=weight_moment,
        rankine_force=rankine_force,
        rankine_moment=rankine_moment,
        surcharge_force=surcharge_force,
        surcharge_moment=surcharge_moment,
        rankine_surcharge_force=rankine_surcharge_force,
        rankine_surcharge_moment=rankine_surcharge_moment,
        wedge_area=wedge_area,
        wedge_centroid_x=wedge_centroid[0],
        geometry=geometry,
        trace=trace,
    )


def scan_xi(inputs: PassivePressureInput, xi_min: float, xi_max: float, n_xi: int) -> tuple[pd.DataFrame, PassivePressureResult]:
    xi_values = np.linspace(xi_min, xi_max, n_xi)
    rows: list[dict[str, float | str]] = []
    best: PassivePressureResult | None = None

    for xi in xi_values:
        if abs(xi) < 1e-8:
            continue
        try:
            result = evaluate_xi(inputs, float(xi))
        except Exception:
            continue
        if not np.isfinite(result.passive_force) or result.passive_force <= 0:
            continue
        row = {
            "xi": result.xi,
            "case": result.case,
            "passive_force": result.passive_force,
            "lever_arm": result.lever_arm,
            "weight_moment": result.weight_moment,
            "rankine_moment": result.rankine_moment,
            "surcharge_moment": result.surcharge_moment,
            "rankine_surcharge_moment": result.rankine_surcharge_moment,
        }
        rows.append(row)
        if best is None or result.passive_force < best.passive_force:
            best = result

    if best is None:
        raise ValueError("No valid xi values were found in the requested range.")

    frame = pd.DataFrame(rows).sort_values("xi").reset_index(drop=True)
    return frame, best
