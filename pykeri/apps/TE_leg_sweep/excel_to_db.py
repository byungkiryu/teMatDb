# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 09:53:34 2017

@author: Jaywan Chung
"""

#excel_filename = "MAT-TEP-DATA_v5_00001-00050_proved.xlsx"
#excel_filename = "MAT-TEP-DATA_v5_00051-00100_proved.xlsx"
#excel_filename = "MAT-TEP-DATA_v5_00101-00150_proved.xlsx"
#excel_filename = "MAT-TEP-DATA_v5_00151-00200_proved.xlsx"
#excel_filename = "MAT-TEP-DATA_v5_00201-00250_proved.xlsx"
#excel_filename = "MAT-TEP-DATA_v5_00251-00300_proved.xlsx"
excel_filename = "MAT-TEP-DATA_v5_00301-00350.xlsx"

db_filename = "tep.db"


#------------------------- DO NOT MODIFY BELOW -------------------------
from pykeri.scidata.read import read_excel_scidata, sci_table
from pykeri.scidata.matdb import MatDB
from pykeri.thermoelectrics.TEProp import TEProp

if 'sheet_names' in locals():
    del sheet_names

if not 'sheet_names' in locals():
    # read once
    print("reading", excel_filename, "...")
    tables_in_sheets, sheet_names = read_excel_scidata(excel_filename,ignore_settings=True)

count = 0
db = MatDB(db_filename)

for idx,sheet_name in enumerate(sheet_names):
    id_num = int( sheet_name[1:] )

    df = tables_in_sheets[idx][3]
    table = sci_table(df.iloc[:,range(0,6)], col_irow=0, unit_irow=1)
    # dataframes
    elec_cond_df = table.iloc[:,(0,1)].dropna()
    Seebeck_df   = table.iloc[:,(2,3)].dropna()
    thrm_cond_df = table.iloc[:,(4,5)].dropna()
    # check the integrity of the data
    if len(elec_cond_df)==0:
        print("id=", id_num, "skipped; electrial conductivity does not exists.")
        continue
    if len(Seebeck_df)==0:
        print("id=", id_num, "skipped; Seebeck coefficient does not exists.")
        continue
    if len(thrm_cond_df)==0:
        print("id=", id_num, "skipped; thermal conductivity does not exists.")
        continue        
    # convert from elec_cond to elec_resi
    elec_resi_df  = elec_cond_df.copy()
    elec_resi_df.columns = ('T [K]','resi [Ohm m]')
    elec_resi_df.iloc[:,1] = 1/elec_resi_df.iloc[:,1]
    # raw_data ready
    elec_resi_raw = elec_resi_df.values
    Seebeck_raw   = Seebeck_df.values
    thrm_cond_raw = thrm_cond_df.values
    # convert to MatProp
    elec_resi = TEProp.def_elec_resi(elec_resi_raw)
    Seebeck   = TEProp.def_Seebeck(Seebeck_raw)
    thrm_cond = TEProp.def_thrm_cond(thrm_cond_raw)
    # record the data
    if TEProp.save_to_DB(db_filename,id_num,elec_resi,Seebeck,thrm_cond):
        print("id=", id_num, "saved.")
        count += 1
    else:
        print("id=", id_num, "skipped.")
        pass
        
print("Total", count, "items recorded.")