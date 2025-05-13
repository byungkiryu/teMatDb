# -*- coding: utf-8 -*-
"""
Created on Wed Mar 07 2018

@author: Jaywan Chung

An example to show how to construct a spec table.
A spec table describes several performance values for given Th and Tc and given mode (max power or max efficiency).
"""

from pykeri.thermoelectrics.TEProp_xls import TEProp
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.environment import Environment
#from pykeri.thermoelectrics.solver1d.device import Device


######### wrtie your device spec below ########

#pMat1 = {'xls_filename': "excelMatDB_1_pType.xlsx", 'sheetname': "pMat1"}  # possible, but slow
pMat = TEProp.from_dict( {'xls_filename': "excelMatDB_1_pType.xlsx", 'sheetname': "pMat1"} )
nMat = TEProp.from_dict( {'xls_filename': "excelMatDB_2_nType.xlsx", 'sheetname': "nMat1"} )

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
#        'global_env': env,
        'legs': [pLeg, nLeg],
#        'environments': [None]*2,             # can define separate environments
        'multipliers': [50,50]
        }


######### how to construct spec tables ########

from pykeri.thermoelectrics.solver1d.device_util import spec_tables
Th_list = [400,500,600]
Tc_list = [300,400,500]

print("---- Maximum power mode ----")
tables = spec_tables(device_spec, Th_list, Tc_list, mode='max power')
print("\nI=\n", tables['I'])
print("\nQhA=\n", tables['QhA'])
print("\nVgen=\n", tables['Vgen'])
print("\nR_TE=\n", tables['R_TE'])
print("\nK_TE=\n", tables['K_TE'])
print("\nefficiency=\n", tables['efficiency'])
print("\npower=\n", tables['power'])
#tables['power'].to_csv('spec_table_max_power.csv')  # can save each table to a file


print("\n---- Maximum efficiency mode ----")
tables = spec_tables(device_spec, Th_list, Tc_list, mode='max efficiency')
print("\nI=\n", tables['I'])
print("\nQhA=\n", tables['QhA'])
print("\nVgen=\n", tables['Vgen'])
print("\nR_TE=\n", tables['R_TE'])
print("\nK_TE=\n", tables['K_TE'])
print("\nefficiency=\n", tables['efficiency'])
print("\npower=\n", tables['power'])
#tables['efficiency'].to_csv('spec_table_max_efficiency.csv')