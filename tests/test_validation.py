from validation import build_fig15_scan_data, evaluate_conclusion_table, load_published_conclusion_table


def test_published_conclusion_table_shape():
    table_df = load_published_conclusion_table(6)
    assert table_df.shape == (5, 17)
    assert table_df.loc[0, "w=0_b=0"] == 4.61


def test_evaluate_conclusion_table_summary_has_expected_counts():
    summary_df, diff_df = evaluate_conclusion_table(6)
    assert diff_df.shape == (5, 17)
    total_cells = summary_df.loc[summary_df["metric"] == "total_cells", "value"].iloc[0]
    assert total_cells == 80


def test_build_fig15_scan_data_returns_all_requested_ratios():
    scan_df, summary_df = build_fig15_scan_data(n_xi=120)
    assert summary_df["delta_over_phi"].tolist() == ["0", "0.5", "0.75", "1", "1.25", "1.5", "2"]
    assert scan_df["delta_over_phi"].nunique() == 7
    assert {"critical_xi", "minimum_pp", "kp"}.issubset(summary_df.columns)
