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
pathcorrection = "../"

DIR_00_tematdb_raw_excel         =  pathcorrection+ "data_000_tematdb_raw_excel/"
DIR_10_tematdb_converted_to_csv  =  pathcorrection+ "data_100_tematdb_csv_converted/"
DIR_30_tematdb_extTEP_csv        =  pathcorrection+ "data_300_tematdb_extTEP_csv/"
DIR_40_tematdb_ZT_error          =  pathcorrection+ "data_400_tematdb_ZT_error/"
DIR_50_tematdb_ZT_filter         =  pathcorrection+ "data_500_filter_table/"
DIR_99_tematdb_summary_meta      =  pathcorrection+ "data_900_tematdb_meta/"

filename_metadataexcel        =  pathcorrection+ "_tematdb_v1.1.6_metadata-20250514.xlsx"
filename_complete_TEP         =  DIR_10_tematdb_converted_to_csv + "tematdb_v1.1.6_completeTEPset.csv"
filename_extended_TEP         =  DIR_30_tematdb_extTEP_csv       + "tematdb_v1.1.6_extendedZTset_dT2K.csv"
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

## db info
dbname = 'tematdb'
dbversion = "v1.1.6"
dbpubname = 'teMatDb272'

## make a metadata
df_tematdb_metadata = df_meta.copy()

df = df_tematdb_metadata.merge( df_scZT_filtered_def[['sample_id','cri_product']], on= ['sample_id'],how='left')
df.rename( columns={'cri_product': 'cri_product_def'}, inplace=True)

df = df[ df.cri_product_def == True]
df['dbname'] = dbname
df['dbversion'] = dbversion
df['dbpubname'] = dbpubname

col_meta = ['dbname',
            'dbversion',
            'dbpubname',
            'sample_id','YEAR', 'URL',
            'DOI', 'figure_number_of_targetZT', 'label_of_targetZT_in_figure',
            'figure_label_description', 
            'mat_dimension(bulk, film, 1D, 2D)', 
            'GROUP', 'BASEMAT','Composition_by_element', 'Composition_detailed',
            'SINTERING'   ]



df = df[col_meta]
df.reset_index(inplace=True, drop=True)
df_tematdb_metadata = df.copy()
df_tematdb_metadata.to_csv(f"{dbpubname}.csv", index=False, encoding="UTF-8-SIG")
df_tematdb_metadata.to_csv(f"{dbpubname}_{formattedDate}.csv", index=False, encoding="UTF-8-SIG")

