# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 17:37:32 2025

@author: cta4r
"""



import numpy as np
import pandas as pd
import time as time

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
DIR_00_tematdb_raw_excel         =  "./data_00_tematdb_raw_excel/"
DIR_10_tematdb_converted_to_csv  =  "./data_10_tematdb_csv_converted/"
DIR_30_tematdb_extTEP_csv        =  "./data_30_tematdb_extTEP_csv/"
DIR_40_tematdb_ZT_error          =  "./data_40_tematdb_ZT_error/"
DIR_50_tematdb_ZT_filter         =  "./data_50_filter_table/"

file_tematdb_metadata_excel   =  "./" + "_tematdb_metadata_v1.1.6-20250224.xlsx"
file_tematdb_db_csv         =  DIR_10_tematdb_converted_to_csv + "tematdb_v1.1.6_completeTEPset.csv"
file_tematdb_db_extZT_csv   =  DIR_30_tematdb_extTEP_csv       + "tematdb_v1.1.6_extendedZTset_dT2K.csv"
file_tematdb_error_csv      =  DIR_40_tematdb_ZT_error         + "ZT_error_table_dropna.csv"

df_tematdb_meta             = load_excel(  file_tematdb_metadata_excel, 'list')
df_tematdb_csv              = load_csv(    file_tematdb_db_csv)
df_tematdb_extended_csv     = load_csv(    file_tematdb_db_extZT_csv )
df_tematdb_ZT_error         = load_csv(    file_tematdb_error_csv )




df_ZT_error0 = df_tematdb_ZT_error.copy()
df_ZT_error  = df_tematdb_ZT_error.copy()






# 1. 빈 문자열을 NaN으로 변환
# 2. inf, -inf 를 NaN으로 변환
# 3. NaN이 포함된 행 제거
# df_ZT_error = df_ZT_error.replace('', np.nan)
# df_ZT_error = df_ZT_error.replace([np.inf, -np.inf], np.nan)
# df_ZT_error = df_ZT_error.dropna()

cols_df_sample_id = ['DOI', 'sample_id']
df_tematdb_meta_sample_id   = df_tematdb_meta[ cols_df_sample_id ].drop_duplicates()





criteria_list_def = [0.10, 0.10, 0.10, 0.10, 0.20, 0.20]
def make_filter_table_using_criteria_list(criteria_list = criteria_list_def):
    df_ZT_filter = df_ZT_error0.copy()
    cri0, cri1, cri2, cri3, cri4, cri5 = criteria_list
    criteriastring = "crieria_" + "_".join([str(int(c * 100)).zfill(2) for c in criteria_list])
    
    df_ZT_filter['criT:  tempratura range > 0'] =  df_ZT_error['fraction_Ts_TEPZToverTEPZTex'] > 0
    df_ZT_filter['criZT: representative ZT > 0 '] =   (df_ZT_error['avg_ZT_ofRawFig']>0)   \
                                               & (df_ZT_error['avg_ZT_ofTEPEval']>0) \
                                               & (df_ZT_error['peak_ZT_ofRawFig']>0) \
                                               & (df_ZT_error['peak_ZT_ofTEPEval']>0) 
                                               
    df_ZT_filter[f'cri0:  d_avgZT  < {cri0}'] = np.abs( df_ZT_error['d_avgZT']  ) < cri0
    df_ZT_filter[f'cri1:  d_peakZT < {cri1}'] = np.abs( df_ZT_error['d_peakZT'] ) < cri1    
    df_ZT_filter[f'cri2:  errdZT_Linf < {cri2}'] = df_ZT_error['errdZT_Linf'] < cri2
    df_ZT_filter[f'cri3:  errdZT_L2 < {cri3}'] = df_ZT_error['errdZT_L2'] < cri3    
    df_ZT_filter[f'cri4:  errdZT_Linf_over_avg_ZT_ofRawFig < {cri4}'] \
                            = np.abs(df_ZT_error['errdZT_Linf_over_avg_ZT_ofTEPEval']) < cri4
    df_ZT_filter[f'cri5:  errdZT_Linf_over_peak_ZT_ofRawFig < {cri5}'] \
                            = np.abs(df_ZT_error['errdZT_Linf_over_peak_ZT_ofTEPEval']) < cri5
    
    cri_columns = [col for col in df_ZT_filter.columns if col.startswith('cri')]

    
    df_ZT_filter['cri_product_criteriastring'] = criteriastring
    df_ZT_filter['cri_product'] = ( df_ZT_filter[cri_columns].prod(axis=1) == True)
    df_ZT_filter_on_metadata = pd.merge( df_tematdb_meta_sample_id, 
                                           df_ZT_filter, on='sample_id', how='left'  )
    
    filename_results_filtered_scZT = f"{criteriastring}_results_filtered_scZT"
    df_ZT_filter.to_csv( DIR_50_tematdb_ZT_filter+ filename_results_filtered_scZT +  ".csv"                  ,index=False)
    df_ZT_filter.to_csv( DIR_50_tematdb_ZT_filter+ f"FormmatedOn{formattedDate}_"+filename_results_filtered_scZT + ".csv"  ,index=False)
        
    # df_ZT_filter_on_metadata.to_feather(path_500_filter_table+ f"FormmatedOn{formattedDate}_"+filename_results_filtered_scZT +  "_over_meta.feather")
    
    
    # dup_ids = df_ZT_filter.sample_id[df_ZT_filter_on_metadata.sample_id.duplicated(keep=False)]
    # dup_DOIs = df_ZT_filter.DOI[df_ZT_filter_on_metadata.sample_id.duplicated(keep=False)]
    # print("duplication in df_ZT_filter            : ",dup_ids,  dup_DOIs)
    
    
    return df_ZT_filter
 


       
       

criteria_list_def = [0.10, 0.10, 0.10, 0.10, 0.20, 0.20]
criteria_list_1ov2 = (np.array(criteria_list_def) / 2).tolist()
criteria_list_1ov5 = (np.array(criteria_list_def) / 5).tolist()

##########
criteria_list = criteria_list_def.copy()
cri0, cri1, cri2, cri3, cri4, cri5 = criteria_list
df_ZT_filter = make_filter_table_using_criteria_list(criteria_list)
cri_string = [f'cri0:  d_avgZT  < {cri0}',
       f'cri1:  d_peakZT < {cri1}',
       f'cri2:  errdZT_Linf < {cri2}',
       f'cri3:  errdZT_L2 < {cri3}',
       f'cri4:  errdZT_Linf_over_avg_ZT_ofRawFig < {cri4}',
       f'cri5:  errdZT_Linf_over_peak_ZT_ofRawFig < {cri5}']

##########
criteria_list = criteria_list_1ov2.copy()
cri0, cri1, cri2, cri3, cri4, cri5 = criteria_list
make_filter_table_using_criteria_list(criteria_list)

##########
criteria_list = criteria_list_1ov5.copy()
cri0, cri1, cri2, cri3, cri4, cri5 = criteria_list
make_filter_table_using_criteria_list(criteria_list)



##########
df_tepzt_filter     = df_ZT_error0.copy()
df_tepzt_filter['before_filter'] = True

df_after_self_ZT_filtered  = df_ZT_filter[ df_ZT_filter.cri_product == True ][['DOI','sample_id']].copy()
df_after_self_ZT_filtered['sc_ZT_filtered'] = True

# df_after_classic_filtered  = df_classic_filter[ df_classic_filter.all_filters == True][['SID','sample_id']].copy()
# df_after_classic_filtered['classical_filtered'] = True

df_tepzt_filter = df_tepzt_filter.merge( df_after_self_ZT_filtered, on=['DOI','sample_id'], how='left')
# df_tepzt_filter = df_tepzt_filter.merge( df_after_classic_filtered, on=['SID','sample_id'], how='left')

from matplotlib import pyplot as plt    

figsize = (7,4)
fig, axs = plt.subplots(1,2, figsize=figsize,dpi=300)
ax1, ax2 = axs
alpha = 0.5

ZT1 = 'peak_ZT_ofRawFig'
ZT2 = 'peak_ZT_ofTEPEval'

# ZT1_label = "Peak ZT from figure raw ZT"
# ZT2_label = "Peak ZT from TEP reevaluated"
ZT1_label = "Peak raw ZT (from figure)"
ZT2_label = "Peak  re-evaluated ZT (from TEPs)"



filtering_list = ['before_filter','sc_ZT_filtered']
label_list = ['before filter','sc-ZT filter']

for idx, filtering in enumerate(filtering_list):
    
    label = label_list[idx]
    filteredd = df_tepzt_filter[ df_tepzt_filter[filtering] == True ]
    print(filtering, len(filteredd) )
    
    zt_eval = filteredd[ZT1]
    zt_decl = filteredd[ZT2]
    
    ax1.scatter( zt_eval, zt_decl, label=label, alpha=alpha, edgecolors='none')
    
    ax2.scatter( zt_eval, zt_decl, label=label, alpha=alpha, edgecolors='none')




for ax in [ax1, ax2]:
    ax.set_xlabel(ZT1_label)
    ax.set_ylabel(ZT2_label)
    
diag = [1e-3,1e1]
diag2 = [0,3.5]
ax1.plot(diag,diag,ls='dotted')
ax2.plot(diag2,diag2,ls='dotted')


ax1.set_title("(a)",loc='left')
ax2.set_title("(b)",loc='left')

ax1.set_xscale('log')
ax1.set_yscale('log')
# # plt.xlim(-0.5,10.5)
# # plt.ylim(-0.5,10.5)
ax1.legend()

# ax2.set_xlim(-0.1,3.5)
# ax2.set_ylim(-0.5,3.5)
ax2.legend()

titlestring = ""
titlestring = titlestring+ f"Filtered ZT-ZT plots over [{dbname} ({dbversion})]"
titlestring = titlestring+ f"\n sc-ZT filter with criteria={criteria_list_def}" 

plt.suptitle(titlestring)
plt.tight_layout()
plt.show()

criteriastring = "crieria_" + "_".join([str(int(c * 100)).zfill(2) for c in criteria_list_def])
fig.savefig(DIR_50_tematdb_ZT_filter+f"Figure_ZT-ZT plots {criteriastring}.png",dpi=300)




