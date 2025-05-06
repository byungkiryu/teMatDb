# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 15:17:44 2017

@author: Jaywan Chung
"""

from pykeri.thermoelectrics.TEProp import TEProp


# Create material properties
raw_data  = ((100,50),(200,100),(300,30),(400,50),(500,90))
elec_resi_raw_data = raw_data
Seebeck_raw_data = raw_data
thrm_cond_raw_data = raw_data

#elec_resi = TEProp.def_elec_resi(raw_data)
#Seebeck   = TEProp.def_Seebeck(raw_data,units=('K','uV/K'))
#thrm_cond = TEProp.def_thrm_cond(raw_data)

print("defining a thermoelectric property...")
tep = TEProp.from_raw_data(elec_resi_raw_data, Seebeck_raw_data, thrm_cond_raw_data, name="interface")
print("thermoelectric property defined.")

# draw the property
import matplotlib.pyplot as plt
import numpy as np

min_T,max_T = tep.elec_resi.raw_interval()
Tnew = np.linspace(min_T,max_T, num=100, endpoint=True)
plt.plot(tep.elec_resi.raw_input(), tep.elec_resi.raw_output(), 'o', Tnew, tep.elec_resi(Tnew), '-')
plt.legend(['data','linear'], loc='best')
plt.title("electrical resistivity")

plt.figure()
plt.plot(Tnew, tep.elec_cond(Tnew), '-')     # elec_cond is derived from elec_resi.
plt.title("electrical conductivity")