# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 15:32:28 2022

@author: byungkiryu

This code read excel files which contatin raw-digitized things
 into a single merged csv file.

"""

import os
import pandas as pd
import time as time
time00 = time.time()

from pykeri.thermoelectrics.TEProp_xls import TEProp
from pykeri.byungkiryu import byungkiryu_util as br

import datetime
formattedDate, yyyymmdd, HHMMSS = br.now_string()


## db info
dbname = 'tematdb'
dbversion = "v1.1.6"

## DIR setting
DIR_00_tematdb_raw_excel         =  "./data_00_tematdb_raw_excel/"
DIR_10_tematdb_converted_to_csv  =  "./data_10_tematdb_csv_converted/"
DIR_30_tematdb_extTEP_csv        =  "./data_30_tematdb_extTEP_csv/"
DIR_40_tematdb_ZT_error          =  "./data_40_tematdb_ZT_error/"



fileseq = 1
idx_ini = 1  + (fileseq-1)*50
idx_fin = 50 + (fileseq-1)*50


files = os.listdir(DIR_00_tematdb_raw_excel)

sample_id_ini, sample_id_fin = 1, 4
sample_id_ini, sample_id_fin = 1, 450

df_raw_tep_list = []
sample_id_list = list(range(sample_id_ini,sample_id_fin+1))
# sample_id_list = sample_id_list[0:4]
for sample_id in sample_id_list:
    # idx = sample_id
    fileindex = int((sample_id-1)/50)
    filename = files[fileindex]
    sheetname = "#{:05d}".format(sample_id)
    

    try:
        mat = TEProp.from_dict({'xls_filename': DIR_00_tematdb_raw_excel +filename,
                                'sheetname': sheetname, 'color': (sample_id/255, 0/255, 0/255)} )
        autoTc = mat.min_raw_T
        autoTh = mat.max_raw_T
    except:
        print(filename, sample_id, 'data set is incompelete or empty')
        continue
    
    df_tep_each = pd.DataFrame()
    df_alpha_each = pd.DataFrame(mat.Seebeck.raw_data(), columns=['Temperature','tepvalue'] )
    df_alpha_each['tepname'] = 'alpha'
    df_alpha_each['unit'] = '[V/K]'
    
    df_rho_each = pd.DataFrame(mat.elec_resi.raw_data(), columns=['Temperature','tepvalue'] )
    df_rho_each['tepname'] = 'rho'
    df_rho_each['unit'] = '[Ohm-m]'
    
    df_kappa_each = pd.DataFrame(mat.thrm_cond.raw_data(), columns=['Temperature','tepvalue'] )
    df_kappa_each['tepname'] = 'kappa'
    df_kappa_each['unit'] = '[W/m/K]'
    
    df_ZT_each = pd.DataFrame(mat.ZT.raw_data(), columns=['Temperature','tepvalue'] )
    df_ZT_each['tepname'] = 'ZT'
    df_ZT_each['unit'] = '[1]'
    
    df_tep_each = pd.concat([df_alpha_each, df_rho_each, df_kappa_each, df_ZT_each])
    df_tep_each['sample_id'] = sample_id
    df_tep_each['autoTc'] = autoTc
    df_tep_each['autoTh'] = autoTh
    
    df_raw_tep_list.append( df_tep_each.copy() )
    
    
    len_alpha = len(df_alpha_each)
    len_rho   = len(df_rho_each)
    len_kappa = len(df_kappa_each)
    len_ZT    = len(df_ZT_each)
    len_tep   = len(df_tep_each)
    
    print(filename, sheetname, " data lenghs of alpha/rho/kappa/ZT/all=",
          len_alpha, len_rho, len_kappa, len_ZT, len_tep)




## Read mat meta excel
file_db_meta = "_tematdb_metadata_v1.1.6-20250224.xlsx"
df_db_meta = pd.read_excel("./"+file_db_meta, sheet_name='list', )


dbversionshort  = 'tematdb_{:s}_completeTEPset'.format(dbversion)
dbversionprefix = 'tematdb_{:s}_completeTEPset_convertedOn_{}_'.format(dbversion,formattedDate)

df_tep_raw = pd.concat( df_raw_tep_list, copy=True,ignore_index=True)
datetimeupdate =  datetime.datetime.now()

# df_tep_all = pd.DataFrame()
df_tep_all = df_tep_raw[['sample_id','tepname','Temperature','tepvalue','unit','autoTc','autoTh']].copy()
sample_id_min = df_tep_all.sample_id.min()
sample_id_max = df_tep_all.sample_id.max()

dbversiontype ="range"
dbversionlabel = dbversionprefix+'_{:s}_{:d}_to_{:d}'.format(dbversiontype,sample_id_min, sample_id_max)

# df_tep_all['id_tematdb'] = df_tep_all.sample_id.copy()
df_tep_all['dbname']  = dbname
df_tep_all['dbversion'] = dbversion
df_tep_all['dbversionlabel'] = dbversionlabel
df_tep_all['update']  = datetimeupdate
df_tep_all['pykeri_compatible'] = True

df_tep_all.to_csv(DIR_10_tematdb_converted_to_csv+ dbversionlabel+'.csv',index=False )
df_tep_all.to_csv(DIR_10_tematdb_converted_to_csv+ dbversionshort+'.csv',index=False )




output_report_filename  =  "readme__completeTEPset.txt"
output_report_filename1 = f"readme__completeTEPset___{formattedDate}.txt"
output_report_files = [output_report_filename,output_report_filename1]


time_f = time.time()
formattedDate_fin, yyyymmdd_fin, HHMMSS_fin = br.now_string()
for file in output_report_files:
    f = open(DIR_10_tematdb_converted_to_csv + file, "w", encoding="utf-8")
    
    # f.write(tepprefix)
    f.write("Date: {}\n".format(datetime.datetime.now()))
    f.write("  dbname    :  {}\n".format(dbname) )
    f.write("  dbversion :  {}\n".format(dbversion) )
    f.write("  make a single tep set for complete TEP curve digital data\n")
    # f.write("    dT_unit for digitization: = {} K\n".format(dT_unit))
    # f.write("    autoTcTh_buffer_dT:       = {} K\n".format(autoTcTh_buffer_dT))
    
    f.write("\n")
    f.write("  start: {} \n".format(formattedDate))  
    f.write("  ended: {} \n".format(formattedDate_fin))    
    
    f.write("\n")
    f.write("    number of complete(valid) samples = {} \n".format( len(df_tep_all.sample_id.unique().tolist()) ))
    # f.write("___{} \n".format(text_data))    
    f.write("\n")
    f.write("Eplased time = {:.1f}.sec".format(time_f-time00) )   
    
    f.close()
    
# del df_tep_all, df_tep_raw



