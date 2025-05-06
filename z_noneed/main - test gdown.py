# -*- coding: utf-8 -*-
"""
Created on Tue May  6 23:05:51 2025

@author: cta4r
"""



import gdown
import pandas as pd


# @st.cache_data
def load_csv(filepath):
    return pd.read_csv(filepath,  encoding="euc-kr" )

# @st.cache_data
def load_excel(filepath,sheet_name):
    return pd.read_excel(filepath,sheet_name=sheet_name)

# @st.cache_data
def load_feather(filepath):
    return pd.read_feather(filepath)




read_method = 'pandas'
read_method = 'gdown'



if (read_method == 'gdown'):
    prefix = "20250210_rawdata"

    print("___ read metadata")    
    PATh_starry   = "../030 starrydata2502 to csv and filter  -- 20250506/"
    PATH_metadata = PATh_starry + "/999_Starrydata2_rawdata_meta/"
    PATH_metadata = PATH_metadata +"_Starrydata2_20250201_rawdata_meta_ZTfilterable_.xlsx"
    df_starry_meta0 = load_excel(PATH_metadata, sheet_name='20250201_rawdata', )       
    
    
    file_csv = 'temp.csv'
    glink_id = "1zB7h-Zqv2uf0JQS1aWd9oX03d7uXblfu"
    url = f"https://drive.google.com/uc?export=download&id={glink_id}"
    gdown.download(url, file_csv, quiet=False)
    df_starry_meta0 = load_csv(file_csv)
    
    # df_db_meta = df_starry_meta0
    # df_db_meta.index = list(df_db_meta.sample_id.copy())
    # df_db_meta['TF_mat_complete'] = df_db_meta['pykeri_TEPZT_readable']
    # df_db_meta['doi'] = df_db_meta['DOI']
    
    # print("___ read tep feathers")    
    # PATH_tep_feather  = PATh_starry+"100_teps/"
    # df_alpha0 = load_feather(PATH_tep_feather+"20250201_rawdata_alpha.feather")
    # df_rho0   = load_feather(PATH_tep_feather+"20250201_rawdata_rho.feather")
    # df_kappa0 = load_feather(PATH_tep_feather+"20250201_rawdata_kappa.feather")
    # df_ZT0    = load_feather(PATH_tep_feather+"20250201_rawdata_ZT.feather")

    # for df in [df_alpha0, df_rho0, df_kappa0, df_ZT0]:
    #     if 'temperature' in df.columns:
    #         df['Temperature'] = df['temperature']
    
    # df_db_csv = pd.concat( [df_alpha0, df_rho0, df_kappa0, df_ZT0], ignore_index=True)
    
    
    # print("___ read exTEP feathers")    
    # PATH_exTEP = PATh_starry+"300_extended_teps/"
    # PATH_exTEP = PATH_exTEP  +"extendedTEPset_2K__20250506_180300.feather"
    # df_db_extended_csv = load_feather(PATH_exTEP )
    # df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_autoTcTh_range ]
    # df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_ZT_author_declared ] 
    
    
    # print("___ read exTEP feathers")   
    # file_tematdb_error_csv = PATh_starry+"400_ZT_error/"
    # file_tematdb_error_csv = file_tematdb_error_csv+"ZT_error_table.csv"
    # df_db_error0 = pd.read_csv(file_tematdb_error_csv)
    # df_db_error = pd.merge( df_db_error0, df_db_meta, on='sample_id', how='left')
    # df_db_error.index = list(df_db_error.sample_id.copy())     




if (read_method == 'pandas'):
    prefix = "20250210_rawdata"

    print("___ read metadata")    
    PATh_starry   = "../030 starrydata2502 to csv and filter  -- 20250506/"
    PATH_metadata = PATh_starry + "/999_Starrydata2_rawdata_meta/"
    PATH_metadata = PATH_metadata +"_Starrydata2_20250201_rawdata_meta_ZTfilterable_.xlsx"
    df_starry_meta0 = load_excel(PATH_metadata, sheet_name='20250201_rawdata', )       
    df_db_meta = df_starry_meta0
    df_db_meta.index = list(df_db_meta.sample_id.copy())
    df_db_meta['TF_mat_complete'] = df_db_meta['pykeri_TEPZT_readable']
    df_db_meta['doi'] = df_db_meta['DOI']
    
    print("___ read tep feathers")    
    PATH_tep_feather  = PATh_starry+"100_teps/"
    df_alpha0 = load_feather(PATH_tep_feather+"20250201_rawdata_alpha.feather")
    df_rho0   = load_feather(PATH_tep_feather+"20250201_rawdata_rho.feather")
    df_kappa0 = load_feather(PATH_tep_feather+"20250201_rawdata_kappa.feather")
    df_ZT0    = load_feather(PATH_tep_feather+"20250201_rawdata_ZT.feather")

    for df in [df_alpha0, df_rho0, df_kappa0, df_ZT0]:
        if 'temperature' in df.columns:
            df['Temperature'] = df['temperature']
    
    df_db_csv = pd.concat( [df_alpha0, df_rho0, df_kappa0, df_ZT0], ignore_index=True)
    
    
    print("___ read exTEP feathers")    
    PATH_exTEP = PATh_starry+"300_extended_teps/"
    PATH_exTEP = PATH_exTEP  +"extendedTEPset_2K__20250506_180300.feather"
    df_db_extended_csv = load_feather(PATH_exTEP )
    df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_autoTcTh_range ]
    df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_ZT_author_declared ] 
    
    
    print("___ read exTEP feathers")   
    file_tematdb_error_csv = PATh_starry+"400_ZT_error/"
    file_tematdb_error_csv = file_tematdb_error_csv+"ZT_error_table.csv"
    df_db_error0 = pd.read_csv(file_tematdb_error_csv)
    df_db_error = pd.merge( df_db_error0, df_db_meta, on='sample_id', how='left')
    df_db_error.index = list(df_db_error.sample_id.copy())        
    