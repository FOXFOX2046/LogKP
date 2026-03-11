from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from numerical_checks import compare_spiral_sector_moment
import plots
from solver import PassivePressureInput, evaluate_xi, scan_xi
from validation import (
    build_fig15_scan_data,
    build_wall_friction_approximation_table_for_phi as build_approx_table_for_phi,
    evaluate_table2,
    get_paper_conclusion_table,
    load_table4,
)


st.set_page_config(page_title="Verification of Paper Title", layout="wide")


def pretty_force_kn(result_force: float) -> str:
    return f"{result_force:.2f} kN/m"


def pretty_distance(value: float) -> str:
    return f"{value:.3f} m"


def pretty_kp(value: float) -> str:
    return f"{value:.3f}"


def compute_coulomb_kp(phi_deg: float, delta_deg: float, beta_deg: float, theta_deg: float) -> float:
    phi = np.radians(phi_deg)
    delta = np.radians(delta_deg)
    beta = np.radians(beta_deg)
    theta = np.radians(theta_deg)

    numerator = np.cos(theta + phi) ** 2
    radical_term = (
        np.sin(phi + delta) * np.sin(phi + beta)
        / (np.cos(theta - delta) * np.cos(theta - beta))
    )
    radical_term = max(float(radical_term), 0.0)
    denominator = (
        np.cos(theta) ** 2
        * np.cos(theta - delta)
        * (1.0 - np.sqrt(radical_term)) ** 2
    )
    if abs(denominator) < 1e-12:
        raise ValueError("Invalid Coulomb denominator.")
    return float(numerator / denominator)


def build_trace_table(best) -> pd.DataFrame:
    rows = [
        ("Critical ξ", best.trace["xi"], "This is the ξ value that gives the smallest push."),
        ("Which picture fit best", best.case, "Case A means the spiral center is outside. Case B means inside."),
        ("Pp", best.trace["passive_force"], "This is the final passive soil force."),
        ("HRW", best.trace["HRW"], "This is the height used for the Rankine helper triangle."),
        ("L1", best.trace["L1"], "This is the lever arm used in the balance equation."),
        ("r0", best.trace["r0"], "This is the first spiral radius."),
        ("rg", best.trace["rg"], "This is the last spiral radius."),
    ]
    return pd.DataFrame(rows, columns=["Plain name", "Value", "What it means"])


def _coerce_manual_xi(raw_value: str | float, xi_min: float, xi_max: float, fallback: float) -> float:
    try:
        xi_value = float(raw_value)
    except (TypeError, ValueError):
        return fallback
    if abs(xi_value) < 1e-9:
        xi_value = fallback
    return min(max(xi_value, xi_min), xi_max)


@st.cache_data(show_spinner=False)
def load_paper_table(table_number: int) -> tuple[float, pd.DataFrame]:
    return get_paper_conclusion_table(table_number)


@st.cache_data(show_spinner=False)
def load_wall_friction_approximation_table_for_phi(phi_deg: float) -> pd.DataFrame:
    return build_approx_table_for_phi(phi_deg)


@st.cache_data(show_spinner=False)
def load_fig15_data(
    phi_deg: float,
    beta_deg: float,
    omega_deg: float,
    H: float,
    gamma: float,
    q: float,
    xi_min: float,
    xi_max: float,
    n_xi: int,
    cache_version: str = "fig15-ratios-v2",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    return build_fig15_scan_data(
        phi_deg=phi_deg,
        beta_deg=beta_deg,
        omega_deg=omega_deg,
        H=H,
        gamma=gamma,
        q=q,
        xi_min=xi_min,
        xi_max=xi_max,
        n_xi=n_xi,
    )


with st.sidebar:
    st.title("Geotechnical Input Parameters")
    st.write("Adjust the soil, wall, surcharge, and search parameters to evaluate the resulting passive earth pressure response.")

    st.subheader("Wall and Soil")
    H = st.text_input("Wall Height (H)", value="0.24")
    gamma = st.text_input("Soil Unit Weight (γ)", value="15.3")
    phi_deg = st.text_input("Soil Friction Angle (φ, deg)", value="35.5")
    delta_deg = st.text_input("Wall Friction Angle (δ, deg)", value="24.0")

    st.subheader("Ground Shape")
    beta_deg = st.text_input("Backfill Slope Angle (β, deg)", value="0.0")
    omega_deg = st.text_input("Wall Inclination Angle (ω, deg)", value="0.0")
    q = st.text_input("Uniform Surcharge (q)", value="0.0")

    st.subheader("Search Range")
    xi_range_mode = st.radio("Xi Search Range (ξ)", options=["Auto", "Manual"], horizontal=True, index=0)
    xi_min = st.text_input("Minimum Xi (ξ_min)", value="-0.50")
    xi_max = st.text_input("Maximum Xi (ξ_max)", value="0.25")
    n_xi = st.text_input("Number of Xi Points (n_ξ)", value="250")

try:
    H = float(H)
    gamma = float(gamma)
    phi_deg = float(phi_deg)
    delta_deg = float(delta_deg)
    beta_deg = float(beta_deg)
    omega_deg = float(omega_deg)
    q = float(q)
    if xi_range_mode == "Auto":
        xi_min = -3.0 * H
        xi_max = 2.0 * H
    else:
        xi_min = float(xi_min)
        xi_max = float(xi_max)
    n_xi = int(float(n_xi))
except ValueError:
    st.error("Please type numbers only in the Control Panel text boxes.")
    st.stop()

if xi_range_mode == "Auto":
    st.sidebar.caption(f"Auto ξ range: {xi_min:.4f} to {xi_max:.4f}")

inputs = PassivePressureInput(
    H=H,
    gamma=gamma,
    phi_deg=phi_deg,
    delta_deg=delta_deg,
    beta_deg=beta_deg,
    omega_deg=omega_deg,
    q=q,
)

try:
    scan_df, best = scan_xi(inputs, xi_min, xi_max, n_xi)
    check = compare_spiral_sector_moment(
        best.geometry.r0,
        np.radians(phi_deg),
        best.geometry.theta_g,
        best.geometry.lambda_angle,
    )
except Exception as exc:
    st.error(f"I could not build the picture with these settings: {exc}")
    st.stop()

st.title("Verification of A Spreadsheet-Based Technique to Calculate the Passive Soil Pressure Based on the Log-Spiral Method")
st.caption("Verification of the published paper calculations and figures.")

resolved_kp = 2.0 * best.passive_force / (gamma * H**2)

hero_left, hero_mid, hero_right, hero_far_right = st.columns(4)
hero_left.metric("Minimum Pp", pretty_force_kn(best.passive_force))
hero_mid.metric("Critical ξ", pretty_distance(best.xi))
hero_right.metric("Best shape", f"Case {best.case}")
hero_far_right.metric("Resolved Kp", pretty_kp(resolved_kp))

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Theory",
        "Results Summary",
        "Geometry Visualization",
        "Parametric Scan",
        "Rebuilt Fig. 15",
        "Verification",
    ]
)

with tab1:
    st.subheader("Theory")
    st.write("This tab summarizes the theory used in the paper and in this app.")

    st.markdown("**1. Failure mechanism**")
    st.write(
        "The passive wedge is formed by a log-spiral arc plus a straight tangent line. "
        "The spiral is described by `r = r0 * exp(θ tan φ)`."
    )

    st.markdown("**2. Two cases**")
    st.write(
        "Case A: the pole of the spiral is outside the soil mass. "
        "Case B: the pole of the spiral is inside the soil mass."
    )

    st.markdown("**3. What ξ does**")
    st.write(
        "`ξ` controls the trial position of the spiral pole. "
        "For each `ξ`, the app rebuilds the geometry and computes one passive force `Pp`."
    )

    st.markdown("**4. Limit equilibrium**")
    st.write(
        "The paper uses moment equilibrium about the pole `O`. "
        "The resisting and driving moments are balanced to obtain `Pp`."
    )

    st.markdown("**5. Critical solution**")
    st.write(
        "The governing passive force is the minimum value on the `Pp - ξ` curve. "
        "That minimum gives the critical `ξ` and the final solution."
    )

    st.markdown("**6. Passive pressure coefficient**")
    st.write(
        "After finding `Pp`, the coefficient `kp` is computed from "
        "`Pp = 1/2 * kp * γ * H^2`, so `kp = 2 * Pp / (γ * H^2)`."
    )

    st.markdown("**Main equations used in the app**")
    st.code(
        "\n".join(
            [
                "α1 = π/4 - φ/2 + 1/2 asin(sinβ / sinφ) - β/2",
                "α2 = π/4 - φ/2 - 1/2 asin(sinβ / sinφ) + β/2",
                "r = r0 * exp(θ tanφ)",
                "Passive force = min(Pp over ξ)",
                "kp = 2 * Pp / (γ * H^2)",
            ]
        ),
        language="text",
    )

    st.markdown("**In this app**")
    theory_df = pd.DataFrame(
        [
            ("Input symbols", "H, γ, φ, δ, β, ω, q, ξ"),
            ("Geometry output", "r0, rg, θg, HRW"),
            ("Main result", "Pp"),
            ("Table result", "kp"),
        ],
        columns=["Item", "Meaning"],
    )
    st.table(theory_df)

    st.markdown("**SYMBOL ABBR**")
    symbol_df = pd.DataFrame(
        [
            ("H", "Retained soil height"),
            ("γ", "Soil unit weight"),
            ("φ", "Internal friction angle of soil"),
            ("δ", "Wall-soil interface friction angle"),
            ("β", "Backfill slope angle"),
            ("ω", "Wall inclination angle"),
            ("q", "Uniform surcharge"),
            ("ξ", "Trial pole-distance parameter used in the search"),
            ("α1", "Rankine-zone angle from the paper"),
            ("α2", "Companion Rankine-zone angle from the paper"),
            ("η", "Derived angle used in geometry construction"),
            ("r0", "Initial spiral radius at point b"),
            ("rg", "Spiral radius at point g"),
            ("θg", "Rotation angle from b to g on the spiral"),
            ("HRW", "Height of the Rankine passive zone"),
            ("L1", "Moment arm of passive force Pp"),
            ("Pp", "Passive soil force"),
            ("kp", "Coefficient of passive earth pressure"),
            ("O", "Pole of the log spiral"),
        ],
        columns=["Symbol", "Meaning"],
    )
    st.dataframe(symbol_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("What happened?")
    st.write(
        "The app tried many `ξ` positions. Then it picked the one with the smallest soil push on the wall."
    )

    answer_col, note_col = st.columns([1.2, 1])
    with answer_col:
        answer_df = pd.DataFrame(
            [
                ("H", f"{H:.2f} m"),
                ("Pp", pretty_force_kn(best.passive_force)),
                ("Resolved Kp", pretty_kp(resolved_kp)),
                ("Critical ξ", pretty_distance(best.xi)),
                ("Chosen case", f"Case {best.case}"),
                ("HRW", pretty_distance(best.trace["HRW"])),
            ],
            columns=["Thing", "Value"],
        )
        st.table(answer_df)
    with note_col:
        st.write("")

with tab3:
    st.subheader("Dynamic Fig. 2")
    st.caption(
        f"Live geometry reconstructed from the current inputs. The figure updates automatically and is now showing Case {best.case}."
    )

    if "picture_xi" not in st.session_state:
        st.session_state.picture_xi = float(best.xi)
    if "picture_xi_text" not in st.session_state:
        st.session_state.picture_xi_text = f"{best.xi:.4f}"

    mode_col, value_col = st.columns([1, 1.2])
    picture_mode = mode_col.radio(
        "Pole O control",
        options=["Auto (critical ξ)", "Manual ξ"],
        horizontal=True,
    )

    picture_result = best
    if picture_mode == "Manual ξ":
        slider_col, text_col = value_col.columns([1.4, 1])
        slider_value = slider_col.slider(
            "Pull Pole O with ξ",
            min_value=float(xi_min),
            max_value=float(xi_max),
            value=float(_coerce_manual_xi(st.session_state.picture_xi, xi_min, xi_max, best.xi)),
            step=max((xi_max - xi_min) / 400.0, 0.0001),
            key="picture_xi_slider",
        )
        if abs(slider_value - float(st.session_state.picture_xi)) > 1e-9:
            st.session_state.picture_xi = float(slider_value)
            st.session_state.picture_xi_text = f"{slider_value:.4f}"

        manual_text = text_col.text_input("Exact ξ", value=st.session_state.picture_xi_text, key="picture_xi_text_input")
        parsed_text_xi = _coerce_manual_xi(manual_text, xi_min, xi_max, st.session_state.picture_xi)
        if manual_text != st.session_state.picture_xi_text:
            st.session_state.picture_xi_text = manual_text
        if abs(parsed_text_xi - float(st.session_state.picture_xi)) > 1e-9:
            st.session_state.picture_xi = float(parsed_text_xi)
            st.session_state.picture_xi_text = f"{parsed_text_xi:.4f}"

        manual_xi = float(st.session_state.picture_xi)
        try:
            picture_result = evaluate_xi(inputs, manual_xi)
            st.session_state.picture_xi = float(picture_result.xi)
            st.session_state.picture_xi_text = f"{picture_result.xi:.4f}"
        except Exception as exc:
            st.warning(f"This ξ does not create a valid geometry: {exc}")
            fallback_xi = float(best.xi)
            try:
                picture_result = evaluate_xi(inputs, fallback_xi)
            except Exception:
                picture_result = best
            st.session_state.picture_xi = float(picture_result.xi)
            st.session_state.picture_xi_text = f"{picture_result.xi:.4f}"
    else:
        st.session_state.picture_xi = float(best.xi)
        st.session_state.picture_xi_text = f"{best.xi:.4f}"
        value_col.metric("Critical ξ", pretty_distance(best.xi))

    left_pad, figure_col, right_pad = st.columns([1, 2, 1])
    with figure_col:
        st.pyplot(plots.plot_geometry(picture_result), use_container_width=False)
    st.write(
        "The blue curve is `bg`, the orange line is `gf`, the green line is the backfill surface, and the red dot is pole `O`."
    )
    shown_kp = 2.0 * picture_result.passive_force / (gamma * H**2)
    pic_a, pic_b, pic_c, pic_d = st.columns(4)
    pic_a.metric("Shown ξ", pretty_distance(picture_result.xi))
    pic_b.metric("Shown case", f"Case {picture_result.case}")
    pic_c.metric("Shown Pp", pretty_force_kn(picture_result.passive_force))
    pic_d.metric("Shown Kp", pretty_kp(shown_kp))

with tab4:
    st.subheader("Every try the app tested")
    left_pad, chart_col, right_pad = st.columns([1, 2, 1])
    with chart_col:
        st.pyplot(plots.plot_passive_force_scan(scan_df, best), use_container_width=False)
    simple_scan = scan_df.rename(
        columns={
            "xi": "ξ",
            "case": "Shape",
            "passive_force": "Pp",
            "lever_arm": "L1",
        }
    )
    st.dataframe(simple_scan, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("Rebuilt Fig. 15")
    st.caption(
        "This rebuild follows the paper-style `Pp-ξ` comparison across several `δ/φ` ratios and tracks where each curve reaches its minimum."
    )
    st.write(
        "Interpretation: negative `ξ` values place the pole outside the soil mass, while positive `ξ` values place it inside."
    )

    fig15_settings_col, fig15_note_col = st.columns([1.2, 1])
    with fig15_settings_col:
        fig15_mode = st.radio(
            "Figure 15 basis",
            options=["Paper standard rebuild", "Use current sidebar inputs"],
            horizontal=True,
            key="fig15_mode",
        )

    if fig15_mode == "Paper standard rebuild":
        fig15_phi_deg = 30.0
        fig15_beta_deg = 0.0
        fig15_omega_deg = 0.0
        fig15_H = 1.0
        fig15_gamma = 19.0
        fig15_q = 0.0
        fig15_xi_min = -5.0
        fig15_xi_max = 1.0
        fig15_n_xi = 1200
    else:
        fig15_phi_deg = 30.0
        fig15_beta_deg = float(beta_deg)
        fig15_omega_deg = float(omega_deg)
        fig15_H = float(H)
        fig15_gamma = float(gamma)
        fig15_q = float(q)
        fig15_xi_min = float(xi_min)
        fig15_xi_max = float(xi_max)
        fig15_n_xi = max(int(n_xi), 200)

    fig15_scan_df, fig15_summary_df = load_fig15_data(
        phi_deg=fig15_phi_deg,
        beta_deg=fig15_beta_deg,
        omega_deg=fig15_omega_deg,
        H=fig15_H,
        gamma=fig15_gamma,
        q=fig15_q,
        xi_min=fig15_xi_min,
        xi_max=fig15_xi_max,
        n_xi=fig15_n_xi,
        cache_version="fig15-ratios-v2",
    )

    if fig15_mode == "Paper standard rebuild":
        st.caption(
            "Rebuild settings: "
            f"φ = {fig15_phi_deg:.0f}°, "
            f"β = {fig15_beta_deg:.0f}°, "
            f"ω = {fig15_omega_deg:.0f}°, "
            f"H = {fig15_H:g} m, "
            f"γ = {fig15_gamma:g} kN/m³, "
            f"q = {fig15_q:g}."
        )
    else:
        st.caption(
            "Rebuild settings: "
            f"φ = {fig15_phi_deg:.0f}°, "
            f"β = {fig15_beta_deg:.0f}°, "
            f"ω = {fig15_omega_deg:.0f}°, "
            f"H = {fig15_H:g} m, "
            f"γ = {fig15_gamma:g} kN/m³, "
            f"q = {fig15_q:g}."
        )

    st.caption(f"Figure 15 plotting uses fixed soil friction angle φ = {fig15_phi_deg:.0f}°.")

    x_axis_default_min = -6.0
    x_axis_default_max = 6.0
    y_axis_default_min = 0.0
    y_axis_default_max = 140000.0

    axis_col1, axis_col2, axis_col3, axis_col4 = st.columns(4)
    x_axis_min = axis_col1.number_input(
        "X axis min",
        value=round(x_axis_default_min, 3),
        step=0.1,
        key="fig15_x_axis_min",
    )
    x_axis_max = axis_col2.number_input(
        "X axis max",
        value=round(x_axis_default_max, 3),
        step=0.1,
        key="fig15_x_axis_max",
    )
    y_axis_min = axis_col3.number_input(
        "Y axis min",
        value=round(y_axis_default_min, 1),
        step=1000.0,
        key="fig15_y_axis_min",
    )
    y_axis_max = axis_col4.number_input(
        "Y axis max",
        value=round(y_axis_default_max, 1),
        step=1000.0,
        key="fig15_y_axis_max",
    )

    if x_axis_min >= x_axis_max:
        st.warning("X axis max must be greater than X axis min. Showing the automatic range instead.")
        fig15_x_range = None
    else:
        fig15_x_range = (float(x_axis_min), float(x_axis_max))

    if y_axis_min >= y_axis_max:
        st.warning("Y axis max must be greater than Y axis min. Showing the automatic range instead.")
        fig15_y_range = None
    else:
        fig15_y_range = (float(y_axis_min), float(y_axis_max))

    chart_left, chart_center, chart_right = st.columns([0.2, 1.5, 0.2])
    with chart_center:
        fig15_plotter = getattr(plots, "plot_fig15_relationship", None)
        if fig15_plotter is None:
            st.error("The Figure 15 plotting helper is missing from plots.py. Please rerun after the file reloads.")
        else:
            st.plotly_chart(
                fig15_plotter(fig15_scan_df, fig15_summary_df, x_range=fig15_x_range, y_range=fig15_y_range),
                use_container_width=True,
            )

    fig15_metric1, fig15_metric2, fig15_metric3 = st.columns(3)
    critical_span = fig15_summary_df["critical_xi"]
    fig15_metric1.metric("Most outside pole", pretty_distance(float(critical_span.min())))
    fig15_metric2.metric("Most inside pole", pretty_distance(float(critical_span.max())))
    fig15_metric3.metric("Ratios compared", str(len(fig15_summary_df)))

    pretty_fig15_summary = fig15_summary_df.rename(
        columns={
            "delta_over_phi": "δ/φ",
            "delta_deg": "δ (deg)",
            "critical_xi": "Critical ξ",
            "case": "Case",
            "minimum_pp": "Minimum Pp",
            "minimum_pp_N": "Minimum Pp (N)",
            "kp": "Resolved Kp",
        }
    ).copy()
    pretty_fig15_summary["δ (deg)"] = pretty_fig15_summary["δ (deg)"].map(lambda x: round(float(x), 3))
    pretty_fig15_summary["Critical ξ"] = pretty_fig15_summary["Critical ξ"].map(lambda x: round(float(x), 4))
    pretty_fig15_summary["Minimum Pp"] = pretty_fig15_summary["Minimum Pp"].map(lambda x: round(float(x), 4))
    pretty_fig15_summary["Minimum Pp (N)"] = pretty_fig15_summary["Minimum Pp (N)"].map(lambda x: round(float(x), 1))
    pretty_fig15_summary["Resolved Kp"] = pretty_fig15_summary["Resolved Kp"].map(lambda x: round(float(x), 4))
    st.dataframe(
        pretty_fig15_summary[["δ/φ", "δ (deg)", "Critical ξ", "Case", "Minimum Pp (N)", "Resolved Kp"]],
        use_container_width=True,
        hide_index=True,
    )

    st.code(
        "\n".join(
            [
                "For each selected δ/φ ratio:",
                "1. Set δ = φ * (δ/φ)",
                "2. Scan ξ over the requested range",
                "3. Pick the minimum Pp on each curve",
                "4. Read the critical ξ to track the spiral pole location",
            ]
        ),
        language="text",
    )

with tab6:
    st.subheader("Checks for engineers and reviewers")
    st.write("This part keeps the math audit trail visible without crowding the main screen.")

    st.markdown("**Plain-language trace**")
    st.dataframe(build_trace_table(best), use_container_width=True, hide_index=True)

    with st.expander("Equation check: spiral sector moment"):
        check_df = pd.DataFrame(
            [
                ("Paper formula result", check["analytical"]),
                ("Numerical integration result", check["numerical"]),
                ("Difference (%)", check["error_pct"]),
            ],
            columns=["Check", "Value"],
        )
        st.table(check_df)

    with st.expander("Paper validation table"):
        st.dataframe(evaluate_table2(), use_container_width=True, hide_index=True)

    with st.expander("Published larger-scale comparison"):
        st.dataframe(load_table4(), use_container_width=True, hide_index=True)

    with st.expander("Full raw trace"):
        raw_trace = pd.DataFrame([best.trace]).T.reset_index()
        raw_trace.columns = ["Name", "Value"]
        st.dataframe(raw_trace, use_container_width=True, hide_index=True)

    st.markdown("**Paper Tables 6-9**")
    table_choice = st.selectbox(
        "Pick a rebuilt paper table",
        options=[6, 7, 8, 9],
        index=0,
        format_func=lambda x: f"Table {x}",
        key="paper_table_choice",
    )
    phi_choice, table_df = load_paper_table(int(table_choice))
    st.caption(f"Paper Table {table_choice}: coefficient of passive pressure `kp` for `φ = {phi_choice:.0f}°`.")

    pretty_columns = {"delta_over_phi": "δ/φ"}
    for omega_deg in [0, 5, 10, 15]:
        for beta_deg in [0, 5, 10, 15]:
            pretty_columns[f"w={omega_deg}_b={beta_deg}"] = f"ω={omega_deg}, β={beta_deg}"

    st.dataframe(table_df.rename(columns=pretty_columns), use_container_width=True, hide_index=True)

    csv_data = table_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download rebuilt table as CSV",
        data=csv_data,
        file_name=f"paper_table_{table_choice}_phi_{int(phi_choice)}.csv",
        mime="text/csv",
    )

    st.markdown("**Calculation step**")
    explain_col1, explain_col2, explain_col3 = st.columns(3)
    ratio_choice = explain_col1.selectbox(
        "Pick δ/φ",
        options=["0", "1/3", "1/2", "2/3", "1"],
        index=0,
        key="paper_table_ratio_choice",
    )
    omega_choice = explain_col2.selectbox(
        "Pick ω",
        options=[0, 5, 10, 15],
        index=0,
        key="paper_table_omega_choice",
    )
    beta_choice = explain_col3.selectbox(
        "Pick β",
        options=[0, 5, 10, 15],
        index=0,
        key="paper_table_beta_choice",
    )

    ratio_map = {"0": 0.0, "1/3": 1.0 / 3.0, "1/2": 1.0 / 2.0, "2/3": 2.0 / 3.0, "1": 1.0}
    delta_ratio = ratio_map[ratio_choice]
    delta_value = float(phi_choice) * delta_ratio
    explain_inputs = PassivePressureInput(
        H=1.0,
        gamma=1.0,
        phi_deg=float(phi_choice),
        delta_deg=delta_value,
        beta_deg=float(beta_choice),
        omega_deg=float(omega_choice),
        q=0.0,
    )
    _, explain_best = scan_xi(explain_inputs, -20.0, 5.0, 1800)
    explain_kp = 2.0 * explain_best.passive_force / (explain_inputs.gamma * explain_inputs.H**2)

    explain_df = pd.DataFrame(
        [
            ("1. Pick paper table", f"Table {table_choice}"),
            ("2. Use soil friction angle φ", f"{phi_choice:.0f} deg"),
            ("3. Pick δ/φ", ratio_choice),
            ("4. Convert to wall friction δ", f"{phi_choice:.0f} x {ratio_choice} = {delta_value:.3f} deg"),
            ("5. Pick wall inclination ω", f"{omega_choice} deg"),
            ("6. Pick backfill slope β", f"{beta_choice} deg"),
            ("7. Use paper standard values", "H = 1, γ = 1, q = 0"),
            ("8. Number of xi points", "n_ξ = 1800"),
            ("9. Scan trial ξ values", "Search from -20.0 to 5.0"),
            ("10. Find critical ξ", f"{explain_best.xi:.4f}"),
            ("11. Minimum passive force Pp", f"{explain_best.passive_force:.5f}"),
            ("12. Convert Pp to kp", f"kp = 2 x Pp / (γ x H^2) = {explain_kp:.5f}"),
            ("13. Table cell value", f"{explain_kp:.2f}"),
        ],
        columns=["Step", "Result"],
    )
    st.table(explain_df)

    st.code(
        "\n".join(
            [
                "δ = φ * (δ/φ)",
                "scan ξ -> find minimum Pp",
                "kp = 2 * Pp / (γ * H^2)",
            ]
        ),
        language="text",
    )

    st.markdown("**Kp Formula (DM7) Table**")
    st.caption("Approximation valid for wall inclination `ω = 0°` and backfill slope `β = 0°`.")
    table_map = {40.0: 6, 35.0: 7, 30.0: 8, 25.0: 9}
    approx_tabs = st.tabs(["φ = 40°", "φ = 35°", "φ = 30°", "φ = 25°"])
    for idx, phi_value in enumerate([40.0, 35.0, 30.0, 25.0]):
        with approx_tabs[idx]:
            approx_raw_df = load_wall_friction_approximation_table_for_phi(phi_value)
            _, exact_table_df = load_paper_table(table_map[phi_value])
            comparison_df = pd.DataFrame(
                {
                    "δ/φ": approx_raw_df["delta_over_phi"],
                    "Kp (DM7)": approx_raw_df["w=0_b=0"],
                    "Kp (Log-Spiral Method)": exact_table_df["w=0_b=0"],
                    "Difference": (approx_raw_df["w=0_b=0"] - exact_table_df["w=0_b=0"]).round(2),
                }
            )

            st.metric("Condition", "ω = 0°, β = 0°")

            st.markdown("**Comparison**")
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    st.markdown("**Kp (DM7) Calculator**")
    calc_col1, calc_col2 = st.columns(2)
    calc_phi_deg = calc_col1.number_input(
        "Soil Friction Angle φ (deg)",
        min_value=1.0,
        max_value=89.0,
        value=40.0,
        step=1.0,
        key="approx_calc_phi_deg",
    )
    calc_delta_ratio = calc_col2.number_input(
        "Wall Friction Ratio δ/φ",
        min_value=0.0,
        max_value=1.0,
        value=0.33,
        step=0.01,
        key="approx_calc_delta_ratio",
    )
    calc_phi_rad = np.radians(calc_phi_deg)
    calc_ln_kp = np.log((1.0 + np.sin(calc_phi_rad)) / (1.0 - np.sin(calc_phi_rad))) * (
        1.443 * calc_delta_ratio * np.sin(calc_phi_rad) + 1.0
    )
    calc_kp = float(np.exp(calc_ln_kp))
    calc_delta_deg = calc_phi_deg * calc_delta_ratio

    st.code(
        "ln(Kp) = ln((1 + sin(φ)) / (1 - sin(φ))) * [1.443 * (δ / φ) * sin(φ) + 1]",
        language="text",
    )
    calc_result_df = pd.DataFrame(
        [
            ("Soil friction angle", f"φ = {calc_phi_deg:.2f}°"),
            ("Wall friction ratio", f"δ/φ = {calc_delta_ratio:.3f}"),
            ("Wall friction angle", f"δ = {calc_delta_deg:.3f}°"),
            ("Natural log result", f"ln(Kp) = {calc_ln_kp:.5f}"),
            ("Approximate passive coefficient", f"Kp = {calc_kp:.5f}"),
        ],
        columns=["Item", "Value"],
    )
    st.table(calc_result_df)

    st.markdown("**Kp (Coulomb Theory) Calculator**")
    st.caption("Based on the Coulomb passive earth pressure expression shown in the reference figure.")
    coulomb_col1, coulomb_col2 = st.columns(2)
    coulomb_phi_deg = coulomb_col1.number_input(
        "Soil Friction Angle φ (deg) - Coulomb",
        min_value=1.0,
        max_value=89.0,
        value=35.0,
        step=1.0,
        key="coulomb_phi_deg",
    )
    coulomb_delta_ratio = coulomb_col2.number_input(
        "Wall Friction Ratio δ/φ - Coulomb",
        min_value=0.0,
        max_value=1.0,
        value=0.33,
        step=0.01,
        key="coulomb_delta_ratio",
    )
    coulomb_col3, coulomb_col4 = st.columns(2)
    coulomb_beta_deg = coulomb_col3.number_input(
        "Backfill Slope β (deg) - Coulomb",
        min_value=0.0,
        max_value=89.0,
        value=0.0,
        step=1.0,
        key="coulomb_beta_deg",
    )
    coulomb_theta_deg = coulomb_col4.number_input(
        "Wall Inclination θ (deg) - Coulomb",
        min_value=-45.0,
        max_value=45.0,
        value=0.0,
        step=1.0,
        key="coulomb_theta_deg",
    )

    try:
        coulomb_delta_deg = coulomb_phi_deg * coulomb_delta_ratio
        coulomb_kp = compute_coulomb_kp(
            phi_deg=coulomb_phi_deg,
            delta_deg=coulomb_delta_deg,
            beta_deg=coulomb_beta_deg,
            theta_deg=coulomb_theta_deg,
        )
        coulomb_pp = 0.5 * coulomb_kp * gamma * H**2
        st.code(
            "Kp = cos^2(θ + φ) / [cos^2(θ) cos(θ - δ) (1 - sqrt((sin(φ + δ) sin(φ + β)) / (cos(θ - δ) cos(θ - β)) ))^2]",
            language="text",
        )
        coulomb_result_df = pd.DataFrame(
            [
                ("Soil friction angle", f"φ = {coulomb_phi_deg:.2f}°"),
                ("Wall friction ratio", f"δ/φ = {coulomb_delta_ratio:.3f}"),
                ("Wall friction angle", f"δ = {coulomb_delta_deg:.2f}°"),
                ("Backfill slope angle", f"β = {coulomb_beta_deg:.2f}°"),
                ("Wall inclination angle", f"θ = {coulomb_theta_deg:.2f}°"),
                ("Passive earth pressure coefficient", f"Kp = {coulomb_kp:.5f}"),
                ("Passive force with current H and γ", f"Pp = {coulomb_pp:.5f}"),
            ],
            columns=["Item", "Value"],
        )
        st.table(coulomb_result_df)
        st.caption("Coulomb note: values are typically considered satisfactory for `δ < φ/3`.")
    except Exception as exc:
        st.warning(f"Coulomb calculator could not evaluate these inputs: {exc}")
