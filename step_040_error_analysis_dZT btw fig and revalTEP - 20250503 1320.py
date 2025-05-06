# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""


import os
import numpy as np
import pandas as pd
# import streamlit as st


from pykeri.scidata.matprop import MatProp
from pykeri.thermoelectrics.TEProp_xls import TEProp as TEProp_xls


from pykeri.byungkiryu import byungkiryu_util as br
 

def tep_generator_from_excel_files(sample_id, interp_opt):    
    files = os.listdir(DIR_00_tematdb_raw_excel)
    
    fileindex = int((sample_id-1)/50)
    filename = files[fileindex]
    sheetname = "#{:05d}".format(sample_id)        
    TF_mat_complete = False
    
    try:
        mat = TEProp_xls.from_dict({'xls_filename': DIR_00_tematdb_raw_excel+filename,
                                'sheetname': sheetname, 'color': (sample_id/255, 0/255, 0/255)} ) 
        TF_mat_complete = True     
        mat.set_interp_opt(interp_opt)
        # print(sample_id)
        return TF_mat_complete, mat
    except:
        print(filename, sample_id, 'data set is incompelete or empty')
        TF_mat_complete = False
        mat = False        
        return TF_mat_complete, mat

def error_analysis(sample_id):
    

    report_dict = {}
    ## read sample extended teps
    
    doi, doilink = get_doi(sample_id)    
    report_dict['sample_id']  = sample_id
    report_dict['doi']  = doi
    report_dict['doilink']  = doilink
    
    
    TF_mat_complete, mat = tep_generator_from_excel_files(sample_id, interp_opt)   
    report_dict['TF_mat_complete'] = TF_mat_complete
    df_extended_tep_sample = df_extended_teps[ df_extended_teps.sample_id == sample_id]
    
    
    ## check end points of temperature ranges
    autoTc = df_extended_tep_sample.autoTc.tolist()[0]
    autoTh = df_extended_tep_sample.autoTh.tolist()[0]
    ztTc   = df_extended_tep_sample.ztTc.tolist()[0]
    ztTh   = df_extended_tep_sample.ztTh.tolist()[0]
    
    ## slice and make a df for a given Ts range
    df_Ts_TEP     = df_extended_tep_sample[ df_extended_tep_sample.is_Temp_in_autoTcTh_range     ].copy()
    df_Ts_ZT      = df_extended_tep_sample[ df_extended_tep_sample.is_Temp_in_ZT_author_declared ].copy()
    df_Ts_TEPZT   = df_extended_tep_sample[ df_extended_tep_sample.is_Temp_in_TEPZT              ].copy()
    df_Ts_TEPZTex = df_extended_tep_sample[ df_extended_tep_sample.is_Temp_in_TEPZTex            ].copy()
    
    ## 유효 온도범위가 0인 경우 numpy 등 크기, 평균 계산 때 데이터 0개짜리가 문제 됨.
    ## eg. sample_id = 786
    
    len_df_Ts_TEP = len( df_Ts_TEP )
    len_df_Ts_ZT = len( df_Ts_ZT )
    len_df_Ts_TEPZT = len( df_Ts_TEPZT )
    len_df_Ts_TEPZTex = len( df_Ts_TEPZTex )
    
    len_df_Ts_product = len_df_Ts_TEP * len_df_Ts_ZT * len_df_Ts_TEPZT * len_df_Ts_TEPZTex
    fraction_Ts_TEPZToverTEPZTex = len_df_Ts_TEPZT / len_df_Ts_TEPZTex
    report_dict['fraction_Ts_TEPZToverTEPZTex'] = fraction_Ts_TEPZToverTEPZTex


    
    if (len_df_Ts_product<=0):
        report_dict['is_temperature_range_valid']  = False
        return report_dict
        # report_dict_list.append(report_dict)
        # continue
    report_dict['is_temperature_range_valid']  = True    
    
    Tmid_ofTEP     = df_Ts_TEP.temperature.mean()
    Tmid_ofZT      = df_Ts_ZT.temperature.mean()
    Tmid_ofTEPZT   = df_Ts_TEPZT.temperature.mean()
            
    Tc_ofTEP        =  df_Ts_TEP.temperature.min()
    Th_ofTEP        =  df_Ts_TEP.temperature.max()
    
    Tc_ofZT         =  df_Ts_ZT.temperature.min()
    Th_ofZT         =  df_Ts_ZT.temperature.max()
    
    Tc_ofTEPZT       = df_Ts_TEPZT.temperature.min()
    Th_ofTEPZT        =df_Ts_TEPZT.temperature.max()
    
    deltaT_ofTEP    =   Th_ofTEP    - Tc_ofTEP
    deltaT_ofZT     =   Th_ofZT     - Tc_ofZT
    deltaT_ofTEPZT  =   Th_ofTEPZT  - Tc_ofTEPZT
    
    report_dict['sample_id']  = sample_id
    report_dict['autoTc'] = autoTc
    report_dict['autoTh'] = autoTh
    report_dict['ztTc']   = ztTc
    report_dict['ztTh']   = ztTh
    
    report_dict['Tc_ofTEP']   = Tc_ofTEP
    report_dict['Th_ofTEP']   = Th_ofTEP
    report_dict['Tc_ofZT']   = Tc_ofZT
    report_dict['Th_ofZT']   = Th_ofZT
    report_dict['Tc_ofTEPZT']   = Tc_ofTEPZT
    report_dict['Th_ofTEPZT']   = Th_ofTEPZT
    report_dict['deltaT_ofTEP']   = deltaT_ofTEP
    report_dict['deltaT_ofZT']   = deltaT_ofZT
    report_dict['deltaT_ofTEPZT']   = deltaT_ofTEPZT   
    

    avg_ZT_ofRawFig    = df_Ts_ZT.ZT_author_declared.mean()
    avg_ZT_ofTEPEval   = df_Ts_TEP.ZT_tep_reevaluated.mean()        
    peak_ZT_ofRawFig    = df_Ts_ZT.ZT_author_declared.max()
    peak_ZT_ofTEPEval   = df_Ts_TEP.ZT_tep_reevaluated.max()

    report_dict['avg_ZT_ofRawFig'  ] = avg_ZT_ofRawFig
    report_dict['avg_ZT_ofTEPEval']  = avg_ZT_ofTEPEval
    report_dict['peak_ZT_ofRawFig']  = peak_ZT_ofRawFig
    report_dict['peak_ZT_ofTEPEval'] = peak_ZT_ofTEPEval

    

    d_Tmid                = Tmid_ofZT - Tmid_ofTEP
    d_avgZT               = avg_ZT_ofRawFig - avg_ZT_ofTEPEval
    d_peakZT              = peak_ZT_ofRawFig - peak_ZT_ofTEPEval
    
    report_dict['d_Tmid'] = d_Tmid
    report_dict['d_avgZT'] = d_avgZT
    report_dict['d_peakZT'] = d_peakZT
    
    
    
    dZT_TEPZT          = (df_Ts_TEPZT.ZT_author_declared) - (df_Ts_TEPZT.ZT_tep_reevaluated )   
    
    errdZT_Linf = np.max(  np.abs(dZT_TEPZT) )
    errdZT_L2  =  np.sqrt(  np.mean(  np.abs(dZT_TEPZT)**2 )  )
    errdZT_L1  =  np.mean(  np.abs(dZT_TEPZT)**1 )

    report_dict['errdZT_Linf'] = errdZT_Linf
    report_dict['errdZT_L2']   = errdZT_L2
    report_dict['errdZT_L1']   = errdZT_L1
              
    
    if (avg_ZT_ofRawFig<=0 or avg_ZT_ofRawFig == np.inf):
        report_dict['is_avg_ZT_ofRawFig_positiveFinite']  = False
        return report_dict
        # report_dict_list.append(report_dict)
        # continue
    if (avg_ZT_ofTEPEval<=0 or avg_ZT_ofTEPEval == np.inf):
        report_dict['is_avg_ZT_ofTEPEval_positiveFinite']  = False
        # report_dict_list.append(report_dict)
        return report_dict
        # continue
    if (peak_ZT_ofRawFig<=0 or peak_ZT_ofRawFig == np.inf):
        report_dict['ispeak_ZT_ofRawFig_positiveFinite']  = False
        return report_dict
        # report_dict_list.append(report_dict)
        # continue
    if (peak_ZT_ofTEPEval<=0 or peak_ZT_ofTEPEval == np.inf):
        report_dict['is_peak_ZT_ofTEPEval_positiveFinite']  = False
        return report_dict
        # report_dict_list.append(report_dict)
        # continue
    
    
    report_dict['is_avg_ZT_ofRawFig_positiveFinite']    = True
    report_dict['is_avg_ZT_ofTEPEval_positiveFinite']   = True
    report_dict['ispeak_ZT_ofRawFig_positiveFinite']    = True
    report_dict['is_peak_ZT_ofTEPEval_positiveFinite']  = True
    
    errdZT_Linf_over_avg_ZT_ofRawFig    = errdZT_Linf / avg_ZT_ofRawFig
    errdZT_Linf_over_avg_ZT_ofTEPEval   = errdZT_Linf / avg_ZT_ofTEPEval
    errdZT_Linf_over_peak_ZT_ofRawFig   = errdZT_Linf / peak_ZT_ofRawFig
    errdZT_Linf_over_peak_ZT_ofTEPEval  = errdZT_Linf / peak_ZT_ofTEPEval
    
    report_dict['errdZT_Linf_over_avg_ZT_ofRawFig']   = errdZT_Linf_over_avg_ZT_ofRawFig
    report_dict['errdZT_Linf_over_avg_ZT_ofTEPEval']  = errdZT_Linf_over_avg_ZT_ofTEPEval
    report_dict['errdZT_Linf_over_peak_ZT_ofRawFig']  = errdZT_Linf_over_peak_ZT_ofRawFig
    report_dict['errdZT_Linf_over_peak_ZT_ofTEPEval'] = errdZT_Linf_over_peak_ZT_ofTEPEval
    
    return report_dict
    # report_dict_list.append(report_dict)


def get_doi(sample_id):
    df_db_meta_sample_id = df_db_meta[ df_db_meta.sample_id == sample_id]
    doi = df_db_meta_sample_id.DOI.iloc[0]   
    doilink = "https://doi.org/{}".format(doi)
    return doi, doilink



formattedDate, yyyymmdd, HHMMSS = br.now_string()

## Read mat meta excel
file_db_meta = "_tematdb_metadata_v1.1.6-20250224.xlsx"
df_db_meta = pd.read_excel("./"+file_db_meta, sheet_name='list', )

## db info
dbname = 'tematdb'
dbversion = "v1.1.6"

## DIR setting
DIR_00_tematdb_raw_excel         =  "./data_00_tematdb_raw_excel/"
DIR_10_tematdb_converted_to_csv  =  "./data_10_tematdb_csv_converted/"
DIR_30_tematdb_extTEP_csv        =  "./data_30_tematdb_extTEP_csv/"
DIR_40_tematdb_ZT_error          =  "./data_40_tematdb_ZT_error/"


file_extended_tep = "tematdb_v1.1.6_extendedTEPset.csv"
df_extended_teps = pd.read_csv( DIR_30_tematdb_extTEP_csv + file_extended_tep )
df_extended_teps['is_Temp_in_TEPZTex'] = df_extended_teps['is_Temp_in_autoTcTh_range'] | df_extended_teps['is_Temp_in_ZT_author_declared']

sample_id_list    = df_extended_teps.sample_id.unique()
report_dict_list = []

## choose DB
## Read mat tep excel
interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
          MatProp.OPT_EXTEND_LEFT_TO:1,          # ok to 0 Kelvin
          MatProp.OPT_EXTEND_RIGHT_BY:2000}        # ok to +50 Kelvin from the raw data

    

sample_id_errLnorm_dict_list = []
for sample_id in sample_id_list:
    sample_id_errLnorm_dict = error_analysis(sample_id)
    sample_id_errLnorm_dict_list.append(sample_id_errLnorm_dict)
    
    # if (sample_id_errLnorm_dict['TF_mat_complete']):
    peak_ZT_ofRawFig  = sample_id_errLnorm_dict['peak_ZT_ofRawFig']
    peak_ZT_ofTEPEval = sample_id_errLnorm_dict['peak_ZT_ofTEPEval']
    dpeakZT = peak_ZT_ofRawFig - peak_ZT_ofTEPEval
    print("{:03d} {:5.1f} {:5.1f} {:5.1f}".format(sample_id, peak_ZT_ofRawFig, peak_ZT_ofTEPEval, dpeakZT ))
    del sample_id_errLnorm_dict

df_db_err = pd.DataFrame(sample_id_errLnorm_dict_list)

df_db_err.to_csv(DIR_40_tematdb_ZT_error  +"ZT_error_{}.csv".format(formattedDate), index=False)
df_db_err.to_csv(DIR_40_tematdb_ZT_error  +"ZT_error.csv", index=False)

