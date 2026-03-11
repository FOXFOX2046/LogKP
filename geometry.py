from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, exp, pi, sin, sqrt, tan

import numpy as np


@dataclass(frozen=True)
class GeometryState:
    case: str
    xi: float
    alpha_1: float
    alpha_2: float
    eta: float
    wall_length: float
    x_offset: float
    pole_x: float
    pole_y: float
    a: tuple[float, float]
    b: tuple[float, float]
    g: tuple[float, float]
    f: tuple[float, float]
    f_prime: tuple[float, float]
    r0: float
    rg: float
    theta_g: float
    lambda_angle: float
    ag: float
    fg: float
    hrw: float
    spiral_points: np.ndarray
    wedge_polygon: np.ndarray


def rankine_angles(phi: float, beta: float) -> tuple[float, float]:
    arc_term = asin(sin(beta) / sin(phi))
    alpha_1 = pi / 4 - phi / 2 + 0.5 * arc_term - beta / 2
    alpha_2 = pi / 4 - phi / 2 - 0.5 * arc_term + beta / 2
    return alpha_1, alpha_2


def rankine_kp(phi: float, beta: float) -> float:
    root_term = sqrt(max(cos(beta) ** 2 - cos(phi) ** 2, 0.0))
    return (cos(beta) + root_term) / max(cos(beta) - root_term, 1e-12)


def spiral_sector_moment(r0: float, phi: float, theta_g: float, lambda_angle: float) -> float:
    tan_phi = tan(phi)
    denom = 3 * (1 + 9 * tan_phi**2)
    term_1 = (r0**3 * cos(lambda_angle) / denom) * (
        1 + exp(3 * theta_g * tan_phi) * (3 * tan_phi * sin(theta_g) - cos(theta_g))
    )
    term_2 = (r0**3 * sin(lambda_angle) / denom) * (
        exp(3 * theta_g * tan_phi) * (sin(theta_g) + 3 * tan_phi * cos(theta_g)) - 3 * tan_phi
    )
    return term_1 + term_2


def polygon_area_centroid(points: np.ndarray) -> tuple[float, tuple[float, float]]:
    x = points[:, 0]
    y = points[:, 1]
    shifted_x = np.roll(x, -1)
    shifted_y = np.roll(y, -1)
    cross = x * shifted_y - shifted_x * y
    signed_area = 0.5 * cross.sum()
    area = abs(signed_area)
    if area < 1e-12:
        raise ValueError("Degenerate polygon.")
    cx = ((x + shifted_x) * cross).sum() / (6 * signed_area)
    cy = ((y + shifted_y) * cross).sum() / (6 * signed_area)
    return area, (cx, cy)


def build_geometry(
    H: float,
    phi: float,
    beta: float,
    omega: float,
    xi: float,
    n_points: int = 180,
) -> GeometryState:
    alpha_1, alpha_2 = rankine_angles(phi, beta)
    eta = alpha_1 - beta
    wall_length = H / cos(omega)
    x_offset = wall_length * sin(omega)

    if abs(xi) < 1e-9:
        raise ValueError("xi must be non-zero.")

    if xi < 0:
        case = "A"
        xi_abs = abs(xi)
        xa = xi_abs * cos(eta)
        ya = xi_abs * sin(eta)
        xb = xa + abs(x_offset)
        yb = ya + H
        r0 = sqrt((H + ya) ** 2 + (xa + x_offset) ** 2)
        lambda_angle = asin(max(min(xb / r0, 1.0), -1.0))
        theta_g = asin(max(min(yb / r0, 1.0), -1.0)) - eta
        rg = r0 * exp(theta_g * tan(phi))
        xg = rg * cos(eta)
        yg = rg * sin(eta)
        ag = rg - xi_abs
        fg = ag * sin(alpha_1)
        xf = xg - fg * sin(beta)
        yf = yg - fg * cos(beta)
    else:
        case = "B"
        xa = -(xi * cos(eta))
        ya = -(xi * sin(eta))
        xb = x_offset + xa
        yb = H + ya
        r0 = sqrt(xb**2 + yb**2)
        lambda_angle = asin(max(min(xb / r0, 1.0), -1.0))
        theta_g = pi / 2 - lambda_angle - eta
        rg = r0 * exp(theta_g * tan(phi))
        xg = rg * cos(eta)
        yg = rg * sin(eta)
        ag = abs(xi) + rg
        fg = ag * sin(alpha_1)
        xf = xg - fg * sin(beta)
        yf = yg - fg * cos(beta)

    # In the paper's geometry, the backfill line descends with positive β in the
    # computational coordinate system used here, so the sign is negative.
    f_prime = (xg, ya - (xg - xa) * tan(beta))
    hrw = fg / cos(beta)
    theta_values = np.linspace(0.0, theta_g, n_points)
    r_values = r0 * np.exp(theta_values * tan(phi))
    spiral_points = np.column_stack(
        (
            r_values * np.sin(theta_values + lambda_angle),
            r_values * np.cos(theta_values + lambda_angle),
        )
    )

    a = (xa, ya)
    b = (xb, yb)
    g = (xg, yg)
    f = (xf, yf)
    wedge_polygon = np.vstack([a, b, spiral_points[1:], f])

    return GeometryState(
        case=case,
        xi=xi,
        alpha_1=alpha_1,
        alpha_2=alpha_2,
        eta=eta,
        wall_length=wall_length,
        x_offset=x_offset,
        pole_x=0.0,
        pole_y=0.0,
        a=a,
        b=b,
        g=g,
        f=f,
        f_prime=f_prime,
        r0=r0,
        rg=rg,
        theta_g=theta_g,
        lambda_angle=lambda_angle,
        ag=ag,
        fg=fg,
        hrw=hrw,
        spiral_points=spiral_points,
        wedge_polygon=wedge_polygon,
    )
