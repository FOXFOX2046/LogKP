from solver import PassivePressureInput, evaluate_xi, scan_xi
from validation import build_conclusion_table


def test_table2_mid_case_runs():
    inputs = PassivePressureInput(H=0.24, gamma=15.3, phi_deg=35.5, delta_deg=24.0)
    result = evaluate_xi(inputs, -0.2)
    assert result.case == "A"
    assert result.passive_force > 0
    assert result.lever_arm > 0
    assert abs(result.passive_force - 3.6144) < 0.02


def test_xi_scan_finds_valid_minimum():
    inputs = PassivePressureInput(H=0.24, gamma=15.3, phi_deg=35.5, delta_deg=24.0)
    scan_df, best = scan_xi(inputs, -0.4, 0.2, 120)
    assert not scan_df.empty
    assert best.passive_force == scan_df["passive_force"].min()


def test_conclusion_table_matches_table6_baseline():
    table = build_conclusion_table(40.0, xi_min=-20.0, xi_max=5.0, n_xi=800)
    row = table.loc[table["delta_over_phi"] == "0"].iloc[0]
    assert abs(row["w=0_b=0"] - 4.61) < 0.05
