# Step 14 Legacy Reconciliation

Legacy sources: `HDI_FN/output/Table_2_EGDI_Neutrosophic.csv` and `HDI_FN/output/Table_1_Raw_Digital.csv`.

| Country | Cell | Canonical value | Legacy value | Absolute difference | Downstream quantity affected |
|---|---|---:|---:|---:|---|
| Iceland | EGDI | 0.9671 | 0.967 | 0.0001 | Phi_EGDI |
| Iceland | Phi_EGDI | 0.01983908195333006 | 0.0205139923 | 0.00067491034666994 | none |
| Norway | EGDI | 0.9315 | 0.931 | 0.0005 | Phi_EGDI |
| Norway | Phi_EGDI | 0.009314975967299985 | 0.0099999741999999 | 0.000684998232699915 | none |
| Netherlands | EGDI | 0.9538 | 0.953 | 0.0008 | Phi_EGDI |
| Netherlands | Phi_EGDI | 0.028549115656640037 | 0.0299319728 | 0.001382857143359963 | none |
| Denmark | EGDI | 0.9847 | 0.984 | 0.0007 | Phi_EGDI |
| Denmark | Phi_EGDI | 0.012056745871410016 | 0.0122440803 | 0.000187334428589984 | none |
| Switzerland | EGDI | 0.9004 | 0.9 | 0.0004 | Phi_EGDI |
| Switzerland | Phi_EGDI | 0.02391132646507999 | 0.0265563376999999 | 0.00264501123491991 | none |
| Canada | EGDI | 0.8452 | 0.845 | 0.0002 | Phi_EGDI |
| Canada | Phi_EGDI | 0.04948390901735996 | 0.0585469817999999 | 0.00906307278263994 | none |
| Republic of Korea | EGDI | 0.9679 | 0.967 | 0.0009 | Phi_EGDI |
| Republic of Korea | Phi_EGDI | 0.02501078010437997 | 0.0258402521999999 | 0.00082947209561993 | none |
| France | EGDI | 0.8744 | 0.874 | 0.0004 | Phi_EGDI |
| France | Phi_EGDI | 0.11510288660983996 | 0.1316364210999999 | 0.01653353449015994 | none |
| Finland | EGDI | 0.9575 | 0.957 | 0.0005 | Phi_EGDI |
| Finland | Phi_EGDI | 0.06210487906874995 | 0.0648614924999999 | 0.00275661343124995 | none |
| Germany | EGDI | 0.9382 | 0.938 | 0.0002 | Phi_EGDI |
| Germany | Phi_EGDI | 0.07058663755340004 | 0.075236237 | 0.00464959944659996 | none |
| Australia | EGDI | 0.9577 | 0.957 | 0.0007 | Phi_EGDI |
| Australia | Phi_EGDI | 0.03719614381950007 | 0.038839035 | 0.00164289118049993 | none |
| Japan | EGDI | 0.9351 | 0.935 | 0.0001 | Phi_EGDI |
| Japan | Phi_EGDI | 0.14017239751455007 | 0.1499009705 | 0.00972857298544993 | none |
| China | EGDI | 0.8718 | 0.871 | 0.0008 | Phi_EGDI |
| China | Phi_EGDI | 0.08194920000000007 | 0.094 | 0.01205079999999993 | none |
| Indonesia | EGDI | 0.7991 | 0.799 | 0.0001 | Phi_EGDI |
| Indonesia | Phi_EGDI | 0.24605595096985997 | 0.3079163445999999 | 0.06186039363013993 | none |
| Morocco | EGDI | 0.6841 | 0.684 | 0.0001 | Phi_EGDI |
| Morocco | Phi_EGDI | 0.061568999999999985 | 0.0899999999999999 | 0.028430999999999915 | none |
| Pakistan | EGDI | 0.5096 | 0.509 | 0.0006 | Phi_EGDI |
| Pakistan | Phi_EGDI | 0.41310724000000004 | 0.81065 | 0.39754275999999996 | none |
| Burkina Faso | EGDI | 0.2895 | 0.289 | 0.0005 | Phi_EGDI |
| Burkina Faso | Phi_EGDI | 0.21607932504465 | 0.7463879967 | 0.53030867165535 | none |
| Philippines | EGDI | 0.7621 | 0.762 | 0.0001 | Phi_EGDI |
| Philippines | Phi_EGDI | 0.16867561761583003 | 0.2213300323 | 0.05265441468416997 | none |
| Nepal | EGDI | 0.5781 | 0.578 | 0.0001 | Phi_EGDI |
| Nepal | Phi_EGDI | 0.31329088434396 | 0.5419319916 | 0.22864110725604 | none |
| Bangladesh | EGDI | 0.6570 | 0.656 | 0.0010 | Phi_EGDI |
| Bangladesh | Phi_EGDI | 0.3646169853885 | 0.5549725805 | 0.1903555951115 | none |

Cells differing above 1e-12: 40.
Legacy economies without a canonical country-name match: none.

Bangladesh is retained as an audit discrepancy: canonical EGDI is 0.6570, while the legacy file reports 0.656. No source or legacy value was modified.
