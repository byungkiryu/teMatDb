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


if (0):
    ## read tematdb
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
    
    
    
    ## read starry
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





df = df_starry_csv[ df_starry_csv.tepname == 'kappa']
kappa_anomaly_SIDs = df[ (df.tepvalue > 500) | (df.tepvalue < 0) ].SID.unique()
# kappa_anomaly_SIDs = df[ (df.tepvalue < 0) ].SID.unique()

df = df_starry_csv[ df_starry_csv.tepname == 'rho']
# rho_anomaly_SIDs   = df[ (df.tepvalue > 500) | (df.tepvalue < 0) ].SID.unique()
rho_anomaly_SIDs   = df[ (df.tepvalue < 0) ].SID.unique()

# kappa_anomaly_SIDs = []
# rho_anomaly_SIDs = []


figsize=(7.2,7.2)
alphas = [0.3, 0.8]


fig, axs = plt.subplots(2,2, figsize=figsize )
ax1, ax2 = axs[0]
ax3, ax4 = axs[1]
labels = ['Starrydata2','teMatDb']    

## for kappa
if (1):
    
    ax = ax3
    tepname = 'kappa'
    
    
    df_tematdb_error_anal = pd.read_excel("Figure_DB_representative_after_filtering_def/tematdb_error_anal.xlsx")
    df_starry_error_anal = pd.read_excel("Figure_DB_representative_after_filtering_def/Starry_error_anal.xlsx")
    
    ZTtematdb0 = df_tematdb_csv[df_tematdb_csv.tepname == tepname]    
    ZTtematdb = pd.merge(ZTtematdb0, df_tematdb_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
    ZTtematdb = ZTtematdb[ZTtematdb.all_pass == True]
    
    ZTstarry0 = df_starry_csv[df_starry_csv.tepname == tepname]    
    ZTstarry = pd.merge(ZTstarry0, df_starry_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
    ZTstarry = ZTstarry[ZTstarry.all_pass == True]
    
    ZTstarry2 =  ZTstarry
    ZTstarry2 =  ZTstarry2[~ZTstarry2.SID.isin(kappa_anomaly_SIDs)]
    ZTstarry2 =  ZTstarry2[~ZTstarry2.SID.isin(rho_anomaly_SIDs)]
    
    
    
    df1 = ZTtematdb
    df2 = ZTstarry2
    
    
    for idx, row in enumerate(zip([df2, df1], labels ) ):
        df, label = row
        alpha = alphas[idx]
        ax.scatter(df.Temperature, df.tepvalue, alpha=alpha, label=label )
    ax.set_yscale('log')
    ax.set_ylabel('Thermal conductivity [W m$^{-1}$ K$^{-1}$]')
    ax.set_xlabel('Temperature [K]')
    

## for rho
if (1):
    ax = ax2
    tepname = 'rho'
    
    
    df_tematdb_error_anal = pd.read_excel("Figure_DB_representative_after_filtering_def/tematdb_error_anal.xlsx")
    df_starry_error_anal = pd.read_excel("Figure_DB_representative_after_filtering_def/Starry_error_anal.xlsx")
    
    ZTtematdb0 = df_tematdb_csv[df_tematdb_csv.tepname == tepname]    
    ZTtematdb = pd.merge(ZTtematdb0, df_tematdb_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
    ZTtematdb = ZTtematdb[ZTtematdb.all_pass == True]
    
    ZTstarry0 = df_starry_csv[df_starry_csv.tepname == tepname]    
    ZTstarry = pd.merge(ZTstarry0, df_starry_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
    ZTstarry = ZTstarry[ZTstarry.all_pass == True]
    
    ZTstarry2 =  ZTstarry
    ZTstarry2 =  ZTstarry2[~ZTstarry2.SID.isin(kappa_anomaly_SIDs)]
    ZTstarry2 =  ZTstarry2[~ZTstarry2.SID.isin(rho_anomaly_SIDs)]
    
    
    
    df1 = ZTtematdb
    df2 = ZTstarry2
    
    # labels = ['Starrydata2','teMatDb']    
    for idx, row in enumerate(zip([df2, df1], labels ) ):
        df, label = row
        alpha = alphas[idx]
        ax.scatter(df.Temperature, df.tepvalue, alpha=alpha, label=label )
    ax.set_yscale('log')
    ax.set_ylabel(r'Electrical resistivity [$\Omega$ m]')
    ax.set_xlabel('Temperature [K]')



## for Seebeck
if (1):
    ax = ax1
    tepname = 'alpha'
    
    
    df_tematdb_error_anal = pd.read_excel("Figure_DB_representative_after_filtering_def/tematdb_error_anal.xlsx")
    df_starry_error_anal = pd.read_excel("Figure_DB_representative_after_filtering_def/Starry_error_anal.xlsx")
    
    ZTtematdb0 = df_tematdb_csv[df_tematdb_csv.tepname == tepname]    
    ZTtematdb = pd.merge(ZTtematdb0, df_tematdb_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
    ZTtematdb = ZTtematdb[ZTtematdb.all_pass == True]
    
    ZTstarry0 = df_starry_csv[df_starry_csv.tepname == tepname]    
    ZTstarry = pd.merge(ZTstarry0, df_starry_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
    ZTstarry = ZTstarry[ZTstarry.all_pass == True]
    
    ZTstarry2 =  ZTstarry
    ZTstarry2 =  ZTstarry2[~ZTstarry2.SID.isin(kappa_anomaly_SIDs)]
    ZTstarry2 =  ZTstarry2[~ZTstarry2.SID.isin(rho_anomaly_SIDs)]
    
    
    df1 = ZTtematdb
    df2 = ZTstarry2
    
    # labels = ['Starrydata2','teMatDb']    
    for idx, row in enumerate(zip([df2, df1], labels ) ):
        df, label = row
        alpha = alphas[idx]
        ax.scatter(df.Temperature, df.tepvalue*1e3, alpha=alpha, label=label )
    # ax.set_yscale('log')
    ax.set_ylabel(r'Seebeck coefficient [mV K$^{-1}$]')
    ax.set_xlabel('Temperature [K]')

    
    
## for ZT
if (1):
    ax = ax4
    tepname = 'ZT'    
    
    df_tematdb_error_anal = pd.read_excel("Figure_DB_representative_after_filtering_def/tematdb_error_anal.xlsx")
    df_starry_error_anal = pd.read_excel("Figure_DB_representative_after_filtering_def/Starry_error_anal.xlsx")
    
    ZTtematdb0 = df_tematdb_csv[df_tematdb_csv.tepname == tepname]    
    ZTtematdb = pd.merge(ZTtematdb0, df_tematdb_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
    ZTtematdb = ZTtematdb[ZTtematdb.all_pass == True]
    
    ZTstarry0 = df_starry_csv[df_starry_csv.tepname == tepname]    
    ZTstarry = pd.merge(ZTstarry0, df_starry_error_anal[['sample_id',"all_pass"]],  on='sample_id', how='left')
    ZTstarry = ZTstarry[ZTstarry.all_pass == True]
    
    ZTstarry2 =  ZTstarry
    ZTstarry2 =  ZTstarry2[~ZTstarry2.SID.isin(kappa_anomaly_SIDs)]
    ZTstarry2 =  ZTstarry2[~ZTstarry2.SID.isin(rho_anomaly_SIDs)]
    
    
    df1 = ZTtematdb
    df2 = ZTstarry2
    
    # alphas = [0.3, 0.8]
    # labels = ['Starrydata2','teMatDb']    
    for idx, row in enumerate(zip([df2, df1], labels ) ):
        df, label = row
        alpha = alphas[idx]
        ax.scatter(df.Temperature, df.tepvalue, alpha=alpha, label=label )
    # ax.set_yscale('log')
    ax.set_ylabel(r'ZT')
    ax.set_xlabel('Temperature [K]')


ax1.set_title("(a)",loc='left')
ax2.set_title("(b)",loc='left')
ax3.set_title("(c)",loc='left')
ax4.set_title("(d)",loc='left')

for ax in [ax1,ax2,ax3,ax4]:
    ax.legend()


fig.tight_layout()
fig.show()


import shutil
formattedDate, yyyymmdd, HHMMSS = br.now_string()
figfile1 =  "Figure_DB_representative_after_filtering_def/figure.png"
figfile2 = f"Figure_DB_representative_after_filtering_def/figure_{formattedDate}.png"

fig.savefig(figfile1,dpi=500)
shutil.copy(figfile1, figfile2) 

