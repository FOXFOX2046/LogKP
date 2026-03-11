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

## Python File Guide

### Main calculation files

- [`C:/Users/dev/Documents/Playground/KP EQU/solver.py`](/Users/dev/Documents/Playground/KP%20EQU/solver.py)
  Main calculation logic. This file contains the core passive pressure solver, including `evaluate_xi()` for a single trial xi value and `scan_xi()` for the full xi search.

- [`C:/Users/dev/Documents/Playground/KP EQU/geometry.py`](/Users/dev/Documents/Playground/KP%20EQU/geometry.py)
  Geometry construction for the log-spiral failure mechanism. This file builds the key points, spiral curve, wall geometry, lever arms, and wedge polygon used by the solver.

- [`C:/Users/dev/Documents/Playground/KP EQU/validation.py`](/Users/dev/Documents/Playground/KP%20EQU/validation.py)
  Validation and reference-table utilities. This file generates rebuilt Table 6-9 values, validation comparisons, and the DM7 approximation tables used in the Verification tab.

- [`C:/Users/dev/Documents/Playground/KP EQU/app.py`](/Users/dev/Documents/Playground/KP%20EQU/app.py)
  Streamlit user interface. This file collects input values, calls the calculation functions, and displays figures, tables, verification outputs, and calculators.

### Supporting calculation files

- [`C:/Users/dev/Documents/Playground/KP EQU/plots.py`](/Users/dev/Documents/Playground/KP%20EQU/plots.py)
  Plotting helpers for the passive force scan chart and geometry visualization.

- [`C:/Users/dev/Documents/Playground/KP EQU/numerical_checks.py`](/Users/dev/Documents/Playground/KP%20EQU/numerical_checks.py)
  Numerical verification helpers, including the spiral sector moment check against the analytical expression.

## Data Structure

### Core input model

The main calculation input is the `PassivePressureInput` dataclass in [`solver.py`](/Users/dev/Documents/Playground/KP%20EQU/solver.py).

| Field | Type | Meaning |
|---|---|---|
| `H` | `float` | Wall height |
| `gamma` | `float` | Soil unit weight |
| `phi_deg` | `float` | Soil friction angle in degrees |
| `delta_deg` | `float` | Wall friction angle in degrees |
| `beta_deg` | `float` | Backfill slope angle in degrees |
| `omega_deg` | `float` | Wall inclination angle in degrees |
| `q` | `float` | Uniform surcharge |

### Geometry model

The geometric reconstruction is stored in the `GeometryState` dataclass in [`geometry.py`](/Users/dev/Documents/Playground/KP%20EQU/geometry.py).

Important fields:

- `case`: failure mechanism case (`A` or `B`)
- `xi`: current trial pole parameter
- `a`, `b`, `g`, `f`, `f_prime`: key geometry points
- `r0`, `rg`, `theta_g`, `lambda_angle`: log-spiral parameters
- `ag`, `fg`, `hrw`: derived geometric lengths
- `spiral_points`: sampled spiral curve coordinates as `np.ndarray`
- `wedge_polygon`: slip-mass polygon coordinates as `np.ndarray`

### Solver result model

The main calculation output is the `PassivePressureResult` dataclass in [`solver.py`](/Users/dev/Documents/Playground/KP%20EQU/solver.py).

Important fields:

- `case`: chosen case for the current solution
- `xi`: current or critical xi value
- `passive_force`: resolved passive force `Pp`
- `lever_arm`: moment arm for the passive force
- `weight_moment`, `rankine_moment`, `surcharge_moment`, `rankine_surcharge_moment`: moment components
- `wedge_area`, `wedge_centroid_x`: geometric mass properties
- `geometry`: embedded `GeometryState`
- `trace`: dictionary of intermediate calculation values for verification display

### Tabular data

The app uses `pandas.DataFrame` objects for reporting and verification.

- `scan_df`: xi scan table returned by `scan_xi()`
- `table2_validation.csv`: measured-versus-calculated validation data
- `table4_validation.csv`: published comparison data
- Table 6-9 rebuilt tables: generated in [`validation.py`](/Users/dev/Documents/Playground/KP%20EQU/validation.py)
- DM7 formula tables: generated in [`validation.py`](/Users/dev/Documents/Playground/KP%20EQU/validation.py)

### UI state

The Streamlit app stores interactive geometry controls in `st.session_state`.

- `picture_xi`: current xi used in the geometry display
- `picture_xi_text`: text-box value paired with the manual xi input

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The solver follows the paper's case split for the spiral pole being outside or inside the soil mass.
- The wedge self-weight moment is evaluated numerically from the reconstructed slip-mass polygon to keep the implementation transparent and auditable.
- Validation data is seeded from the paper's published tables so the app can compare current calculations with reported values.
