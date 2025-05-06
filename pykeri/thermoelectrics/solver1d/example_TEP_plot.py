# -*- coding: utf-8 -*-
"""
Created on Fri Mar 09 2018

@author: Jaywan Chung
"""

from pykeri.thermoelectrics.TEProp_xls import TEProp
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.environment import Environment
from pykeri.thermoelectrics.solver1d.device import Device


######### wrtie your device spec below ########

#pMat1 = {'xls_filename': "excelMatDB_1_pType.xlsx", 'sheetname': "pMat1"}
pMat1 = TEProp.from_dict( {'xls_filename': "excelMatDB_1_pType.xlsx", 'sheetname': "pMat1", 'mat_name': "pMat1, defined", 'color': (176/255,23/255,31/255)} )
pMat2 = TEProp.from_dict( {'xls_filename': "excelMatDB_1_pType.xlsx", 'sheetname': "pMat2"} )
pMat3 = TEProp.from_dict( {'xls_filename': "excelMatDB_1_pType.xlsx", 'sheetname': "pMat3"} )

nMat1 = TEProp.from_dict( {'xls_filename': "excelMatDB_2_nType.xlsx", 'sheetname': "nMat1", 'mat_name': "nMat1, defined", 'color': (0/255,0/255,238/255)} )
nMat2 = TEProp.from_dict( {'xls_filename': "excelMatDB_2_nType.xlsx", 'sheetname': "nMat2"} )
nMat3 = TEProp.from_dict( {'xls_filename': "excelMatDB_2_nType.xlsx", 'sheetname': "nMat3"} )

pLeg = Leg.from_dict( {
        'type': 'p',
        'length': 2/1000,
        'area': 0.002**2,
        'materials': [pMat1],
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
        'materials': [nMat1],
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
        'multipliers': [50,50]
        }

## define a device
dev = Device.from_dict(device_spec)


## computation
#print("---- Maximum Power Mode ----")
dev.run_with_max_power()
#dev.report()


#print("\n---- Maximum Efficiency Mode ----")
#dev.run_with_max_efficiency()
#dev.report()


##### TEP plot: vs. x
#fig = dev.legs[0].plot_leg_TEP(x_label='x [mm]', x_multiplier=1e3, show_grid=True, show_each_title=True, show_title=True)
#fig = dev.legs[0].plot_TEP(x_label='x [mm]', x_multiplier=1e3, show_grid=True, show_each_title=True, show_title=False)
#fig.savefig('pLeg_leg_TEP.png', dpi=300)

##### TEP plot: vs. T
fig = dev.legs[0].plot_mat_TEP(mat_pos=0, Tc=dev.Tc, Th=dev.Th, show_grid=False, show_each_title=False, show_title=False)
fig.savefig('pLeg_mat_TEP.png', dpi=300)