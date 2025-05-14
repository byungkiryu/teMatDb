# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 20:46:53 2023

@author: cta4r
"""


import sys
import os

# 현재 실행 중인 파일 기준, 특정 폴더를 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.join(current_dir, '../')  # 예: ./library/mylib.py
sys.path.append(main_dir)

# import mylib  # 이제 가능

import numpy as np
import pandas as pd
import time as time
import json
from datetime import datetime


from library.tematdb_util import make_doi_url
from pykeri.byungkiryu import byungkiryu_util as br
formattedDate, yyyymmdd, HHMMSS = br.now_string()
# time00 = time.time()

def load_csv(filepath):
    return pd.read_csv(filepath,  encoding='utf-8-sig')

def load_excel(filepath,sheet_name):
    return pd.read_excel(filepath,sheet_name=sheet_name)

def load_feather(filepath):
    return pd.read_feather(filepath)




# ## db info
# dbname = 'tematdb'
# dbversion = "v1.1.6"

## DIR setting
pathcorrection = main_dir

DIR_00_tematdb_raw_excel         =  pathcorrection+ "data_000_tematdb_raw_excel/"
DIR_10_tematdb_converted_to_csv  =  pathcorrection+ "data_100_tematdb_csv_converted/"
DIR_30_tematdb_extTEP_csv        =  pathcorrection+ "data_300_tematdb_extTEP_csv/"
DIR_40_tematdb_ZT_error          =  pathcorrection+ "data_400_tematdb_ZT_error/"
DIR_50_tematdb_ZT_filter         =  pathcorrection+ "data_500_filter_table/"
DIR_99_tematdb_summary_meta      =  pathcorrection+ "data_900_tematdb_meta/"

filename_metadataexcel        =  pathcorrection+ "_tematdb_v1.1.6_metadata-20250514.xlsx"
filename_complete_TEP         =  DIR_10_tematdb_converted_to_csv + "tematdb_v1.1.6_completeTEPset.csv"
filename_extended_TEP         =  DIR_30_tematdb_extTEP_csv       + "tematdb_v1.1.6_extendedTEPset_dT2K.csv"
filename_ZT_error_dropna      =  DIR_40_tematdb_ZT_error +"ZT_error_table_dropna.csv" 
filename_scZT_filtered_def    =  DIR_50_tematdb_ZT_filter+"crieria_10_10_10_10_20_20_results_filtered_scZT.csv"
filename_scZT_filtered_1o2    =  DIR_50_tematdb_ZT_filter+"crieria_05_05_05_05_10_10_results_filtered_scZT.csv"
filename_scZT_filtered_1o5    =  DIR_50_tematdb_ZT_filter+"crieria_02_02_02_02_04_04_results_filtered_scZT.csv"

df_meta               = load_excel(    filename_metadataexcel, 'list')
df_complete_csv       = load_csv(      filename_complete_TEP         )
df_extended_csv       = load_csv(      filename_extended_TEP         )
df_ZT_error_dropna    = load_csv(      filename_ZT_error_dropna      )
df_scZT_filtered_def  = pd.read_csv(   filename_scZT_filtered_def,  encoding="UTF-8-SIG")
df_scZT_filtered_1o2  = pd.read_csv(   filename_scZT_filtered_1o2,  encoding="UTF-8-SIG")
df_scZT_filtered_1o5  = pd.read_csv(   filename_scZT_filtered_1o5,  encoding="UTF-8-SIG")



df_scZT_filtered = df_scZT_filtered_def.copy()
cri_product_criteriastring = df_scZT_filtered_def.cri_product_criteriastring.unique()[0]

####### sample_ids for db_publication
def get_db_publication_sample_ids(df_in, col_name):
    sample_ids = df_in[df_in[col_name] == True]['sample_id']
    sample_ids = sample_ids.drop_duplicates().to_list()
    sample_ids.sort()
    return sample_ids
db_publication_sample_ids = get_db_publication_sample_ids(df_scZT_filtered, "cri_product")





####### db info
####### db info
####### db info
####### db info
dbname              = 'teMatDb'
dbversion           = "v1.1.6"
db_publication_id   = 'teMatDb272'
prefix = f"{dbname}"

db_publication_path = f"{db_publication_id}_dataset_20250515/"
db_mother           = f"{dbname}_{dbversion}"
db_full_id          = f"{db_publication_id}_{dbversion}"


filenamelist =[f"{prefix}_samples",
               f"{prefix}_TEPcurves",
               f"{prefix}_TEPcollocated",
               ]
# filenamelist =["metadata",
#                "rawdata_teps",
#                "collocated_teps",
#                ]
fileformatlist =["csv",
               "csv",
               "csv",
               ]

####### sample metadata
####### sample metadata
####### sample metadata
####### sample metadata
df_tematdb_sample_metadata = df_scZT_filtered[ df_scZT_filtered["cri_product"]  == True]
col_base = ["sample_id","DOI"]
df = df_tematdb_sample_metadata[ col_base ].copy()

df = df.merge( df_meta, on=col_base, how='left')

col_meta = [  'sample_id','YEAR', 'DOI', 
            'figure_number_of_targetZT', 'label_of_targetZT_in_figure',
            'figure_label_description', 
            'mat_dimension(bulk, film, 1D, 2D)', 
            'GROUP', 'BASEMAT','Composition_by_element', 'Composition_detailed',
            'SINTERING'   ]

df = df[col_meta]
df.reset_index(inplace=True, drop=True)
df_tematdb_sample_metadata = df.copy()
filename = filenamelist[0]
df_tematdb_sample_metadata.to_csv(db_publication_path+f"{filename}.csv", index=False, encoding="UTF-8-SIG")
# df_tematdb_sample_metadata.to_csv(db_publication_path+f"{filename}_{formattedDate}.csv", index=False, encoding="UTF-8-SIG")



####### complete teps
####### complete teps
####### complete teps
####### complete teps
col_compelte_teps =   [  'sample_id', 'tepname', 'Temperature', 'tepvalue', 'unit', 
                       'dbversionlabel', 'update', 'TF_matzt_complete'  ]
df_tematdb_complete_teps = df_complete_csv[df_complete_csv['sample_id'].isin(db_publication_sample_ids)].copy()
df_tematdb_complete_teps = df_tematdb_complete_teps[  col_compelte_teps  ].copy()
df_tematdb_complete_teps.reset_index(inplace=True, drop=True)

filename = filenamelist[1]
df_tematdb_complete_teps.to_csv(db_publication_path+f"{filename}.csv", index=False, encoding="UTF-8-SIG")
# df_tematdb_complete_teps.to_csv(db_publication_path+f"{filename}_{formattedDate}.csv", index=False, encoding="UTF-8-SIG")




####### collocated teps
col_collocated_teps = ['sample_id', 'Temperature', 
                       'alpha', 'rho', 'kappa',
                       'RK', 'sigma', 'PF','ZT_tep_reevaluated']
df_tematdb_collocated_teps = df_extended_csv[df_extended_csv['sample_id'].isin(db_publication_sample_ids)].copy()
df_tematdb_collocated_teps = df_tematdb_collocated_teps[ df_tematdb_collocated_teps['is_Temp_in_TEPZT'] == True].copy()

df_tematdb_collocated_teps = df_tematdb_collocated_teps[col_collocated_teps]
df_tematdb_collocated_teps['ZT'] = df_tematdb_collocated_teps["ZT_tep_reevaluated"].copy()

df_tematdb_collocated_teps.reset_index(inplace=True, drop=True)


filename = filenamelist[2]
df_tematdb_collocated_teps.to_csv(db_publication_path+f"{filename}.csv", index=False, encoding="UTF-8-SIG")
# df_tematdb_collocated_teps.to_csv(db_publication_path+f"{filename}_{formattedDate}.csv", index=False, encoding="UTF-8-SIG")






num_sample_id        = df_tematdb_sample_metadata['sample_id'].nunique()
num_DOI              = df_tematdb_sample_metadata['DOI'].nunique()
len_complete_teps    = len( df_tematdb_complete_teps )
len_collocated_teps  = len( df_tematdb_collocated_teps )





report_dict = {}
report_dict['scZT_filter'] = cri_product_criteriastring
report_dict['dbname'] = dbname
report_dict['dbversion'] = dbversion
report_dict['db_mother'] = db_mother
report_dict['db_publication_id'] = db_publication_id
report_dict['db_full_id'] = db_full_id


data_dict = {}
data_dict['num_sample_id (samples)'] = num_sample_id
data_dict['num_DOI (papers)'] = num_DOI
data_dict['len_complete_teps'] = len_complete_teps
data_dict['len_collocated_teps'] = len_collocated_teps
data_dict['dT_unit for temp collocation'] = 2

file_dict = {}
file_dict['filename for sample_id metadata']    = filenamelist[0] + "." + fileformatlist[0]
file_dict['filename for rawdata  teps']         = filenamelist[1] + "." + fileformatlist[1]
file_dict['filename for collated teps']         = filenamelist[2] + "." + fileformatlist[2]
file_dict['formattedDate']  = formattedDate


report_string = ""
report_string = report_string + "_____Generated on: {}\n".format(formattedDate)
# report_string = report_string + "_____teMatDb by Byungki Ryu from KERI, Korea\n"
report_string = report_string + "  Publicate teMatDb for thermoelectric property curves: {}\n".format(db_publication_id)
report_string = report_string + "\n"
report_string = report_string + "  Developer: Dr. Byungki Ryu from KERI, Changwon, 51543, Republic of Korea(south)\n"
report_string = report_string + "\n"
report_string = report_string + "  DB info\n"
for key, value in report_dict.items():
    report_line = f"    {key}: {value}"
    report_string = report_string + report_line + "\n"

report_string = report_string + "\n"
report_string = report_string + "  Data stats of dataset for TEP (thermoelectric properties)\n"
for key, value in data_dict.items():
    report_line = f"    {key}: {value}"
    report_string = report_string + report_line + "\n"

report_string = report_string + "\n"
report_string = report_string + "  Filename information\n"
for description, filename in file_dict.items():
    report_line = "    {:40}: {}".format(filename, description)
    report_string = report_string + report_line + "\n"



print(report_string)
with open(db_publication_path+ f"z_{prefix}_report.txt", "w", encoding="utf-8") as file:
    file.write(report_string)
