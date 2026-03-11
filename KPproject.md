“A Spreadsheet-Based Technique to Calculate the Passive Soil Pressure Based on the Log-Spiral Method”


Title: A Spreadsheet-Based Technique to Calculate the Passive Soil Pressure Based on the Log-Spiral Method

Field: Geotechnical Engineering / Earth Pressure Theory

Topic: Passive Earth Pressure using Log-Spiral Failure Surface

Method: Spreadsheet-based computational procedure for solving 

A spreadsheet-based technique to calculate the passive soil pressure
based on the log-spiral method.


The log-spiral method is widely used to evaluate passive earth pressure
in geotechnical engineering. In the paper titled
"A Spreadsheet-Based Technique to Calculate the Passive Soil Pressure
Based on the Log-Spiral Method", a computational procedure was proposed
to facilitate the evaluation of passive resistance using spreadsheet tools.

# AI Development Role Definition
## Log-Spiral Passive Earth Pressure Verification System

---

# 1. Assigned AI Role

The AI agent responsible for implementing this system shall assume the role of:

**Senior Geotechnical Engineering Computational Developer and Academic Verification Analyst**

The agent must operate with the mindset of:

• Geotechnical Engineer  
• Numerical Methods Specialist  
• Engineering Software Developer  
• Academic Paper Reviewer  

The objective is **not only to implement code**, but also to **audit the mathematical correctness of the published equations**.



# Streamlit Engineering Verification App
## Requirements & Development Specification
### Log-Spiral Passive Earth Pressure Paper Review System

---

# 1. Purpose

This document defines the **system requirements, architecture, and development workflow**
for building a **Streamlit-based engineering verification application** that reproduces
and validates the equations presented in the academic paper:

"A spreadsheet-based technique to calculate the passive soil pressure based on the log-spiral method."

The purpose of this system is to create a **transparent computational framework**
capable of verifying the mathematical formulation and numerical results presented
in the paper.

The application will allow engineers, researchers, and reviewers to:

- Reproduce the analytical derivations
- Verify the equation consistency
- Validate numerical results against experimental data
- Visualize failure mechanisms
- Audit the derivation process step-by-step

This document is written to a **professional engineering and academic review standard**.

---

# 2. System Objectives

The system shall provide the following capabilities:

1. Implement the **log-spiral passive earth pressure calculation method**
2. Support both geometric configurations defined in the paper

   • Case A – Pole located outside soil mass  
   • Case B – Pole located inside soil mass

3. Compute passive earth pressure force **Pp**
4. Perform **parameter scanning over ξ (xi)**
5. Identify **minimum passive resistance**
6. Provide **equation traceability**
7. Verify closed-form equations numerically
8. Replicate validation datasets
9. Generate engineering calculation reports

---

# 3. Software Platform

Programming Language:

Python 3.11+

Application Framework:

Streamlit

Scientific Libraries:

- NumPy
- Pandas
- SciPy
- Matplotlib

Optional:

- Plotly (interactive plotting)

---

# 4. Project Architecture

```
logspiral_review_app/
│
├─ app.py
├─ solver.py
├─ geometry.py
├─ validation.py
├─ plots.py
├─ numerical_checks.py
│
├─ data/
│   ├─ table2_validation.csv
│   └─ table4_validation.csv
│
├─ tests/
│   └─ test_solver.py
│
├─ requirements.txt
└─ README.md
```

---

# 5. Functional Requirements

## 5.1 Input Parameters

The application shall allow users to input the following engineering parameters.

| Parameter | Description |
|-----------|-------------|
| H | Retained soil height |
| γ | Soil unit weight |
| φ | Soil friction angle |
| δ | Wall friction angle |
| β | Backfill slope |
| ω | Wall inclination |
| q | Uniform surcharge |
| ξ_min | Minimum xi search bound |
| ξ_max | Maximum xi search bound |
| n_ξ | Number of xi search points |

All angle inputs shall be provided in **degrees** but internally converted to **radians**.

---

# 6. Mathematical Implementation

## 6.1 Log-Spiral Geometry

The failure surface consists of:

- A logarithmic spiral
- A tangent line segment

General log-spiral equation:

```
r = r₀ * exp(θ * tan φ)
```

Where:

r = radial distance  
θ = angular coordinate  
φ = soil friction angle  

The solver must compute:

- spiral origin radius
- spiral endpoint radius
- spiral angle limits

---

## 6.2 Case A – Pole Outside Soil Mass

Case A corresponds to the condition where the pole of the log spiral
is located outside the soil mass.

The solver must compute:

- geometric parameters
- coordinates of points along the spiral
- area moments
- resultant forces
- lever arms
- passive force equilibrium

The final passive force **Pp** is obtained through moment equilibrium.

---

## 6.3 Case B – Pole Inside Soil Mass

Case B corresponds to the condition where the pole of the log spiral
is located within the soil mass.

The calculation follows a similar structure to Case A but with
modified geometric relationships.

The solver must compute:

- adjusted spiral geometry
- additional area components
- modified moment arms
- final passive force equilibrium

---

# 7. ξ Parameter Search

The passive force **Pp** is a function of the parameter **ξ**.

The solver must perform the following algorithm:

1. Define ξ search range
2. Discretize the range into n points
3. Compute passive force for each ξ
4. Identify minimum passive force
5. Record critical ξ value

Optional refinement:

Perform secondary search near the minimum.

---

# 8. Equation Trace Module

The application must display intermediate variables including:

- input parameters
- derived angles
- spiral parameters
- coordinate locations
- area components
- force components
- moment arms
- passive force

Each output must reference the equation used.

---

# 9. Numerical Verification Module

Closed-form equations must be verified using numerical integration.

Example verification:

Area moment calculated using:

• analytical formula  
• numerical integration  

The difference shall be reported as percentage error.

---

# 10. Visualization Requirements

## 10.1 Passive Force vs ξ Plot

The application must generate a plot showing:

- passive force vs ξ
- identified minimum force
- critical ξ value

---

## 10.2 Failure Mechanism Visualization

The geometry plot must display:

- retaining wall
- soil surface
- spiral curve
- tangent line
- pole location
- failure region

---

# 11. Experimental Validation

The application must replicate validation results using experimental data.

Datasets must be stored as CSV files.

Validation output must include:

| Measured Force | Calculated Force | Difference (%) |

---

# 12. User Interface Design

The Streamlit interface shall include the following tabs.

1. Input Summary
2. Equation Trace
3. Passive Force vs ξ Plot
4. Geometry Visualization
5. Validation Results
6. Parametric Study

---

# 13. Export Features

Users must be able to export:

- CSV calculation tables
- engineering report
- figures

Reports should contain:

- input parameters
- calculation procedure
- critical ξ
- minimum passive force
- validation comparison

---

# 14. Testing Requirements

Unit tests must verify:

- equation implementation
- geometry calculations
- stability of ξ search algorithm

---

# 15. Acceptance Criteria

The system shall be considered complete when:

• all equations implemented  
• validation data reproduced  
• equation trace available  
• numerical verification operational  
• application runs successfully in Streamlit  

---

# 16. Intended Users

Primary users:

- Geotechnical engineers
- Engineering researchers
- Graduate students
- Academic reviewers

---

# 17. Deliverables

The project deliverables shall include:

1. Streamlit application
2. Python source code
3. documentation
4. validation datasets
5. unit tests
6. calculation report templates

---

# End of Document