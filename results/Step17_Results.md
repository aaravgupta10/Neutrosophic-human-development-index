# Step 17: External Validation Results Registry
## Independent Verification of the Φ–F Horse Race and Interaction Reparameterisation

**Status:** Fully Replicated & Verified  
**Execution Runtime:** 0.16 seconds  
**Environment:** Python 3.12.4 | pandas 3.0.5 | statsmodels 0.14.6 | scipy 1.18.0 | numpy 2.5.2

---

### 1. Gate A Verification & Sample Integrity (Task 1)
- **Left-Join Rule:** Merged `Step15_Findex_Raw.csv` onto canonical `HDIN_Canonical_v2.csv` (184 rows).
- **Dropped Non-Frame Codes (22 total):** Excluded 22 aggregate/territory/exclusion codes automatically:
  `EAP, ECA, HIC, HKG, LAC, LIC, LMC, LMY, MNA, PRI, PSE, SAS, SDN, SSA, SSD, SYR, TKM, TWN, UMC, WLD, XKX, YEM`
- **Recomputation Discrepancies:**
  - $\max |\Phi_{EGDI} - (EGDI \times (1 - p))| = 1.4572e-16$ (threshold: $< 1 \times 10^{-10}$) -> **PASS**
  - $\max |\Phi_{OSI} - (OSI \times (1 - p))| = 1.3878e-16$ (threshold: $< 1 \times 10^{-10}$) -> **PASS**
- **Gate A Estimation Sample Sizes:**
  | Outcome Indicator | Observed Non-Missing Rows | Expected Rows | Gate A Status |
  | :--- | :---: | :---: | :---: |
  | `GovPay_Pct` | **145** | 145 | **PASS** |
  | `DigitalPay_Pct` | **150** | 150 | **PASS** |
  | `MobileAccess_Pct` | **88** | 88 | **PASS** |
  *Note: Monaco (MCO) has no UNDP income sub-index (`I_income = NaN`) and leaves every specification through listwise deletion.*

### 2. The Six-Model Ladder Summary (Task 2)
All specifications estimated by OLS with heteroskedasticity-robust HC3 standard errors.

#### Outcome: `GovPay_Pct`
| Model | RHS Regressors | $N$ | $R^2$ | Key Regressor | Coef | HC3 SE | $t$-stat | $p$-value |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| M0 | inc | 145 | 0.5758 | `inc` | **0.7630** | 0.0547 | 13.9454 | 3.3579e-44 |
| M1 | inc, T | 145 | 0.5923 | `T` | **0.2594** | 0.0994 | 2.6108 | 0.0090 |
| M2 | inc, T, Phi | 145 | 0.6238 | `Phi` | **-0.4624** | 0.1092 | -4.2363 | 2.2720e-05 |
| M3 | inc, T, F, Phi | 145 | 0.6462 | `Phi` | **-0.8698** | 0.1776 | -4.8973 | 9.7151e-07 |
| M3b | inc, T, F | 145 | 0.5929 | `F` | **-0.0417** | 0.0732 | -0.5706 | 0.5683 |
| M5 | inc, T_svc, F, Phi_svc | 145 | 0.6195 | `Phi_svc` | **-0.5718** | 0.1594 | -3.5864 | 0.0003 |

#### Outcome: `DigitalPay_Pct`
| Model | RHS Regressors | $N$ | $R^2$ | Key Regressor | Coef | HC3 SE | $t$-stat | $p$-value |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| M0 | inc | 150 | 0.5599 | `inc` | **1.1132** | 0.0707 | 15.7508 | 6.7867e-56 |
| M1 | inc, T | 150 | 0.5983 | `T` | **0.6021** | 0.1640 | 3.6704 | 0.0002 |
| M2 | inc, T, Phi | 150 | 0.5989 | `Phi` | **-0.0917** | 0.2510 | -0.3654 | 0.7148 |
| M3 | inc, T, F, Phi | 150 | 0.6470 | `Phi` | **-0.9533** | 0.3318 | -2.8736 | 0.0041 |
| M3b | inc, T, F | 150 | 0.6170 | `F` | **0.3472** | 0.1663 | 2.0878 | 0.0368 |
| M5 | inc, T_svc, F, Phi_svc | 150 | 0.6274 | `Phi_svc` | **-0.5839** | 0.3183 | -1.8342 | 0.0666 |

#### Outcome: `MobileAccess_Pct`
| Model | RHS Regressors | $N$ | $R^2$ | Key Regressor | Coef | HC3 SE | $t$-stat | $p$-value |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| M0 | inc | 88 | 0.4924 | `inc` | **0.9592** | 0.0823 | 11.6614 | 2.0064e-31 |
| M1 | inc, T | 88 | 0.5471 | `T` | **0.5018** | 0.1659 | 3.0251 | 0.0025 |
| M2 | inc, T, Phi | 88 | 0.5783 | `Phi` | **-0.4427** | 0.1601 | -2.7656 | 0.0057 |
| M3 | inc, T, F, Phi | 88 | 0.6046 | `Phi` | **-1.1157** | 0.2849 | -3.9162 | 8.9966e-05 |
| M3b | inc, T, F | 88 | 0.5517 | `F` | **-0.1082** | 0.1175 | -0.9208 | 0.3572 |
| M5 | inc, T_svc, F, Phi_svc | 88 | 0.5720 | `Phi_svc` | **-0.8037** | 0.2850 | -2.8195 | 0.0048 |

**Verification Confirmation:** M2 reproduces the published $\Phi$ coefficient on government payments exactly: **-0.4624** (published benchmark: **-0.4624**).

### 3. Centring-Invariance Demonstration for M3 (Task 3)
Demonstration of invariance of the interaction coefficient $\beta_\Phi$ to mean-centring of constituent regressors ($T_c = T - \bar{T}$, $F_c = F - \bar{F}$, $\Phi_c = T_c \times F_c$):

- **Uncentred M3:** $\beta_\Phi = -0.8698$ (HC3 SE = 0.1776, $p = 9.7151e-07$)
- **Centred M3:** $\beta_{\Phi_c} = -0.8698$ (HC3 SE = 0.1776, $p = 9.7151e-07$)
- **Four-Decimal Agreement:** Both coefficients agree to four decimal places: **YES** (exact discrepancy: $8.8818e-16$).

#### M3 Variance Inflation Factors (VIF)
| Regressor | Uncentred VIF | Mean-Centred VIF | Structural Note |
| :--- | :---: | :---: | :--- |
| `inc` | 8.8889 | 8.8889 | Control variable, invariant |
| `T` | 10.0517 | 7.1652 | Inflation absorbed by level origin |
| `F` | 12.6448 | 7.4264 | Inflation absorbed by level origin |
| `Phi` | 4.2702 | 1.8211 | Interaction collinearity reduced |

### 4. Marginal Effects of Non-Reach ($F$) Across Capacity Grid ($T$) (Task 4)
Partial derivative: $\partial y / \partial F = \beta_F + \beta_\Phi \cdot T$. Delta-method SEs from HC3 covariance matrix.

**Outcome: `GovPay_Pct`** (Sample Mean $T = 0.6848$, Share $T < 0.40 = 0.1310$ [$N = 145$])
| State Capacity Grid ($T$) | Marginal Effect $\partial y / \partial F$ | HC3 SE | $z$-statistic | $p$-value |
| :---: | :---: | :---: | :---: | :---: |
| 0.20 | **0.1931** | 0.0896 | 2.1561 | 0.0311 |
| 0.40 | **0.0191** | 0.0709 | 0.2699 | 0.7872 |
| 0.60 | **-0.1548** | 0.0675 | -2.2932 | 0.0218 |
| 0.80 | **-0.3288** | 0.0813 | -4.0433 | 5.2700e-05 |
| 0.95 | **-0.4592** | 0.0990 | -4.6371 | 3.5334e-06 |

**Outcome: `DigitalPay_Pct`** (Sample Mean $T = 0.6774$, Share $T < 0.40 = 0.1400$ [$N = 150$])
| State Capacity Grid ($T$) | Marginal Effect $\partial y / \partial F$ | HC3 SE | $z$-statistic | $p$-value |
| :---: | :---: | :---: | :---: | :---: |
| 0.20 | **0.6044** | 0.1839 | 3.2860 | 0.0010 |
| 0.40 | **0.4137** | 0.1651 | 2.5059 | 0.0122 |
| 0.60 | **0.2231** | 0.1717 | 1.2990 | 0.1940 |
| 0.80 | **0.0324** | 0.2013 | 0.1610 | 0.8721 |
| 0.95 | **-0.1106** | 0.2336 | -0.4734 | 0.6360 |

### 5. Functional Form: Fractional Logit Model (Task 5)
Generalised Linear Model (GLM) with Binomial family, logit link, and HC3 standard errors (Quasi-Maximum Likelihood Estimation):

- **Linear Index Coefficient on $\Phi$:** $\beta_\Phi^{GLM} = -2.1544$ (HC3 SE = 1.2960, $z = -1.6624$, $p = 0.0964$)
- **Average Marginal Effects (AME) of $F$ on Fitted-Probability Scale:**
  - At $T = 0.60$: $AME = -0.2052$
  - At $T = 0.80$: $AME = -0.3271$
  - At $T = 0.95$: $AME = -0.4262$
  *(Note: The index coefficient and probability-scale AMEs are distinct econometric objects and are reported separately without reconciliation, per protocol).*

### 6. Robustness Re-estimations and Influence Diagnostics (Task 6)
- **Influence (Cook's Distance):** Conventional threshold $4/n = 4/145 = 0.0276$. Six highest Cook's distance economies:
  - `ARE` (United Arab Emirates): Cook's $D = 0.1327$ (exceeds 4/n)
  - `KOR` (Republic of Korea): Cook's $D = 0.0415$ (exceeds 4/n)
  - `SAU` (Saudi Arabia): Cook's $D = 0.0347$ (exceeds 4/n)
  - `SGP` (Singapore): Cook's $D = 0.0345$ (exceeds 4/n)
  - `VEN` (Venezuela): Cook's $D = 0.0335$ (exceeds 4/n)
  - `CHE` (Switzerland): Cook's $D = 0.0332$ (exceeds 4/n)
- **Extreme $\Phi$ (Drop Top Decile):** $N = 130$, $\beta_\Phi = -0.9530$ (HC3 SE = 0.2299, $p = 3.3831e-05).
- **Regional Confounding (World Bank Region Fixed Effects):** $N = 145$, $\beta_\Phi = -0.6870$ (HC3 SE = 0.1948, $p = 0.0004).
- **Survey Vintage (Restricted to Survey_Year = 2024):** $N = 136$, $\beta_\Phi = -0.9235$ (HC3 SE = 0.2028, $p = 5.2726e-06).
- **Pakistan Vintage (Nowcast $p = 0.5725$ for PAK):** $N = 145$, $\beta_\Phi = -0.8719$ (HC3 SE = 0.1781, $p = 9.8006e-07).

### 7. Findex Coverage Comparison: Selection Diagnostics (Task 7)
Full Tier I population partition on `GovPay_Pct` availability ($N = 184$ total):

- **Covered Group:** $n = 145$ economies
- **Uncovered Group:** $n = 39$ economies
| Variable | Covered Mean ($n$) | Uncovered Mean ($n$) | Two-Sided Mann–Whitney $U$ | $p$-value | Population Sum Check |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `Phi` | 0.1487 ($n=145$) | 0.1298 ($n=39$) | 3041.0000 | 0.4707 | 184 / 184 |
| `EGDI` | 0.6848 ($n=145$) | 0.5312 ($n=39$) | 4041.0000 | 3.9878e-05 | 184 / 184 |
| `inc` | 0.7287 ($n=145$) | 0.6983 ($n=38$) | 3030.5000 | 0.3441 | 183 / 184 |

**Uncovered ISO3 List (39 economies):**
`AGO, AND, ATG, BDI, BHS, BRB, BRN, BTN, CPV, CUB, DJI, DMA, ERI, FJI, FSM, GNB, GNQ, GRD, GUY, KIR, KNA, LCA, LIE, MCO, MHL, NRU, OMN, PLW, PNG, QAT, SLB, SMR, SOM, STP, SUR, SYC, TLS, TON, VCT`

*(Note: Per Section 8 instructions, no substantive conclusion is drawn; the tests and complete ISO3 list are reported as observed).*

### 8. Deliverable Registry (Task 8)
| Deliverable | Path | Description | Verification Status |
| :--- | :--- | :--- | :---: |
| **Analysis Frame** | `step17/Step17_Frame.csv` | Merged Tier I panel ($N=184$) with constructed variables | **VERIFIED** |
| **Model Ladder** | `step17/Step17_Ladder.csv` | Full six-model OLS HC3 ladder across 3 outcomes | **VERIFIED** |
| **Marginal Effects** | `step17/Step17_MarginalEffects.csv` | Delta-method marginal effects across $T$ grid | **VERIFIED** |
| **Results Registry** | `step17/Step17_Results.md` | Complete formatted tables and diagnostics | **VERIFIED** |
| **Estimation Pipeline** | `step17/Step17_Estimation.py` | Clean, reproducible pipeline | **VERIFIED** |
