import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Load canonical dataset
df_canon = pd.read_csv(r'c:\Users\Aarav Gupta\Downloads\Research_ashu\step_14\HDIN_Canonical_v2.csv')

# Load Findex dataset
df_findex = pd.read_csv(r'c:\Users\Aarav Gupta\Downloads\Research_ashu\step15\GlobalFindexDatabase2025_downloaded.csv', low_memory=False)
df_findex_all = df_findex[(df_findex['group'] == 'all') & (df_findex['group2'] == 'all')]

# Latest year per country
df_latest = df_findex_all.sort_values(['codewb', 'year']).groupby('codewb').last().reset_index()

merged = pd.merge(df_canon, df_latest, left_on='ISO3', right_on='codewb', how='inner')
print(f'Total matched canonical: {len(merged)}')

indicators = {
    'GovPay_Pct': ('fing2p_acc', 'Received government payments: into an account (%, age 15+)'),
    'DigitalPay_Pct': ('g20_any', 'Made or received a digital payment (%, age 15+)'),
    'MobileAccess_Pct (dig_acc)': ('dig_acc', 'Digitally enabled account (%, age 15+)'),
    'MobileAccess_Pct (fin9b)': ('fin9b', 'Used a mobile phone or the internet to check account balance (%, age 15+)'),
    'MobileAccess_Pct (fin3)': ('fin3', 'Used a card or mobile phone to make payments (%, age 15+)'),
    'MobileAccess_Pct (fin26a)': ('fin26a', 'Used a mobile phone or the internet to pay bills (%, age 15+)')
}

for label, (col, desc) in indicators.items():
    print(f'\n=======================================================')
    print(f'INDICATOR: {label} (Column: {col})')
    print(f'Description: {desc}')
    sub = merged.dropna(subset=['EGDI', 'I_income', 'Phi_EGDI', col]).copy()
    N = len(sub)
    print(f'N = {N}')
    
    # Model 1
    X1 = sm.add_constant(sub[['EGDI', 'I_income']])
    m1 = sm.OLS(sub[col], X1).fit(cov_type='HC3')
    
    # Model 2
    X2 = sm.add_constant(sub[['EGDI', 'I_income', 'Phi_EGDI']])
    m2 = sm.OLS(sub[col], X2).fit(cov_type='HC3')
    
    print('MODEL 1 (Baseline):')
    print(f'  const:    coef={m1.params["const"]:.4f}, se={m1.bse["const"]:.4f}, p={m1.pvalues["const"]:.4f}')
    print(f'  EGDI:     coef={m1.params["EGDI"]:.4f}, se={m1.bse["EGDI"]:.4f}, p={m1.pvalues["EGDI"]:.4f}')
    print(f'  I_income: coef={m1.params["I_income"]:.4f}, se={m1.bse["I_income"]:.4f}, p={m1.pvalues["I_income"]:.4f}')
    print(f'  R2={m1.rsquared:.4f}, R2_adj={m1.rsquared_adj:.4f}')
    
    print('MODEL 2 (Test):')
    print(f'  const:    coef={m2.params["const"]:.4f}, se={m2.bse["const"]:.4f}, p={m2.pvalues["const"]:.4f}')
    print(f'  EGDI:     coef={m2.params["EGDI"]:.4f}, se={m2.bse["EGDI"]:.4f}, p={m2.pvalues["EGDI"]:.4f}')
    print(f'  I_income: coef={m2.params["I_income"]:.4f}, se={m2.bse["I_income"]:.4f}, p={m2.pvalues["I_income"]:.4f}')
    print(f'  Phi_EGDI: coef={m2.params["Phi_EGDI"]:.4f}, se={m2.bse["Phi_EGDI"]:.4f}, p={m2.pvalues["Phi_EGDI"]:.4f}')
    print(f'  R2={m2.rsquared:.4f}, delta_R2={m2.rsquared - m1.rsquared:.4f}')
