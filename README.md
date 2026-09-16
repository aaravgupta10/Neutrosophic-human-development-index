# Stranded Capacity: Measuring and Validating the Gap Between State Digital Provision and Citizen Reach

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.placeholder.svg)](https://zenodo.org/)
[![Replication Status](https://img.shields.io/badge/Replication-Passing%20(100%25)-brightgreen.svg)](tests/test_replication.py)

Official research code, canonical datasets, and replication pipeline for the paper:
> **"Stranded capacity: measuring and validating the gap between state digital provision and citizen reach"**  
> *Neutrosophic Human Development Index (HDI-N / NHDI) Framework*

---

## 📖 Overview & Conceptual Framework

The United Nations Human Development Index (HDI) remains the benchmark metric for national capability, yet its health–education–income structure predates modern digital infrastructure. Existing composite digital metrics (e.g., DESI, IDI) treat state supply and citizen adoption as compensatory and substitutable—arithmetically averaging away the chasm between them.

This research formulates a **neutrosophic decomposition** $(T, I, F)$ holding state capability and citizen reach strictly distinct:
1. **Truth ($T$):** Measured nominal state digital capacity (UN E-Government Development Index, $EGDI$).
2. **Falsity ($F$):** Citizen digital exclusion or non-penetration ($F = 1 - p$, where $p$ is the ITU digital penetration rate).
3. **Stranded Capacity ($\Phi$):** The conjunctive product of state provision and citizen exclusion:
   $$\Phi = T \times F = EGDI \times (1 - p)$$
   $\Phi$ quantifies nominal state administrative capability lying stranded beyond the reach of the population.
4. **Indeterminacy ($I$):** Bipolar structural divergence between public service interfaces ($OSI$) and physical connectivity ($TII$):
   $$I = OSI - TII$$

The framework is evaluated across **184 global economies**, establishing canonical panels (`HDIN_Canonical_v1.csv` and `HDIN_Canonical_v2.csv`) and verified against microdata from the **World Bank Global Findex Database**.

---

## 🎯 Key Empirical Findings

### 1. The Incremental Validation Criterion ($\Phi$-vs-$F$ Horse Race)
Using OLS with heteroskedasticity-robust **HC3 standard errors** across the 145-economy Findex validation sample, digital facade $\Phi$ is pitted directly against raw exclusion $F$:

$$\text{GovPay} = \beta_0 + \beta_1 \text{inc} + \beta_2 T + \beta_3 F + \beta_4 \Phi + \varepsilon$$

| Model | Specification | $N$ | $R^2$ | Key Regressor | Coef | HC3 SE | $t$-stat | $p$-value |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M0** | Baseline Income | 145 | 0.5758 | `inc` | 0.7630 | 0.0547 | 13.95 | $< 10^{-40}$ |
| **M1** | Supply Side | 145 | 0.5923 | `T` | 0.2594 | 0.0994 | 2.61 | 0.0090 |
| **M2** | Facade Model | 145 | 0.6238 | `Phi` | **-0.4624** | 0.1092 | -4.24 | $2.27 \times 10^{-5}$ |
| **M3** | **Full Horse Race** | 145 | **0.6462** | `Phi` | **-0.8698** | 0.1776 | -4.90 | **$9.72 \times 10^{-7}$** |
| **M3b** | Non-Penetration Alone | 145 | 0.5929 | `F` | -0.0417 | 0.0732 | -0.57 | 0.5683 *(n.s.)* |
| **M5** | Service-Level Robustness | 145 | 0.6195 | `Phi_svc` | -0.5718 | 0.1594 | -3.59 | 0.0003 |

**Result:** In Model M3, $\Phi$ remains deeply negative and significant ($p < 10^{-6}$), while raw non-penetration $F$ is statistically indistinguishable from zero ($p = 0.57$). Stranded capacity uniquely captures the institutional bottleneck where nominal digitization yields zero welfare return.

---

## 📁 Repository Structure & Data Catalog

```text
├── README.md                      # Academic documentation & replication guide
├── LICENSE                        # MIT Open Source License
├── requirements.txt               # Python package dependencies
├── run_replication.py             # Single-command end-to-end master replication runner
│
├── data/
│   ├── canonical/                 # Frozen published research datasets
│   │   ├── HDIN_Canonical_v1.csv  # 184-economy canonical panel v1
│   │   ├── HDIN_Canonical_v2.csv  # 184-economy canonical panel v2 (complete variables)
│   │   └── Step14_North_South_Country_List.md
│   ├── inputs/                    # Primary raw and harmonized inputs
│   │   ├── Step12_EGDI_2024_Full.csv
│   │   ├── Step12_Facade_Full_Population.csv
│   │   ├── Step12_ITU_Penetration_Full.csv
│   │   ├── Step13_Master_Inputs.csv
│   │   ├── Step13_HDIN_Operators.csv
│   │   ├── EGOV_DATA_2024.csv
│   │   ├── fixed-broadband-subscriptions_.csv
│   │   ├── high-technology-exports-1.csv
│   │   ├── individuals-using-the-internet_.csv
│   │   ├── gini_clean_2023_updated.csv
│   │   ├── shadow_economy.csv
│   │   └── swiid9_92_summary.csv
│   └── validation/                # External validation datasets
│       ├── Step15_Findex_Raw.csv  # Clean 174-economy extract from WB Global Findex
│       ├── Step15_Validation_Set.csv
│       ├── Step16_Disparity_Comparison.csv
│       └── Step16_Elgin_Extract.csv
│
├── scripts/                       # Modular replication scripts
│   ├── step13_compute.py          # Master inputs and operator sensitivity computations
│   ├── step14_build.py            # Builds canonical panels from inputs
│   ├── step14_statistics.py       # 161 summary statistics, North-South tests
│   ├── step15_validation.py       # Global Findex validation merge and regressions
│   ├── step17_estimation.py       # Six-Model Ladder OLS regressions (HC3 SEs)
│   ├── full_triple_aggregation.py # Full (T, I, F) triple aggregation
│   └── conversion_channel_robustness.py
│
├── results/                       # Empirical outputs, tables, and registries
│   ├── Step14_Statistics_Output.md# Complete numerical statistics audit log
│   ├── Step15_Validation_Results.md
│   ├── Step17_Results.md          # Step 17 External validation registry
│   ├── Step17_Ladder.csv          # Regression ladder parameter estimates
│   ├── Step17_MarginalEffects.csv # Marginal effects across digital penetration grid
│   ├── Step17_Frame.csv           # Merged estimation frame
│   ├── plots/                     # Diagnostic residual plots
│   └── tables/                    # Published paper tables 1-5 and robustness grids
│
├── HDI_FN/                        # Modular self-contained pipeline for earlier stages
└── tests/
    └── test_replication.py        # Automated unit and econometric validation tests
```

---

## ⚡ Quickstart: Replicating All Results

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

```bash
# Clone the repository
git clone https://github.com/aaravgupta10/Neutrosophic-human-development-index.git
cd Neutrosophic-human-development-index

# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Execute End-to-End Replication
Run the master runner to execute all scripts in sequence and verify all econometric results:

```bash
python run_replication.py
```

### 3. Run Automated Validation Tests
Verify the numerical identities, Gate A sample sizes ($N=145, 150, 88$), and HC3 standard error reproductions:

```bash
python -m unittest tests/test_replication.py
```

---

## 🌐 Minting a Permanent DOI via Zenodo

This repository is formatted and structured for direct archival deposition with **Zenodo**:

1. Log into [Zenodo](https://zenodo.org/) using your GitHub credentials.
2. Navigate to [Zenodo GitHub Settings](https://zenodo.org/account/settings/github/).
3. Find `aaravgupta10/Neutrosophic-human-development-index` and switch the toggle to **ON**.
4. In GitHub, create a new Release:
   - Tag: `v1.0.0`
   - Title: `Neutrosophic Human Development Index: Replication Archive`
   - Click **Publish release**.
5. Zenodo will automatically archive the snapshot, mint a permanent citable **DOI**, and provide a badge to insert above.

---

## 📜 Citation

If using this codebase or data in academic work, please cite:

```bibtex
@article{nhdi2026stranded,
  title={Stranded capacity: measuring and validating the gap between state digital provision and citizen reach},
  author={Gupta, Aarav and Research Contributors},
  journal={Working Paper / Manuscript Submission},
  year={2026},
  publisher={GitHub / Zenodo},
  doi={10.5281/zenodo.[PENDING]}
}
```

---

## 📄 License
This repository is licensed under the [MIT License](LICENSE). Datasets are sourced from public reporting by the United Nations Department of Economic and Social Affairs (UN DESA), International Telecommunication Union (ITU), and World Bank Open Data.
