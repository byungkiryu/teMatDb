# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 20:46:53 2023

@author: cta4r
"""




import numpy as np
import pandas as pd
import time as time
import json
from datetime import datetime

from pykeri.byungkiryu import byungkiryu_util as br


def load_csv(filepath):
    return pd.read_csv(filepath,  encoding='utf-8-sig')

def load_excel(filepath,sheet_name):
    return pd.read_excel(filepath,sheet_name=sheet_name)

def load_feather(filepath):
    return pd.read_feather(filepath)


formattedDate, yyyymmdd, HHMMSS = br.now_string()
time00 = time.time()


## db info
dbname = 'tematdb'
dbversion = "v1.1.6"

## DIR setting
DIR_00_tematdb_raw_excel         =  "data_000_tematdb_raw_excel/"
DIR_10_tematdb_converted_to_csv  =  "data_100_tematdb_csv_converted/"
DIR_30_tematdb_extTEP_csv        =  "data_300_tematdb_extTEP_csv/"
DIR_40_tematdb_ZT_error          =  "data_400_tematdb_ZT_error/"
DIR_50_tematdb_ZT_filter         =  "data_500_filter_table/"
DIR_99_tematdb_summary_meta      =  "data_900_tematdb_meta/"

filename_metadataexcel       =   "_tematdb_v1.1.6_metadata-20250224.xlsx"
filename_complete_TEP        =  DIR_10_tematdb_converted_to_csv + "tematdb_v1.1.6_completeTEPset.csv"
filename_extended_TEP        =  DIR_30_tematdb_extTEP_csv       + "tematdb_v1.1.6_extendedZTset_dT2K.csv"
filename_ZT_error_dropna     = DIR_40_tematdb_ZT_error +"ZT_error_table_dropna.csv" 
filename_scZT_filtered_def   = DIR_50_tematdb_ZT_filter+"crieria_10_10_10_10_20_20_results_filtered_scZT.csv"
filename_scZT_filtered_1o2   = DIR_50_tematdb_ZT_filter+"crieria_05_05_05_05_10_10_results_filtered_scZT.csv"
filename_scZT_filtered_1o5   = DIR_50_tematdb_ZT_filter+"crieria_02_02_02_02_04_04_results_filtered_scZT.csv"



df_meta               = load_excel(  filename_metadataexcel, 'list')
df_complete_csv       = load_csv(    filename_complete_TEP)
df_extended_csv       = load_csv(    filename_extended_TEP )
df_ZT_error_dropna    = load_csv(    filename_ZT_error_dropna )
df_scZT_filtered_def  = pd.read_csv(   filename_scZT_filtered_def,  encoding="UTF-8-SIG")
df_scZT_filtered_1o2  = pd.read_csv(   filename_scZT_filtered_1o2,  encoding="UTF-8-SIG")
df_scZT_filtered_1o5  = pd.read_csv(   filename_scZT_filtered_1o5,  encoding="UTF-8-SIG")



filename_list = [ filename_metadataexcel,
                  filename_complete_TEP,
                  filename_extended_TEP,
                  filename_ZT_error_dropna,
                  filename_scZT_filtered_def,
                  filename_scZT_filtered_1o2,
                  filename_scZT_filtered_1o5
                  ]

df_list = [       df_meta,
                  df_complete_csv,
                  df_extended_csv,
                  df_ZT_error_dropna,
                  df_scZT_filtered_def,
                  df_scZT_filtered_1o2,
                  df_scZT_filtered_1o5
                  ]

for idx, df in enumerate(df_list):
    print(filename_list[idx])
    print(df.columns)
                  # df_meta,
                  # df_complete_csv,
                  # df_extended_csv,
                  # df_ZT_error_dropna,
                  # df_scZT_filtered_def,
                  # df_scZT_filtered_1o2,
                  # df_scZT_filtered_1o5
                  
###############
###############
###############
cols = ['DOI', 'sample_id', 'YEAR']
df_tematdb_meta_samples   = df_meta[ cols ].drop_duplicates(['DOI','sample_id'])
df_tematdb_meta_samples['DOIlink'] = "https://DOI.org/"+df_tematdb_meta_samples['DOI']
df_tematdb_meta_samples['dbnanme']   = dbname
df_tematdb_meta_samples['dbversion'] = dbversion


###############
###############
###############
cols =  ['sample_id',  'pykeri_compatible', 'TF_matzt_complete']
df = df_complete_csv[cols]
df = df.drop_duplicates(subset= ['sample_id'])
df_tematdb_meta_samples = df_tematdb_meta_samples.merge( df, on= ['sample_id'],how='left')

 # 'TF_matzt_complete',

###############
###############
###############
cols =  ['sample_id',  'TF_mat_complete', 
       'fraction_Ts_TEPZToverTEPZTex', 'is_Temperature_range_valid', 'autoTc',
       'autoTh', 'ztTc', 'ztTh', 'Tc_ofTEP', 'Th_ofTEP', 'Tc_ofZT', 'Th_ofZT',
       'Tc_ofTEPZT', 'Th_ofTEPZT', 'deltaT_ofTEP', 'deltaT_ofZT',
       'deltaT_ofTEPZT', 'avg_ZT_ofRawFig', 'avg_ZT_ofTEPEval',
       'peak_ZT_ofRawFig', 'peak_ZT_ofTEPEval', 'd_Tmid', 'd_avgZT',
       'd_peakZT', 'errdZT_Linf', 'errdZT_L2', 'errdZT_L1',
       'is_avg_ZT_ofRawFig_positiveFinite',
       'is_avg_ZT_ofTEPEval_positiveFinite',
       'ispeak_ZT_ofRawFig_positiveFinite',
       'is_peak_ZT_ofTEPEval_positiveFinite',
       'errdZT_Linf_over_avg_ZT_ofRawFig', 'errdZT_Linf_over_avg_ZT_ofTEPEval',
       'errdZT_Linf_over_peak_ZT_ofRawFig',
       'errdZT_Linf_over_peak_ZT_ofTEPEval']
df = df_ZT_error_dropna[cols]
df_tematdb_meta_samples = df_tematdb_meta_samples.merge( df, on= ['sample_id'],how='left')




###############
###############
###############
cols =  ['sample_id', 'cri_product',]  
df = df_scZT_filtered_def[cols]
df = df[ df.cri_product ]
df.rename( columns={'cri_product': 'cri_product_def'},inplace=True)
df_tematdb_meta_samples = df_tematdb_meta_samples.merge( df, on= ['sample_id'],how='left')

df = df_scZT_filtered_1o2[cols]
df = df[ df.cri_product ]
df.rename( columns={'cri_product': 'cri_product_1o2'},inplace=True)
df_tematdb_meta_samples = df_tematdb_meta_samples.merge( df, on= ['sample_id'],how='left')

df = df_scZT_filtered_1o5[cols]
df = df[ df.cri_product ]
df.rename( columns={'cri_product': 'cri_product_1o5'},inplace=True)
df_tematdb_meta_samples = df_tematdb_meta_samples.merge( df, on= ['sample_id'],how='left')


cols_filter = ['cri_product_def', 'cri_product_1o2', 'cri_product_1o5']
df_tematdb_meta_samples[cols_filter] = df_tematdb_meta_samples[cols_filter].notna()

formattedDate, yyyymmdd, HHMMSS = br.now_string()
filename_meta_sample = DIR_99_tematdb_summary_meta+f"{dbname}_{dbversion}__meta_samples-scZT_clas_filteres-{formattedDate}"
df_tematdb_meta_samples.to_csv(     filename_meta_sample+".csv", encoding="UTF-8-SIG",index=False)
df_tematdb_meta_samples.to_excel(   filename_meta_sample+".xlsx",sheet_name=dbname+" "+dbversion,index=False)




## report
df0 = df_tematdb_meta_samples.copy()
df = df0
print("all data cases")
print("SID and sample_id pair unique cases: ", len(df))
nunique_series = df.nunique()  # 기본값 dropna=True
for col, count in nunique_series.items():
    print(f"Column '{col}' has {count} unique non-null values.\t{col}\t{count}")
print()
true_counts = (df.apply(lambda col: col.map(lambda x: x is True))).sum()
for col, truecount in true_counts.items():
    print(f"Column '{col}' has {truecount} True values.\t{col}\t{truecount}")
print()


print()
print( "nunique DOIs for TF_mat_complete", df[ df.TF_matzt_complete == True ].sample_id.nunique()   )
print( "nunique DOIs for cri_product_def", df[ df.cri_product_def == True ].sample_id.nunique()   )
print( "nunique DOIs for cri_product_1o2", df[ df.cri_product_1o2 == True ].sample_id.nunique()   )
print( "nunique DOIs for cri_product_1o5", df[ df.cri_product_1o5 == True ].sample_id.nunique()   )

print()
print( "nunique DOIs for TF_mat_complete", df[ df.TF_matzt_complete == True ].DOI.nunique()   )
print( "nunique DOIs for cri_product_def", df[ df.cri_product_def == True ].DOI.nunique()   )
print( "nunique DOIs for cri_product_1o2", df[ df.cri_product_1o2 == True ].DOI.nunique()   )
print( "nunique DOIs for cri_product_1o5", df[ df.cri_product_1o5 == True ].DOI.nunique()   )

# col_TF = ['is_SID_not_duplicated',
#             'is_sample_id_not_duplicated',
#             'pykeri_TEP_readable',
#             'pykeri_TEPZT_readable', 
#             'TF_matzt_complete', 
#             'classic_all_filters',
#             'cri_product_def', 
#             'cri_product_1o2', 
#             'cri_product_1o5']
# col_anal = ['SID', 'DOI', 'composition', 'sample_id']

# df_anal =   df_starry_meta_samples[col_anal].copy()
# df_TF   =   df_starry_meta_samples[col_TF].copy()

# # 조건 이름 리스트 초기화
# index_names = []

# # 조건별 유니크 카운트 리스트 생성
# temp_series_list = []

# temp_series_list.append(df_anal.nunique())
# index_names.append("ALL")  # 마지막 행 이름

# # 조건별 처리
# for col in col_TF:
#     temp_series = df_anal[df_TF[col]==True]
#     temp_series_list.append(temp_series.nunique())
#     index_names.append(col)  # 해당 조건 이름 추가

# # 조건 없이 전체 유니크 카운트도 추가

   
# # DataFrame 생성
# df_counts = pd.DataFrame(temp_series_list, index=index_names)
