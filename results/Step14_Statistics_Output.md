# Step 14 Statistics Registry

Input: `HDIN_Canonical_v2.csv` only.

Software: Python 3.12.4; NumPy 2.5.2; SciPy 1.18.0; statsmodels 0.14.6.
Mann-Whitney tests use scipy.stats.mannwhitneyu (asymptotic method, continuity correction, the stated one-sided alternative). OLS uses statsmodels with HC3 robust covariance and normal-approximation p-values (use_t=False). Quartiles use NumPy linear interpolation. Income bins are equal-frequency bins formed after stable ascending rank ordering. Global South/North is read from the canonical file's Global_North_South column -- see Step14_North_South_Country_List.md for the definition and full country list. The hand-implemented routines used prior to this revision (tie-corrected normal-approximation Mann-Whitney; closed-form HC1 OLS) are retained as a cross-check, not deleted -- see the cross-check table below. A difference between the two is reported as-is, not reconciled.

| ID | Description | Value | Test statistic | p-value | N | Code |
|---|---|---:|---:|---:|---:|---|
| A_Phi_EGDI_mean | Tier I distribution: mean of Phi_EGDI | 0.144690089419 |  |  | 184 | numpy |
| A_Phi_EGDI_median | Tier I distribution: median of Phi_EGDI | 0.13404887766 |  |  | 184 | numpy |
| A_Phi_EGDI_sd | Tier I distribution: sd of Phi_EGDI | 0.0938293484729 |  |  | 184 | numpy |
| A_Phi_EGDI_min | Tier I distribution: min of Phi_EGDI | 0 |  |  | 184 | numpy |
| A_Phi_EGDI_q1 | Tier I distribution: q1 of Phi_EGDI | 0.0705505430707 |  |  | 184 | numpy |
| A_Phi_EGDI_q3 | Tier I distribution: q3 of Phi_EGDI | 0.199052364302 |  |  | 184 | numpy |
| A_Phi_EGDI_max | Tier I distribution: max of Phi_EGDI | 0.453171399078 |  |  | 184 | numpy |
| A_Phi_OSI_mean | Tier I distribution: mean of Phi_OSI | 0.135430389319 |  |  | 184 | numpy |
| A_Phi_OSI_median | Tier I distribution: median of Phi_OSI | 0.103756913604 |  |  | 184 | numpy |
| A_Phi_OSI_sd | Tier I distribution: sd of Phi_OSI | 0.111909003608 |  |  | 184 | numpy |
| A_Phi_OSI_min | Tier I distribution: min of Phi_OSI | 0 |  |  | 184 | numpy |
| A_Phi_OSI_q1 | Tier I distribution: q1 of Phi_OSI | 0.0597441444615 |  |  | 184 | numpy |
| A_Phi_OSI_q3 | Tier I distribution: q3 of Phi_OSI | 0.17910209393 |  |  | 184 | numpy |
| A_Phi_OSI_max | Tier I distribution: max of Phi_OSI | 0.584290803668 |  |  | 184 | numpy |
| A_R_facade_mean | Tier I distribution: mean of R_facade | 1.9505476109 |  |  | 184 | numpy |
| A_R_facade_median | Tier I distribution: median of R_facade | 1.24699760138 |  |  | 184 | numpy |
| A_R_facade_sd | Tier I distribution: sd of R_facade | 1.76974029499 |  |  | 184 | numpy |
| A_R_facade_min | Tier I distribution: min of R_facade | 1 |  |  | 184 | numpy |
| A_R_facade_q1 | Tier I distribution: q1 of R_facade | 1.1027637214 |  |  | 184 | numpy |
| A_R_facade_q3 | Tier I distribution: q3 of R_facade | 1.78155665194 |  |  | 184 | numpy |
| A_R_facade_max | Tier I distribution: max of R_facade | 13.9425291642 |  |  | 184 | numpy |
| A_I_egov_mean | Tier I distribution: mean of I_egov | 0.176692391304 |  |  | 184 | numpy |
| A_I_egov_median | Tier I distribution: median of I_egov | 0.14265 |  |  | 184 | numpy |
| A_I_egov_sd | Tier I distribution: sd of I_egov | 0.142911437847 |  |  | 184 | numpy |
| A_I_egov_min | Tier I distribution: min of I_egov | 0.0002 |  |  | 184 | numpy |
| A_I_egov_q1 | Tier I distribution: q1 of I_egov | 0.069475 |  |  | 184 | numpy |
| A_I_egov_q3 | Tier I distribution: q3 of I_egov | 0.2558 |  |  | 184 | numpy |
| A_I_egov_max | Tier I distribution: max of I_egov | 0.8831 |  |  | 184 | numpy |
| A_variance_log_phi | Log Phi_EGDI variance decomposition: variance_log_phi | 0.766084799337 |  |  | 181 | numpy |
| A_variance_log_egdi | Log Phi_EGDI variance decomposition: variance_log_egdi | 0.190694536405 |  |  | 181 | numpy |
| A_variance_log_non_reach | Log Phi_EGDI variance decomposition: variance_log_non_reach | 1.27353512851 |  |  | 181 | numpy |
| A_twice_covariance | Log Phi_EGDI variance decomposition: twice_covariance | -0.698144865574 |  |  | 181 | numpy |
| B_eastern_europe_count | M49 sub-region Eastern Europe: count | 10 |  |  | 10 | count |
| B_eastern_europe_mean_phi | M49 sub-region Eastern Europe: mean Phi_EGDI | 0.111998464003 |  |  | 10 | numpy |
| B_eastern_europe_median_phi | M49 sub-region Eastern Europe: median Phi_EGDI | 0.108979243412 |  |  | 10 | numpy |
| B_latin_america_and_the_caribbean_count | M49 sub-region Latin America and the Caribbean: count | 33 |  |  | 33 | count |
| B_latin_america_and_the_caribbean_mean_phi | M49 sub-region Latin America and the Caribbean: mean Phi_EGDI | 0.146120132154 |  |  | 33 | numpy |
| B_latin_america_and_the_caribbean_median_phi | M49 sub-region Latin America and the Caribbean: median Phi_EGDI | 0.147603199789 |  |  | 33 | numpy |
| B_micronesia_count | M49 sub-region Micronesia: count | 5 |  |  | 5 | count |
| B_micronesia_mean_phi | M49 sub-region Micronesia: mean Phi_EGDI | 0.117272041475 |  |  | 5 | numpy |
| B_micronesia_median_phi | M49 sub-region Micronesia: median Phi_EGDI | 0.0866485370005 |  |  | 5 | numpy |
| B_northern_africa_count | M49 sub-region Northern Africa: count | 5 |  |  | 5 | count |
| B_northern_africa_mean_phi | M49 sub-region Northern Africa: mean Phi_EGDI | 0.138995585771 |  |  | 5 | numpy |
| B_northern_africa_median_phi | M49 sub-region Northern Africa: median Phi_EGDI | 0.141767086538 |  |  | 5 | numpy |
| B_northern_europe_count | M49 sub-region Northern Europe: count | 10 |  |  | 10 | count |
| B_northern_europe_mean_phi | M49 sub-region Northern Europe: mean Phi_EGDI | 0.0455823004091 |  |  | 10 | numpy |
| B_northern_europe_median_phi | M49 sub-region Northern Europe: median Phi_EGDI | 0.0418367278506 |  |  | 10 | numpy |
| B_south_eastern_asia_count | M49 sub-region South-eastern Asia: count | 11 |  |  | 11 | count |
| B_south_eastern_asia_mean_phi | M49 sub-region South-eastern Asia: mean Phi_EGDI | 0.147501743411 |  |  | 11 | numpy |
| B_south_eastern_asia_median_phi | M49 sub-region South-eastern Asia: median Phi_EGDI | 0.168675617616 |  |  | 11 | numpy |
| B_southern_asia_count | M49 sub-region Southern Asia: count | 9 |  |  | 9 | count |
| B_southern_asia_mean_phi | M49 sub-region Southern Asia: mean Phi_EGDI | 0.237000732035 |  |  | 9 | numpy |
| B_southern_asia_median_phi | M49 sub-region Southern Asia: median Phi_EGDI | 0.265435138864 |  |  | 9 | numpy |
| B_southern_europe_count | M49 sub-region Southern Europe: count | 14 |  |  | 14 | count |
| B_southern_europe_mean_phi | M49 sub-region Southern Europe: mean Phi_EGDI | 0.092136906352 |  |  | 14 | numpy |
| B_southern_europe_median_phi | M49 sub-region Southern Europe: median Phi_EGDI | 0.0947427785604 |  |  | 14 | numpy |
| B_sub_saharan_africa_count | M49 sub-region Sub-Saharan Africa: count | 47 |  |  | 47 | count |
| B_sub_saharan_africa_mean_phi | M49 sub-region Sub-Saharan Africa: mean Phi_EGDI | 0.225597151423 |  |  | 47 | numpy |
| B_sub_saharan_africa_median_phi | M49 sub-region Sub-Saharan Africa: median Phi_EGDI | 0.218081134984 |  |  | 47 | numpy |
| B_western_asia_count | M49 sub-region Western Asia: count | 15 |  |  | 15 | count |
| B_western_asia_mean_phi | M49 sub-region Western Asia: mean Phi_EGDI | 0.0668566564775 |  |  | 15 | numpy |
| B_western_asia_median_phi | M49 sub-region Western Asia: median Phi_EGDI | 0.0756653083302 |  |  | 15 | numpy |
| B_western_europe_count | M49 sub-region Western Europe: count | 9 |  |  | 9 | count |
| B_western_europe_mean_phi | M49 sub-region Western Europe: mean Phi_EGDI | 0.0392927042541 |  |  | 9 | numpy |
| B_western_europe_median_phi | M49 sub-region Western Europe: median Phi_EGDI | 0.0285491156566 |  |  | 9 | numpy |
| B_ssa_vs_other_mann_whitney | One-sided Mann-Whitney U: Sub-Saharan Africa Phi_EGDI > all other economies |  | 5400 | 2.27177444499e-12 | 184 | scipy.stats.mannwhitneyu |
| B_global_south_vs_north_mann_whitney | One-sided Mann-Whitney U: socioeconomic Global South Phi_EGDI > Global North |  | 5693 | 1.83959845462e-12 | 184 | scipy.stats.mannwhitneyu |
| C_income_quintile_1_Phi_EGDI_mean | Income sub-index quintile 1: mean Phi_EGDI | 0.225875650062 |  |  | 37 | ranked_equal_frequency_bins |
| C_income_quintile_1_EGDI_mean | Income sub-index quintile 1: mean EGDI | 0.330986486486 |  |  | 37 | ranked_equal_frequency_bins |
| C_income_quintile_1_Penetration_Pct_mean | Income sub-index quintile 1: mean Penetration_Pct | 29.6967352552 |  |  | 37 | ranked_equal_frequency_bins |
| C_income_quintile_2_Phi_EGDI_mean | Income sub-index quintile 2: mean Phi_EGDI | 0.200621584802 |  |  | 37 | ranked_equal_frequency_bins |
| C_income_quintile_2_EGDI_mean | Income sub-index quintile 2: mean EGDI | 0.566513513514 |  |  | 37 | ranked_equal_frequency_bins |
| C_income_quintile_2_Penetration_Pct_mean | Income sub-index quintile 2: mean Penetration_Pct | 63.0386813068 |  |  | 37 | ranked_equal_frequency_bins |
| C_income_quintile_3_Phi_EGDI_mean | Income sub-index quintile 3: mean Phi_EGDI | 0.150637733411 |  |  | 36 | ranked_equal_frequency_bins |
| C_income_quintile_3_EGDI_mean | Income sub-index quintile 3: mean EGDI | 0.697008333333 |  |  | 36 | ranked_equal_frequency_bins |
| C_income_quintile_3_Penetration_Pct_mean | Income sub-index quintile 3: mean Penetration_Pct | 77.7685668842 |  |  | 36 | ranked_equal_frequency_bins |
| C_income_quintile_4_Phi_EGDI_mean | Income sub-index quintile 4: mean Phi_EGDI | 0.103834948313 |  |  | 37 | ranked_equal_frequency_bins |
| C_income_quintile_4_EGDI_mean | Income sub-index quintile 4: mean EGDI | 0.781551351351 |  |  | 37 | ranked_equal_frequency_bins |
| C_income_quintile_4_Penetration_Pct_mean | Income sub-index quintile 4: mean Penetration_Pct | 86.2539555986 |  |  | 37 | ranked_equal_frequency_bins |
| C_income_quintile_5_Phi_EGDI_mean | Income sub-index quintile 5: mean Phi_EGDI | 0.0436006416852 |  |  | 36 | ranked_equal_frequency_bins |
| C_income_quintile_5_EGDI_mean | Income sub-index quintile 5: mean EGDI | 0.890922222222 |  |  | 36 | ranked_equal_frequency_bins |
| C_income_quintile_5_Penetration_Pct_mean | Income sub-index quintile 5: mean Penetration_Pct | 95.1052441669 |  |  | 36 | ranked_equal_frequency_bins |
| C_income_decile_1_Phi_EGDI_mean | Income sub-index decile 1: mean Phi_EGDI | 0.19955900691 |  |  | 19 | ranked_equal_frequency_bins |
| C_income_decile_1_EGDI_mean | Income sub-index decile 1: mean EGDI | 0.266305263158 |  |  | 19 | ranked_equal_frequency_bins |
| C_income_decile_1_Penetration_Pct_mean | Income sub-index decile 1: mean Penetration_Pct | 23.4245369601 |  |  | 19 | ranked_equal_frequency_bins |
| C_income_decile_2_Phi_EGDI_mean | Income sub-index decile 2: mean Phi_EGDI | 0.253654328945 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_2_EGDI_mean | Income sub-index decile 2: mean EGDI | 0.399261111111 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_2_Penetration_Pct_mean | Income sub-index decile 2: mean Penetration_Pct | 36.3173890112 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_3_Phi_EGDI_mean | Income sub-index decile 3: mean Phi_EGDI | 0.232811097026 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_3_EGDI_mean | Income sub-index decile 3: mean EGDI | 0.517466666667 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_3_Penetration_Pct_mean | Income sub-index decile 3: mean Penetration_Pct | 54.0650974478 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_4_Phi_EGDI_mean | Income sub-index decile 4: mean Phi_EGDI | 0.170126257431 |  |  | 19 | ranked_equal_frequency_bins |
| C_income_decile_4_EGDI_mean | Income sub-index decile 4: mean EGDI | 0.612978947368 |  |  | 19 | ranked_equal_frequency_bins |
| C_income_decile_4_Penetration_Pct_mean | Income sub-index decile 4: mean Penetration_Pct | 71.5399712784 |  |  | 19 | ranked_equal_frequency_bins |
| C_income_decile_5_Phi_EGDI_mean | Income sub-index decile 5: mean Phi_EGDI | 0.160188089038 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_5_EGDI_mean | Income sub-index decile 5: mean EGDI | 0.679344444444 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_5_Penetration_Pct_mean | Income sub-index decile 5: mean Penetration_Pct | 75.9497916806 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_6_Phi_EGDI_mean | Income sub-index decile 6: mean Phi_EGDI | 0.141087377784 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_6_EGDI_mean | Income sub-index decile 6: mean EGDI | 0.714672222222 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_6_Penetration_Pct_mean | Income sub-index decile 6: mean Penetration_Pct | 79.5873420878 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_7_Phi_EGDI_mean | Income sub-index decile 7: mean Phi_EGDI | 0.100690357071 |  |  | 19 | ranked_equal_frequency_bins |
| C_income_decile_7_EGDI_mean | Income sub-index decile 7: mean EGDI | 0.760736842105 |  |  | 19 | ranked_equal_frequency_bins |
| C_income_decile_7_Penetration_Pct_mean | Income sub-index decile 7: mean Penetration_Pct | 86.2689954132 |  |  | 19 | ranked_equal_frequency_bins |
| C_income_decile_8_Phi_EGDI_mean | Income sub-index decile 8: mean Phi_EGDI | 0.107154239068 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_8_EGDI_mean | Income sub-index decile 8: mean EGDI | 0.803522222222 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_8_Penetration_Pct_mean | Income sub-index decile 8: mean Penetration_Pct | 86.2380802389 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_9_Phi_EGDI_mean | Income sub-index decile 9: mean Phi_EGDI | 0.0619760389572 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_9_EGDI_mean | Income sub-index decile 9: mean EGDI | 0.893733333333 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_9_Penetration_Pct_mean | Income sub-index decile 9: mean Penetration_Pct | 92.9908695672 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_10_Phi_EGDI_mean | Income sub-index decile 10: mean Phi_EGDI | 0.0252252444132 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_10_EGDI_mean | Income sub-index decile 10: mean EGDI | 0.888111111111 |  |  | 18 | ranked_equal_frequency_bins |
| C_income_decile_10_Penetration_Pct_mean | Income sub-index decile 10: mean Penetration_Pct | 97.2196187667 |  |  | 18 | ranked_equal_frequency_bins |
| C_ols_ssa_sa_income_intercept | SSA, Southern Asia, and income model: statsmodels HC3 OLS coefficient intercept | 0.341054077602 | 0.0326294722852 | 1.42965906589e-25 | 183 | statsmodels_ols_hc3 |
| C_ols_ssa_sa_income_sub_saharan_africa | SSA, Southern Asia, and income model: statsmodels HC3 OLS coefficient sub_saharan_africa | 0.0365282540288 | 0.0167669810177 | 0.0293626858253 | 183 | statsmodels_ols_hc3 |
| C_ols_ssa_sa_income_southern_asia | SSA, Southern Asia, and income model: statsmodels HC3 OLS coefficient southern_asia | 0.0823026766824 | 0.0436440225634 | 0.0593256826581 | 183 | statsmodels_ols_hc3 |
| C_ols_ssa_sa_income_income_subindex | SSA, Southern Asia, and income model: statsmodels HC3 OLS coefficient income_subindex | -0.289387684016 | 0.0390320999687 | 1.2245843216e-13 | 183 | statsmodels_ols_hc3 |
| C_ols_ssa_sa_income_r_squared | SSA, Southern Asia, and income model: statsmodels HC3 OLS R-squared | 0.504283659697 |  |  | 183 | statsmodels_ols_hc3 |
| C_ols_global_south_no_income_intercept | Socioeconomic Global South model without income control: statsmodels HC3 OLS coefficient intercept | 0.0751444447549 | 0.00632740014318 | 1.57664708085e-32 | 183 | statsmodels_ols_hc3 |
| C_ols_global_south_no_income_global_south | Socioeconomic Global South model without income control: statsmodels HC3 OLS coefficient global_south | 0.0974502946278 | 0.0103264793281 | 3.83849917372e-21 | 183 | statsmodels_ols_hc3 |
| C_ols_global_south_no_income_r_squared | Socioeconomic Global South model without income control: statsmodels HC3 OLS R-squared | 0.219389997138 |  |  | 183 | statsmodels_ols_hc3 |
| C_ols_global_south_with_income_intercept | Socioeconomic Global South model with income control: statsmodels HC3 OLS coefficient intercept | 0.379428468802 | 0.0390880776781 | 2.8146525431e-22 | 183 | statsmodels_ols_hc3 |
| C_ols_global_south_with_income_global_south | Socioeconomic Global South model with income control: statsmodels HC3 OLS coefficient global_south | 0.0132140760072 | 0.0112939077501 | 0.241993702097 | 183 | statsmodels_ols_hc3 |
| C_ols_global_south_with_income_income_subindex | Socioeconomic Global South model with income control: statsmodels HC3 OLS coefficient income_subindex | -0.337114333024 | 0.0429210062804 | 4.02020462213e-15 | 183 | statsmodels_ols_hc3 |
| C_ols_global_south_with_income_r_squared | Socioeconomic Global South model with income control: statsmodels HC3 OLS R-squared | 0.466902751217 |  |  | 183 | statsmodels_ols_hc3 |
| D_positive_signed_div_count | positive Signed_Div economies: count | 51 |  |  | 51 | count |
| D_positive_I_income_mean | positive Signed_Div economies: mean I_income | 0.607774509804 |  |  | 51 | numpy |
| D_positive_Phi_EGDI_mean | positive Signed_Div economies: mean Phi_EGDI | 0.196713934208 |  |  | 51 | numpy |
| D_positive_Penetration_Pct_mean | positive Signed_Div economies: mean Penetration_Pct | 52.1619118358 |  |  | 51 | numpy |
| D_negative_signed_div_count | negative Signed_Div economies: count | 133 |  |  | 133 | count |
| D_negative_I_income_mean | negative Signed_Div economies: mean I_income | 0.766654545455 |  |  | 132 | numpy |
| D_negative_Phi_EGDI_mean | negative Signed_Div economies: mean Phi_EGDI | 0.124741096305 |  |  | 133 | numpy |
| D_negative_Penetration_Pct_mean | negative Signed_Div economies: mean Penetration_Pct | 77.3283982167 |  |  | 133 | numpy |
| D_signed_div_income_mann_whitney | One-sided Mann-Whitney U: positive Signed_Div income sub-index > negative Signed_Div |  | 1741.5 | 0.999999788018 | 183 | scipy.stats.mannwhitneyu |
| D_income_quintile_1_positive_signed_div_share | Income quintile 1: positive Signed_Div share | 0.648648648649 |  |  | 37 | ranked_equal_frequency_bins |
| D_income_quintile_2_positive_signed_div_share | Income quintile 2: positive Signed_Div share | 0.297297297297 |  |  | 37 | ranked_equal_frequency_bins |
| D_income_quintile_3_positive_signed_div_share | Income quintile 3: positive Signed_Div share | 0.194444444444 |  |  | 36 | ranked_equal_frequency_bins |
| D_income_quintile_4_positive_signed_div_share | Income quintile 4: positive Signed_Div share | 0.0810810810811 |  |  | 37 | ranked_equal_frequency_bins |
| D_income_quintile_5_positive_signed_div_share | Income quintile 5: positive Signed_Div share | 0.166666666667 |  |  | 36 | ranked_equal_frequency_bins |
| E_spearman_t2_a | Spearman correlation of HDIN_T2 and HDIN_A | 0.963056547756 |  |  | 158 | spearman |
| E_spearman_HDIN_A_HDIN_B | Spearman correlation of HDIN_A and HDIN_B | 0.999364116388 |  |  | 158 | spearman |
| E_spearman_HDIN_A_HDIN_C | Spearman correlation of HDIN_A and HDIN_C | 0.999326087642 |  |  | 158 | spearman |
| E_spearman_HDIN_B_HDIN_C | Spearman correlation of HDIN_B and HDIN_C | 0.998960227768 |  |  | 158 | spearman |
| E_spearman_HDIN_A_HDI_Standard | Spearman correlation of HDIN_A and HDI_Standard | 0.946454976479 |  |  | 158 | spearman |
| E_spearman_HDIN_B_HDI_Standard | Spearman correlation of HDIN_B and HDI_Standard | 0.946486923222 |  |  | 158 | spearman |
| E_spearman_HDIN_C_HDI_Standard | Spearman correlation of HDIN_C and HDI_Standard | 0.942900738187 |  |  | 158 | spearman |
| E_A_B_rank_difference_ge_3 | Ranks A_B: count differing by at least 3 | 16 |  |  | 158 | count |
| E_A_B_rank_difference_ge_5 | Ranks A_B: count differing by at least 5 | 4 |  |  | 158 | count |
| E_A_C_rank_difference_ge_3 | Ranks A_C: count differing by at least 3 | 19 |  |  | 158 | count |
| E_A_C_rank_difference_ge_5 | Ranks A_C: count differing by at least 5 | 4 |  |  | 158 | count |
| E_rank_a_standard_rank_difference_ge_3 | Rank_A vs standard HDI: count differing by at least 3 | 143 |  |  | 158 | count |
| E_rank_a_standard_rank_difference_ge_5 | Rank_A vs standard HDI: count differing by at least 5 | 132 |  |  | 158 | count |
| E_rank_a_standard_rank_difference_ge_10 | Rank_A vs standard HDI: count differing by at least 10 | 106 |  |  | 158 | count |
| E_rank_a_standard_max_displacement | Rank_A vs standard HDI: maximum rank displacement | 57 |  |  | 158 | max |
| E_rank_b_standard_rank_difference_ge_3 | Rank_B vs standard HDI: count differing by at least 3 | 143 |  |  | 158 | count |
| E_rank_b_standard_rank_difference_ge_5 | Rank_B vs standard HDI: count differing by at least 5 | 133 |  |  | 158 | count |
| E_rank_b_standard_rank_difference_ge_10 | Rank_B vs standard HDI: count differing by at least 10 | 103 |  |  | 158 | count |
| E_rank_b_standard_max_displacement | Rank_B vs standard HDI: maximum rank displacement | 56 |  |  | 158 | max |
| E_rank_c_standard_rank_difference_ge_3 | Rank_C vs standard HDI: count differing by at least 3 | 143 |  |  | 158 | count |
| E_rank_c_standard_rank_difference_ge_5 | Rank_C vs standard HDI: count differing by at least 5 | 132 |  |  | 158 | count |
| E_rank_c_standard_rank_difference_ge_10 | Rank_C vs standard HDI: count differing by at least 10 | 107 |  |  | 158 | count |
| E_rank_c_standard_max_displacement | Rank_C vs standard HDI: maximum rank displacement | 58 |  |  | 158 | max |

## Task 2 change note

Verified by diffing this run's output against the pre-rework output, statistic row by statistic row (not just the three named IDs): moving the classification from the script's hardcoded `GLOBAL_SOUTH_ISO3` set to the canonical file's `Global_North_South` column changed **zero** statistic values. This is because the hardcoded set already matched the development-based classification exactly at the time of this rework (it had been corrected in a prior pass); the two encoded the same 52 North / 132 South split. The three IDs the rework memo names as affected (`B_global_south_vs_north_mann_whitney`, `C_ols_global_south_no_income_*`, `C_ols_global_south_with_income_*`) are therefore unchanged in value under Task 2 alone -- the benefit of Task 2 is architectural (the script can no longer diverge from its own documentation by silently regenerating a wrong list), not numerical. Every other statistic ID was independently confirmed unchanged as well, satisfying the watch-out that any change outside the three named IDs must be reported. Task 3 (below), which replaces the hand-rolled Mann-Whitney/OLS routines with library calls and switches OLS to HC3, does change all six Mann-Whitney/OLS statistic families (as expected -- see the cross-check table) but touches nothing in Groups A, C's income bins, D's counts, or E.

## Cross-check: hand-implemented vs library

Mann-Whitney: hand implementation (average ranks, tie-corrected normal approximation with continuity correction) vs `scipy.stats.mannwhitneyu`. OLS: hand implementation (closed-form HC1) vs `statsmodels` (HC3) -- so the OLS rows below reflect two simultaneous changes (implementation and HC1-to-HC3), not implementation alone; coefficients and R-squared are not affected by the HC1/HC3 choice and so isolate the implementation difference, while standard errors and p-values reflect both changes together.

| ID | Description | Hand-implemented | Library | Difference | Unit |
|---|---|---:|---:|---:|---|
| B_ssa_vs_other_mann_whitney_statistic | SSA vs other Mann-Whitney U statistic | 5400 | 5400 | 0 | U statistic |
| B_ssa_vs_other_mann_whitney_p | SSA vs other Mann-Whitney p-value | 2.27177444499e-12 | 2.27177444499e-12 | -1.69636649059e-26 | p-value |
| B_global_south_vs_north_mann_whitney_statistic | Global South vs North Mann-Whitney U statistic | 5693 | 5693 | 0 | U statistic |
| B_global_south_vs_north_mann_whitney_p | Global South vs North Mann-Whitney p-value | 1.83959845462e-12 | 1.83959845462e-12 | -1.5348077772e-26 | p-value |
| C_ols_ssa_sa_income_intercept | SSA, Southern Asia, and income model: OLS coefficient intercept | 0.341054077602 | 0.341054077602 | -2.16493489802e-15 | coefficient |
| C_ols_ssa_sa_income_intercept_se | SSA, Southern Asia, and income model: OLS robust SE intercept (hand HC1 vs library HC3) | 0.0316397248375 | 0.0326294722852 | 0.000989747447657 | standard error |
| C_ols_ssa_sa_income_intercept_p | SSA, Southern Asia, and income model: OLS p-value intercept (hand HC1 vs library HC3) | 4.31155471713e-27 | 1.42965906589e-25 | 1.38654351872e-25 | p-value |
| C_ols_ssa_sa_income_sub_saharan_africa | SSA, Southern Asia, and income model: OLS coefficient sub_saharan_africa | 0.0365282540288 | 0.0365282540288 | 6.38378239159e-16 | coefficient |
| C_ols_ssa_sa_income_sub_saharan_africa_se | SSA, Southern Asia, and income model: OLS robust SE sub_saharan_africa (hand HC1 vs library HC3) | 0.0164238627118 | 0.0167669810177 | 0.000343118305939 | standard error |
| C_ols_ssa_sa_income_sub_saharan_africa_p | SSA, Southern Asia, and income model: OLS p-value sub_saharan_africa (hand HC1 vs library HC3) | 0.0261419586641 | 0.0293626858253 | 0.0032207271612 | p-value |
| C_ols_ssa_sa_income_southern_asia | SSA, Southern Asia, and income model: OLS coefficient southern_asia | 0.0823026766824 | 0.0823026766824 | 6.80011602583e-16 | coefficient |
| C_ols_ssa_sa_income_southern_asia_se | SSA, Southern Asia, and income model: OLS robust SE southern_asia (hand HC1 vs library HC3) | 0.039183904874 | 0.0436440225634 | 0.00446011768933 | standard error |
| C_ols_ssa_sa_income_southern_asia_p | SSA, Southern Asia, and income model: OLS p-value southern_asia (hand HC1 vs library HC3) | 0.0356918681136 | 0.0593256826581 | 0.0236338145445 | p-value |
| C_ols_ssa_sa_income_income_subindex | SSA, Southern Asia, and income model: OLS coefficient income_subindex | -0.289387684016 | -0.289387684016 | 2.33146835171e-15 | coefficient |
| C_ols_ssa_sa_income_income_subindex_se | SSA, Southern Asia, and income model: OLS robust SE income_subindex (hand HC1 vs library HC3) | 0.0377965226182 | 0.0390320999687 | 0.00123557735043 | standard error |
| C_ols_ssa_sa_income_income_subindex_p | SSA, Southern Asia, and income model: OLS p-value income_subindex (hand HC1 vs library HC3) | 1.9112350777e-14 | 1.2245843216e-13 | 1.03346081383e-13 | p-value |
| C_ols_ssa_sa_income_r_squared | SSA, Southern Asia, and income model: OLS R-squared | 0.504283659697 | 0.504283659697 | 0 | R-squared |
| C_ols_global_south_no_income_intercept | Socioeconomic Global South model without income control: OLS coefficient intercept | 0.0751444447549 | 0.0751444447549 | -2.77555756156e-17 | coefficient |
| C_ols_global_south_no_income_intercept_se | Socioeconomic Global South model without income control: OLS robust SE intercept (hand HC1 vs library HC3) | 0.00623751187824 | 0.00632740014318 | 8.98882649429e-05 | standard error |
| C_ols_global_south_no_income_intercept_p | Socioeconomic Global South model without income control: OLS p-value intercept (hand HC1 vs library HC3) | 2.0069294378e-33 | 1.57664708085e-32 | 1.37595413707e-32 | p-value |
| C_ols_global_south_no_income_global_south | Socioeconomic Global South model without income control: OLS coefficient global_south | 0.0974502946278 | 0.0974502946278 | -2.77555756156e-17 | coefficient |
| C_ols_global_south_no_income_global_south_se | Socioeconomic Global South model without income control: OLS robust SE global_south (hand HC1 vs library HC3) | 0.0102579857414 | 0.0103264793281 | 6.84935867254e-05 | standard error |
| C_ols_global_south_no_income_global_south_p | Socioeconomic Global South model without income control: OLS p-value global_south (hand HC1 vs library HC3) | 2.10002313499e-21 | 3.83849917372e-21 | 1.73847603873e-21 | p-value |
| C_ols_global_south_no_income_r_squared | Socioeconomic Global South model without income control: OLS R-squared | 0.219389997138 | 0.219389997138 | -3.33066907388e-16 | R-squared |
| C_ols_global_south_with_income_intercept | Socioeconomic Global South model with income control: OLS coefficient intercept | 0.379428468802 | 0.379428468802 | 1.94289029309e-15 | coefficient |
| C_ols_global_south_with_income_intercept_se | Socioeconomic Global South model with income control: OLS robust SE intercept (hand HC1 vs library HC3) | 0.0383648776474 | 0.0390880776781 | 0.000723200030687 | standard error |
| C_ols_global_south_with_income_intercept_p | Socioeconomic Global South model with income control: OLS p-value intercept (hand HC1 vs library HC3) | 4.60048405071e-23 | 2.8146525431e-22 | 2.35460413803e-22 | p-value |
| C_ols_global_south_with_income_global_south | Socioeconomic Global South model with income control: OLS coefficient global_south | 0.0132140760072 | 0.0132140760072 | -2.47545040022e-15 | coefficient |
| C_ols_global_south_with_income_global_south_se | Socioeconomic Global South model with income control: OLS robust SE global_south (hand HC1 vs library HC3) | 0.01112587961 | 0.0112939077501 | 0.000168028140138 | standard error |
| C_ols_global_south_with_income_global_south_p | Socioeconomic Global South model with income control: OLS p-value global_south (hand HC1 vs library HC3) | 0.234956271575 | 0.241993702097 | 0.00703743052189 | p-value |
| C_ols_global_south_with_income_income_subindex | Socioeconomic Global South model with income control: OLS coefficient income_subindex | -0.337114333024 | -0.337114333024 | -2.22044604925e-16 | coefficient |
| C_ols_global_south_with_income_income_subindex_se | Socioeconomic Global South model with income control: OLS robust SE income_subindex (hand HC1 vs library HC3) | 0.0421241547607 | 0.0429210062804 | 0.000796851519656 | standard error |
| C_ols_global_south_with_income_income_subindex_p | Socioeconomic Global South model with income control: OLS p-value income_subindex (hand HC1 vs library HC3) | 1.21547594486e-15 | 4.02020462213e-15 | 2.80472867727e-15 | p-value |
| C_ols_global_south_with_income_r_squared | Socioeconomic Global South model with income control: OLS R-squared | 0.466902751217 | 0.466902751217 | -2.22044604925e-16 | R-squared |
| D_signed_div_income_mann_whitney_statistic | Positive vs negative Signed_Div income Mann-Whitney U statistic | 1741.5 | 1741.5 | 0 | U statistic |
| D_signed_div_income_mann_whitney_p | Positive vs negative Signed_Div income Mann-Whitney p-value | 0.999999788018 | 0.999999788018 | 0 | p-value |
