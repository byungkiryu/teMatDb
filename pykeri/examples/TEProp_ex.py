# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 15:17:44 2017

@author: Jaywan Chung
"""

from pykeri.thermoelectrics.TEProp import TEProp


# Create material properties
raw_data  = ((100,50),(200,100),(300,30),(400,50),(500,90))
elec_resi = TEProp.def_elec_resi(raw_data)
Seebeck   = TEProp.def_Seebeck(raw_data,units=('K','uV/K'))
thrm_cond = TEProp.def_thrm_cond(raw_data)

db_filename = 'TEProp_ex.db'
id_num = 1

written = TEProp.save_to_DB(db_filename,id_num,elec_resi,Seebeck,thrm_cond,overwrite=False)

if written:
    print("DB updated.")
else:
    print("Not overwritten.")

# load a material property
tep = TEProp(db_filename,id_num)
print(tep.elec_resi, tep.Seebeck, tep.thrm_cond)

# draw the property
import matplotlib.pyplot as plt
import numpy as np

min_T,max_T = tep.elec_resi.raw_interval()
Tnew = np.linspace(min_T,max_T, num=100, endpoint=True)
plt.plot(tep.elec_resi.raw_input(), tep.elec_resi.raw_output(), 'o', Tnew, tep.elec_resi(Tnew), '-')
plt.legend(['data','linear'], loc='best')

plt.figure()
plt.plot(Tnew, tep.elec_cond(Tnew), '-')     # elec_cond is derived from elec_resi.