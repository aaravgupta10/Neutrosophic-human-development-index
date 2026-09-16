# Step 13 Operator Reconciliation and Comparison Report

## Computable Set & Normalisation Base

- **Total Baseline Economies (Step 12 Facade)**: 193
- **Computable Set Size**: **158 economies**
- **Normalisation Maxima (taken strictly over the computable set)**:
  - $\max(B) = 51.7401$ set by **AND (Andorra)**
  - $\max(H) = 63.9779\%$ set by **PHL (Philippines)**

### Excluded Economies Breakdown

#### (a) Excluded due to Missing Inputs (33 economies)
- **AFG** (Afghanistan): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **BGD** (Bangladesh): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **DZA** (Algeria): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **ERI** (Eritrea): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **FSM** (Micronesia (Federated States of)): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **GIN** (Guinea): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **GNB** (Guinea-Bissau): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **GNQ** (Equatorial Guinea): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **HTI** (Haiti): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **IRQ** (Iraq): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **KNA** (Saint Kitts and Nevis): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **LBY** (Libya): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **LIE** (Liechtenstein): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **MCO** (Monaco): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **MHL** (Marshall Islands): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **NRU** (Nauru): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **PLW** (Palau): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **PRK** (Democratic People's Republic of Korea): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **SDN** (Sudan): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **SLB** (Solomon Islands): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **SLE** (Sierra Leone): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **SMR** (San Marino): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **SOM** (Somalia): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **SRB** (Serbia): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **SSD** (South Sudan): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **SYR** (Syrian Arab Republic): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **TCD** (Chad): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **TKM** (Turkmenistan): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **TUV** (Tuvalu): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **VEN** (Venezuela): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **VUT** (Vanuatu): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)
- **WSM** (Samoa): Missing Internet penetration (ITU)
- **YEM** (Yemen): Missing High-technology exports (WDI series TX.VAL.TECH.MF.ZS)

#### (b) Excluded due to Exactly Zero Values (2 economies)
- **ATG** (Antigua and Barbuda): High-technology exports == 0
- **BLZ** (Belize): High-technology exports == 0

---

## 1. Spearman Rank Correlations

| Operator Pair / Comparison | Spearman $\rho$ |
| :--- | :--- |
| Operator A vs. Operator B | 0.9994 |
| Operator A vs. Operator C | 0.9993 |
| Operator B vs. Operator C | 0.9990 |
| Operator A vs. Standard HDI | 0.8854 |
| Operator B vs. Standard HDI | 0.8854 |
| Operator C vs. Standard HDI | 0.8812 |

## 2. Rank Movement Analysis

### (a) Between Operator A and Operator B
- Economies moving $\ge 3$ ranks: **16**
  - South Africa (ZAF: $\Delta=3$), Gabon (GAB: $\Delta=3$), Egypt (EGY: $\Delta=3$), Saint Lucia (LCA: $\Delta=3$), Albania (ALB: $\Delta=3$), Guyana (GUY: $\Delta=3$), Iran (Islamic Republic of) (IRN: $\Delta=5$), Dominica (DMA: $\Delta=3$), Montenegro (MNE: $\Delta=5$), Suriname (SUR: $\Delta=4$), Estonia (EST: $\Delta=4$), Kazakhstan (KAZ: $\Delta=3$), Jordan (JOR: $\Delta=3$), Andorra (AND: $\Delta=7$), Brunei Darussalam (BRN: $\Delta=7$), Luxembourg (LUX: $\Delta=3$)
- Economies moving $\ge 5$ ranks: **4**
  - Iran (Islamic Republic of) (IRN: $\Delta=5$), Montenegro (MNE: $\Delta=5$), Andorra (AND: $\Delta=7$), Brunei Darussalam (BRN: $\Delta=7$)

### (b) Between Operator A and Operator C
- Economies moving $\ge 3$ ranks: **19**
  - Uganda (UGA: $\Delta=3$), Nigeria (NGA: $\Delta=3$), Tajikistan (TJK: $\Delta=3$), Papua New Guinea (PNG: $\Delta=5$), Grenada (GRD: $\Delta=3$), Tonga (TON: $\Delta=7$), Comoros (COM: $\Delta=4$), Egypt (EGY: $\Delta=3$), Ukraine (UKR: $\Delta=5$), Cuba (CUB: $\Delta=4$), Guyana (GUY: $\Delta=3$), Azerbaijan (AZE: $\Delta=3$), Bhutan (BTN: $\Delta=5$), Morocco (MAR: $\Delta=3$), Oman (OMN: $\Delta=3$), Brunei Darussalam (BRN: $\Delta=4$), Luxembourg (LUX: $\Delta=3$), Kuwait (KWT: $\Delta=3$), Bahrain (BHR: $\Delta=4$)
- Economies moving $\ge 5$ ranks: **4**
  - Papua New Guinea (PNG: $\Delta=5$), Tonga (TON: $\Delta=7$), Ukraine (UKR: $\Delta=5$), Bhutan (BTN: $\Delta=5$)

## 3. Original 20 Panel Economies

| ISO3 | Country | Rank A | Rank B | Rank C | HDI-N (A) | HDI-N (B) | HDI-N (C) | Standard HDI Rank |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ISL | Iceland | 1 | 1 | 1 | 0.9227 | 0.9173 | 0.9230 | 3 |
| CHE | Switzerland | 2 | 3 | 2 | 0.9135 | 0.9065 | 0.9162 | 1 |
| NOR | Norway | 5 | 4 | 5 | 0.9077 | 0.9045 | 0.9097 | 2 |
| KOR | Republic of Korea | 6 | 6 | 6 | 0.8924 | 0.8920 | 0.8945 | 19 |
| NLD | Netherlands | 9 | 8 | 9 | 0.8875 | 0.8847 | 0.8895 | 10 |
| FRA | France | 18 | 17 | 16 | 0.8472 | 0.8428 | 0.8555 | 28 |
| FIN | Finland | 25 | 25 | 24 | 0.8210 | 0.8173 | 0.8236 | 12 |
| DNK | Denmark | 11 | 11 | 11 | 0.8762 | 0.8761 | 0.8772 | 5 |
| DEU | Germany | 12 | 12 | 12 | 0.8688 | 0.8688 | 0.8740 | 7 |
| AUS | Australia | 10 | 10 | 10 | 0.8790 | 0.8774 | 0.8815 | 10 |
| JPN | Japan | 20 | 20 | 20 | 0.8291 | 0.8287 | 0.8370 | 24 |
| CAN | Canada | 17 | 16 | 18 | 0.8472 | 0.8447 | 0.8546 | 18 |
| BGD | Bangladesh | *Excluded* | *Excluded* | *Excluded* | *N/A* | *N/A* | *N/A* | 129 (Missing WDI HiTech) |
| CHN | China | 36 | 36 | 36 | 0.7686 | 0.7673 | 0.7758 | 75 |
| PAK | Pakistan | 137 | 138 | 137 | 0.3137 | 0.3086 | 0.3472 | 164 |
| NPL | Nepal | 120 | 120 | 120 | 0.4056 | 0.3961 | 0.4257 | 146 |
| BFA | Burkina Faso | 147 | 147 | 147 | 0.2620 | 0.2615 | 0.2956 | 185 |
| PHL | Philippines | 64 | 64 | 63 | 0.6475 | 0.6454 | 0.6612 | 113 |
| IDN | Indonesia | 92 | 92 | 92 | 0.5573 | 0.5552 | 0.5708 | 112 |
| MAR | Morocco | 93 | 94 | 96 | 0.5573 | 0.5440 | 0.5642 | 120 |

## 4. Bangladesh EGDI 2024 Re-Retrieval

- **Source**: United Nations Department of Economic and Social Affairs (UN DESA), E-Government Knowledgebase (EGOVKB).
- **URL**: `https://publicadministration.un.org/egovkb/en-us/Data/Country-Information/id/14-Bangladesh`
- **Published EGDI Value (2024)**: `0.6570` (reported to 4 decimal places).
- **Global EGDI Rank**: 100
- **Reconciliation**: The source page publishes Bangladesh's 2024 EGDI to 4 decimal places as `0.6570`. This accounts for the discrepancy with the rounded 3-decimal figure `0.656` in the project panel file without modifying either historical file.
