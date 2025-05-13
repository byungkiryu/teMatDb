# -*- coding: utf-8 -*-
"""
Created on Fri May  9 18:28:07 2025

@author: byungkiryu
"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pykeri.byungkiryu import byungkiryu_util as br
formattedDate, yyyymmdd, HHMMSS = br.now_string()



## read tematdb csv

## DIR setting

prefix = "20250210_rawdata"
PATh_starry   = "./postprocessed_Starrydata2_20250210_rawdata__analyzed20250507/"


PATH_metadata = PATh_starry + "/999_Starrydata2_rawdata_meta/"
PATH_metadata = PATH_metadata +"_Starrydata2_20250201_rawdata_meta_ZTfilterable_.xlsx"
df_starry_meta0 = pd.read_excel(PATH_metadata, sheet_name='20250201_rawdata', )       
df_db_meta = df_starry_meta0
df_db_meta.index = list(df_db_meta.sample_id.copy())
df_db_meta['TF_mat_complete'] = df_db_meta['pykeri_TEPZT_readable']
df_db_meta['doi'] = df_db_meta['DOI']


PATH_tep_feather  = PATh_starry+"100_teps/"
df_alpha0 = pd.read_feather(PATH_tep_feather+"20250201_rawdata_alpha.feather")
df_rho0   = pd.read_feather(PATH_tep_feather+"20250201_rawdata_rho.feather")
df_kappa0 = pd.read_feather(PATH_tep_feather+"20250201_rawdata_kappa.feather")
df_ZT0    = pd.read_feather(PATH_tep_feather+"20250201_rawdata_ZT.feather")

for df in [df_alpha0, df_rho0, df_kappa0, df_ZT0]:
    if 'temperature' in df.columns:
        df['Temperature'] = df['temperature']


df_db_csv = pd.concat( [df_alpha0, df_rho0, df_kappa0, df_ZT0], ignore_index=True)


PATH_exTEP = PATh_starry+"300_extended_teps/"
PATH_exTEP = PATH_exTEP  +"extendedZTset_4K.feather"
# PATH_exTEP = PATH_exTEP  +"extendedTEPset_2K__20250506_180300.feather"
df_db_extended_csv = pd.read_feather(PATH_exTEP )
# df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_autoTcTh_range ]
# df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_ZT_author_declared ] 


file_tematdb_error_csv = PATh_starry+"400_ZT_error/"
file_tematdb_error_csv = file_tematdb_error_csv+"ZT_error_table.csv"
df_db_error0 = pd.read_csv(file_tematdb_error_csv)
df_db_error = pd.merge( df_db_error0, df_db_meta, on='sample_id', how='left')
df_db_error.index = list(df_db_error.sample_id.copy())     


df_starry_meta             = df_db_meta.copy()
df_starry_csv              = df_db_csv.copy()
# df_starry_extended_csv     = df_db_extended_csv.copy()
df_starry_ZTerr            = df_db_error.copy()




cri_cols = ['d_avgZT', 
            'd_peakZT',
            'errdZT_Linf', 'errdZT_L2',
            'errdZT_Linf_over_avg_ZT_ofTEPEval',
            'errdZT_Linf_over_peak_ZT_ofTEPEval'
            ]

df_db_error = df_starry_ZTerr[['sample_id']+cri_cols].copy()
df_db_error.index = list(df_db_error.sample_id.copy())   
cri_vals = [0.10, 0.10, 0.10, 0.10, 0.20, 0.20]
col_filters = []
    
df_db_error_criteria_list = []
error_criteria_list = []
sample_id_list_df_db_error_criteria = []
df_db_error['all_pass'] = True
for idx, row in enumerate(zip(cri_cols, cri_vals) ):   
    cri_col, cri_val = row       
    col_filter = "cri{}: {} <= {}".format(idx, cri_col,cri_val)
    col_filters.append(col_filter)
    print( col_filter )
    df_db_error.loc[:, col_filter] = df_db_error[cri_col] < cri_val
    
    df_db_error['all_pass'] = df_db_error['all_pass'] * df_db_error[col_filter]

# df_db_error['all_pass'] = df_db_error[cri_cols].prod(axis=1).astype(bool)

for temptemp in ["","__{}".format(formattedDate)]:
    path = "Figure_DB_representative_after_filtering_def/"
    df_db_error.to_excel(f"{path}/Starry_error_anal{temptemp}.xlsx",index=False)

df_starry_error_anal = df_db_error.copy()


ZT = df_starry_csv[df_starry_csv.tepname == 'ZT']    
ZT = pd.merge(ZT, df_starry_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
ZT = ZT[ZT.all_pass == True]
plt.figure()

plt.scatter(ZT.Temperature, ZT.tepvalue, )
plt.show()
