# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 15:32:28 2022

@author: byungkiryu

This code generates a set of extended TEPs from raw digitized TEPs
Here, I used the teMatDb v1.0.


"""

import os
import math
import numpy as np
import pandas as pd
import time as time
time00 = time.time()

import datetime

from pykeri.scidata.matprop import MatProp
from pykeri.thermoelectrics.TEProp_xls import TEProp as TEProp_xls
# from pykeri.thermoelectrics.solver1d.leg import Leg
# from pykeri.thermoelectrics.solver1d.environment import Environment
# from pykeri.thermoelectrics.solver1d.device import Device

from pykeri.byungkiryu import byungkiryu_util as br

# formattedDate, yyyymmdd, HHMMSS = br.now_string()

# version = "v1.1.6"
# DIR_00_tematdb_raw_excel         =  "./data_00_tematdb_raw_excel/"
# DIR_10_tematdb_converted_to_csv  =  "./data_10_tematdb_csv_converted/"
# DIR_30_tematdb_extTEP_csv        =  "./data_30_tematdb_extTEP_csv/"


def get_df_from_tematdb(teMatDb_file):
    df_raw_tep = pd.read_csv(teMatDb_file)    
    df_raw_alpha = df_raw_tep[ df_raw_tep.tepname == 'alpha']
    df_raw_rho   = df_raw_tep[ df_raw_tep.tepname == 'rho']
    df_raw_kappa = df_raw_tep[ df_raw_tep.tepname == 'kappa']
    df_raw_ZT    = df_raw_tep[ df_raw_tep.tepname == 'ZT']    
    return df_raw_tep, df_raw_alpha, df_raw_rho, df_raw_kappa, df_raw_ZT


def tep_generator_from_excel_files(sample_id, interp_opt):    
    files = os.listdir(DIR_00_tematdb_raw_excel)
    
    fileindex = int((sample_id-1)/50)
    filename = files[fileindex]
    sheetname = "#{:05d}".format(sample_id)        
    
    try:
        mat = TEProp_xls.from_dict({'xls_filename': DIR_00_tematdb_raw_excel+filename,
                                'sheetname': sheetname, 'color': (sample_id/255, 0/255, 0/255)} ) 
        TF_mat_complete = True     
        mat.set_interp_opt(interp_opt)
        print(sample_id)
        return TF_mat_complete, mat
    except:
        print(filename, sample_id, 'data set is incompelete or empty')
        TF_mat_complete = False
        mat = False        
        return TF_mat_complete, mat


autoTcTh_buffer_dT = 15
dT_unit = 2
def get_df_extended_tep_sample(sample_id):
    interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
                  MatProp.OPT_EXTEND_LEFT_TO:1,          # ok to 0 Kelvin
                  MatProp.OPT_EXTEND_RIGHT_BY:2000}        # ok to +50 Kelvin from the raw data

    TF_mat_complete, mat = tep_generator_from_excel_files(sample_id, interp_opt)
        
    try:
        df = pd.DataFrame()
        
        # autoTcTh_buffer_dT = 15
        # dT_unit = 2
        
        autoTc = mat.min_raw_T
        autoTh = mat.max_raw_T
        ztTc, ztTh = mat.ZT.raw_interval()
        
        Tmin = min( autoTc, ztTc ) - autoTcTh_buffer_dT
        Tmax = max( autoTh, ztTh ) + autoTcTh_buffer_dT
        
        Tmin_floor = math.floor(Tmin/dT_unit)*dT_unit
        Tmax_ceil  = math.ceil( Tmax/dT_unit)*dT_unit ## 정수
        dT_extended = np.arange(Tmin_floor, Tmax_ceil+1, dT_unit )
        
        
        
        
        alpha = mat.Seebeck(dT_extended)
        rho   = mat.elec_resi(dT_extended)
        kappa = mat.thrm_cond(dT_extended)
        raw_ZT = mat.ZT(dT_extended)
        
        sigma = 1/rho
        PF    = alpha*alpha*sigma
        Z     = PF/kappa
        ZT    = Z*dT_extended
        RK    = rho*kappa
        # Lorenz= RK/dT_extended

        
        df['sample_id'] = [sample_id]*len(dT_extended)
        df['Temperature'] = dT_extended.copy()
        df['alpha'] = alpha
        df['rho']   = rho
        df['kappa'] = kappa
        df['RK'] = RK
        
        df['sigma'] = sigma
        df['PF']    = PF
        # df['Z']     = Z
        # df['ZT_tep_reevaluated']    = ZT
        df['ZT_author_declared'] = raw_ZT
        df['ZT_tep_reevaluated']    = ZT
        # df['RK']    = RK
        # df['Lorenz']= Lorenz
        
        # autoTcTh_buffer_dT = 0
        df['autoTc'] = autoTc
        df['autoTh'] = autoTh

        df['ztTc'] = ztTc
        df['ztTh'] = ztTh
        
        df['autoTcTh_buffer_dT'] = autoTcTh_buffer_dT
        # df['is_Temp_in_autoTcTh_range'] = (df.Temperature >= autoTc-autoTcTh_buffer_dT) & (df.Temperature <= autoTh+autoTcTh_buffer_dT)
        df['is_Temp_in_autoTcTh_range'] = (df.Temperature >= autoTc) & (df.Temperature <= autoTh)
        df['is_Temp_in_ZT_author_declared']  = (df.Temperature >= ztTc) & (df.Temperature <= ztTh)
        df['is_Temp_in_TEPZT'] =  (df.is_Temp_in_autoTcTh_range) & (df.is_Temp_in_ZT_author_declared)
        
        
        df_extended_tep_sample = df.copy()
        
        return df_extended_tep_sample
    except:
        df_extended_tep_sample = pd.DataFrame()
        return df_extended_tep_sample


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


teMatDb_csv_file = DIR_10_tematdb_converted_to_csv + "tematdb_{}_completeTEPset.csv".format(dbversion)
df_raw_tep, df_raw_alpha, df_raw_rho, df_raw_kappa, df_raw_ZT = get_df_from_tematdb(teMatDb_csv_file)


sample_id_ini, sample_id_fin = 1, 5
sample_id_ini, sample_id_fin = 1, 450


df_extended_tep_sample_list = []
for sample_id in range(sample_id_ini,sample_id_fin+1):
    df_extended_tep_sample = get_df_extended_tep_sample(sample_id)  
    df_extended_tep_sample_list.append(df_extended_tep_sample.copy())


df_extended_tep = pd.concat( df_extended_tep_sample_list, ignore_index= True)



# dbname = 'tematdb'
dbversionshort  = 'tematdb_{:s}_extendedTEPset'.format(dbversion)
dbversionprefix = 'tematdb_{:s}_extendedTEPset_convertedOn_{}_'.format(dbversion,formattedDate)

datetimeupdate =  datetime.datetime.now()


sample_id_min = df_extended_tep.sample_id.min()
sample_id_max = df_extended_tep.sample_id.max()

dbversiontype ="range"
dbversionlabel = dbversionprefix+'_{:s}_{:d}_to_{:d}'.format(dbversiontype,sample_id_min, sample_id_max)


df_extended_tep.to_csv( DIR_30_tematdb_extTEP_csv +dbversionlabel+'.csv',index=False )
df_extended_tep.to_csv( DIR_30_tematdb_extTEP_csv +dbversionshort+'.csv',index=False )



samples_list_converted_extTEP = df_extended_tep.sample_id.unique().tolist()
      
# 파일로 저장 (기본 인코딩 UTF-8)
output_report_filename  =  "readme__extendedTEP.txt"
output_report_filename1 = f"readme__extendedTEP__{formattedDate}.txt"
output_report_files = [output_report_filename,output_report_filename1]

# text_data = reported

time_f = time.time()
formattedDate_fin, yyyymmdd_fin, HHMMSS_fin = br.now_string()
for file in output_report_files:
    f = open( DIR_30_tematdb_extTEP_csv +file, "w", encoding="utf-8")
    
    # f.write(tepprefix)
    f.write("Date: {}\n".format(datetime.datetime.now()))
    f.write("  dbname    :  {}\n".format(dbname) )
    f.write("  dbversion :  {}\n".format(dbversion) )
    f.write("  make a extended tep set for ZT filter analysis\n")
    f.write("    dT_unit for digitization: = {} K\n".format(dT_unit))
    f.write("    autoTcTh_buffer_dT:       = {} K\n".format(autoTcTh_buffer_dT))
    
    f.write("\n")
    f.write("  start: {} \n".format(formattedDate))  
    f.write("  ended: {} \n".format(formattedDate_fin))    
    
    f.write("\n")
    f.write("    number of total converted samples = {} \n".format( len(samples_list_converted_extTEP) ))
    # f.write("___{} \n".format(text_data))    
    f.write("\n")
    f.write("Eplased time = {:.1f}.sec".format(time_f-time00) )   
    
    f.close()
    








