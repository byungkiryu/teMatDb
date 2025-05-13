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
DIR_00_tematdb_raw_excel         =  "./data_00_tematdb_raw_excel/"
DIR_10_tematdb_converted_to_csv  =  "./data_10_tematdb_csv_converted/"
DIR_30_tematdb_extTEP_csv        =  "./data_30_tematdb_extTEP_csv/"
DIR_40_tematdb_ZT_error          =  "./data_40_tematdb_ZT_error/"

file_tematdb_metadata_excel   =  "./" + "_tematdb_metadata_v1.1.6-20250224.xlsx"
file_tematdb_db_csv         =  DIR_10_tematdb_converted_to_csv + "tematdb_v1.1.6_completeTEPset.csv"
file_tematdb_db_extZT_csv   =  DIR_30_tematdb_extTEP_csv       + "tematdb_v1.1.6_extendedZTset_dT2K.csv"
file_tematdb_error_csv      =  DIR_40_tematdb_ZT_error         + "ZT_error.csv"

df_tematdb_meta             = pd.read_excel( file_tematdb_metadata_excel, 'list')
df_tematdb_csv              = pd.read_csv(file_tematdb_db_csv)
df_tematdb_extended_csv     = pd.read_csv( file_tematdb_db_extZT_csv )
df_tematdb_ZTerr            = pd.read_csv( file_tematdb_error_csv )


 
cri_cols = ['d_avgZT', 
            'd_peakZT',
            'errdZT_Linf', 'errdZT_L2',
            'errdZT_Linf_over_avg_ZT_ofTEPEval',
            'errdZT_Linf_over_peak_ZT_ofTEPEval'
            ]

df_db_error = df_tematdb_ZTerr[['sample_id']+cri_cols].copy()
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
    df_db_error.to_excel(f"Figure_DB_representative_after_filtering_def/teMatDb_error_anal{temptemp}.xlsx",index=False)

df_tematdb_error_anal = df_db_error.copy()



ZT0 = df_tematdb_csv[df_tematdb_csv.tepname == 'ZT']    
ZT0 = pd.merge(ZT0, df_tematdb_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
ZT0 = ZT0[ZT0.all_pass == True]
plt.figure()

plt.scatter(ZT0.Temperature, ZT0.tepvalue)
plt.show()

    
