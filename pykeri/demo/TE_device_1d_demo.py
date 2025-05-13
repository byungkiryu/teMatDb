# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 11:46:02 2018

@author: 정재환

A Demo of one-dimensional thermoelectric device:
    comparison between analytic and numerical solutions
"""

from pykeri.thermoelectrics.TEProp_xls import TEProp
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.environment import Environment
from pykeri.thermoelectrics.solver1d.device import Device

######### wrtie your device spec below ########

pMat = TEProp.from_dict( {'xls_filename': "TE_device_1d_demo_p_type_mat.xlsx", 'sheetname': "pMat1"} )
nMat = TEProp.from_dict( {'xls_filename': "TE_device_1d_demo_n_type_mat.xlsx", 'sheetname': "nMat1"} )

pLeg = Leg.from_dict( {
        'type': 'p',
        'length': 2/1000,
        'area': 0.002**2,
        'materials': [pMat],
        'material_ratios': [100],   # 'material_lengths' is also possible
#        'interfaces': [nMat1]*4,
#        'interface_lengths': [0.1]*4,
        'min_length_per_grid': 2/1000/100,        # for mesh generation
        'max_num_of_grid_per_interval': 50   # for mesh generation; omissible
        } )

nLeg = Leg.from_dict( {
        'type': 'n',
        'length': 2/1000,
        'area': 0.002**2,
        'materials': [nMat],
        'material_ratios': [100],   # 'material_lengths' is also possible
        #'interfaces': [None]*4,
        #'interface_lengths': [0.0]*4,
        'min_length_per_grid': 2/1000/100,        # for mesh generation
        'max_num_of_grid_per_interval': 50   # for mesh generation; omissible
        } )

env = Environment.from_dict( {
       'Th': 800,
       'Tc': 400
       } )

device_spec = {
#        'type': 'common',
#        'length': 1,
#        'area': 0.04*0.04,
        'global_env': env,
        'legs': [pLeg, nLeg],
        'environments': [None]*2,             # can define separate environments
        'multipliers': [50, 50]  # in fact there are many p- and n-legs.
        }

dev = Device.from_dict(device_spec)


def is_similar(value1, value2, abs_tol=1e-6):
    if abs(value1 - value2) < abs_tol:
        return True
    else:
        return False

print("---- Maximum Power Mode ----")
dev.run_with_max_power()
dev.report()

# check the result
analytic_power = 32
analytic_efficiency = 0.166666667

if is_similar(dev.power, analytic_power):
    print("- ok: The maximum power is correct.")
else:
    raise ValueError("Maximum power is wrong!")
if is_similar(dev.efficiency, analytic_efficiency):
    print("- ok: The efficiency for maximum power is correct.")
else:
    raise ValueError("The efficiency for maximum power is wrong!")



print("\n---- Maximum Efficiency Mode ----")
dev.run_with_max_efficiency()
dev.report()

# check the result
analytic_power = 29.18220272
analytic_efficiency = 0.180021693
if is_similar(dev.power, analytic_power):
    print("- ok: The power for maximum efficiency is correct.")
else:
    raise ValueError("The power for maximum efficiency is wrong!")
if is_similar(dev.efficiency, analytic_efficiency):
    print("- ok: The maximum efficiency is correct.")
else:
    raise ValueError("The maximum efficiency is wrong!")
