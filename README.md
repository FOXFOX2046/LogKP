# Log-Spiral Passive Pressure Review App

This workspace implements a Streamlit-based verification app for the paper:

`A Spreadsheet-Based Technique to Calculate the Passive Soil Pressure Based on the Log-Spiral Method`

## What is included

- `app.py`: Streamlit interface with six review tabs
- `solver.py`: passive force evaluation and xi scanning
- `geometry.py`: case geometry, Rankine terms, and polygon helpers
- `numerical_checks.py`: analytical versus numerical sector-moment check
- `validation.py`: CSV-backed validation helpers
- `plots.py`: Matplotlib figures for xi scans and mechanism geometry
- `data/`: validation tables transcribed from the paper
- `tests/`: smoke tests for solver behavior

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The solver follows the paper's case split for the spiral pole being outside or inside the soil mass.
- The wedge self-weight moment is evaluated numerically from the reconstructed slip-mass polygon to keep the implementation transparent and auditable.
- Validation data is seeded from the paper's published tables so the app can compare current calculations with reported values.
