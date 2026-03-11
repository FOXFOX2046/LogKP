from __future__ import annotations

from math import exp, sin, tan

import numpy as np

from geometry import spiral_sector_moment


def numerical_spiral_sector_moment(r0: float, phi: float, theta_g: float, lambda_angle: float, n: int = 4000) -> float:
    theta = np.linspace(0.0, theta_g, n)
    r = r0 * np.exp(theta * tan(phi))
    integrand = (1.0 / 3.0) * r**3 * np.sin(theta + lambda_angle)
    return np.trapz(integrand, theta)


def compare_spiral_sector_moment(r0: float, phi: float, theta_g: float, lambda_angle: float) -> dict[str, float]:
    analytical = spiral_sector_moment(r0, phi, theta_g, lambda_angle)
    numerical = numerical_spiral_sector_moment(r0, phi, theta_g, lambda_angle)
    error_pct = 100.0 * abs(analytical - numerical) / max(abs(numerical), 1e-12)
    return {
        "analytical": analytical,
        "numerical": numerical,
        "error_pct": error_pct,
    }
