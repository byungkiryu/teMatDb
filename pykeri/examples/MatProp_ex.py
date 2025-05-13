# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 08:40:53 2017

@author: Jaywan Chung
"""

import numpy as np
from pykeri.scidata.matprop import MatProp

names = ('temperature','Seebeck')
units = ('K','uV/K')
raw_data = ((100,50),(200,100),(300,30),(400,50),(500,90))
interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
              MatProp.OPT_EXTEND_LEFT_TO:0,          # ok to 0 Kelvin
              MatProp.OPT_EXTEND_RIGHT_BY:50}        # ok to +50 Kelvin from the raw data

#Seebeck = MatProp(names,units,raw_data)
Seebeck = MatProp(names,units,raw_data,interp_opt=interp_opt)
print(Seebeck)

import matplotlib.pyplot as plt

Tnew = np.linspace(0,550, num=100, endpoint=True)
plt.plot(Seebeck.raw_input(), Seebeck.raw_output(), 'o', Tnew, Seebeck(Tnew), '-')
plt.legend(['data','linear'], loc='best')

print(Seebeck.input_units(), Seebeck.unit())
print(Seebeck.raw_interval())   # min and max values of the input

print(Seebeck.to_units(('K','V/K')))    # unit conversion
print(Seebeck.to_units(('degC','V/K')))
print(Seebeck.to_units(('degF','uV/K')))