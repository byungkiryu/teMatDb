# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 12:38:56 2018

@author: Jaywan Chung
"""

import matplotlib.pyplot as plt

from pykeri.thermoelectrics.TEProp_xls import TEProp
from pykeri.thermoelectrics.solver1d.environment import Environment
from pykeri.thermoelectrics.solver1d.device_util import rank_mats_as_leg
from pykeri.thermoelectrics.solver1d.device_util import rank_mats_as_device


######### wrtie your device spec below ########

pMat1 = TEProp.from_dict( {'xls_filename': "excelMatDB_1_pType.xlsx", 'sheetname': "pMat1", 
                           'mat_name': "pMat1", 'color': (176/255, 23/255, 31/255)} )
pMat2 = TEProp.from_dict( {'xls_filename': "excelMatDB_1_pType.xlsx", 'sheetname': "pMat2", 
                           'mat_name': "pMat2", 'color': (255/255, 62/255,150/255)} )
pMat3 = TEProp.from_dict( {'xls_filename': "excelMatDB_1_pType.xlsx", 'sheetname': "pMat3", 
                           'mat_name': "pMat2", 'color': (218/255,112/255,214/255)} )

nMat1 = TEProp.from_dict( {'xls_filename': "excelMatDB_2_nType.xlsx", 'sheetname': "nMat1", 
                           'mat_name': "nMat1, defined", 'color': (0/255,0/255,238/255)} )
nMat2 = TEProp.from_dict( {'xls_filename': "excelMatDB_2_nType.xlsx", 'sheetname': "nMat2",
                           'mat_name': "nMat2, defined", 'color': (0/255,191/255,255/255)} )  # deepskyblue 1
nMat3 = TEProp.from_dict( {'xls_filename': "excelMatDB_2_nType.xlsx", 'sheetname': "nMat3",
                           'mat_name': "nMat3, defined", 'color': (84/255,255/255,159/255)} )  # seagreen 1

env = Environment.from_dict( {
       'Th': 800,
       'Tc': 400
       } )


#### rank legs

leg_combination_spec = {
    'pn_type': 'n',
    'length': 2/1000,
    'area': 0.002**2,
    'materials': [nMat1, nMat2, nMat3],
#    'interface_mat': None,
#    'interface_length': 0,
#    'multiplier': 1,
    'env': env,
    'num_ranks': 5,
    'max_num_stages': 2,
    'resolution': 3,
    'mode': 'max power',
    'show_alert': False
}


devs1, scores = rank_mats_as_leg(**leg_combination_spec)
#for idx, dev in enumerate(devs):
#    fig = dev.legs[0].plot(length_unit='[mm]', length_multiplier=1e3)
    #plt.title('power = %.2f [W]' % scores[idx])
#    fig.savefig('leg_power_rank_%2d.png' % (idx+1))
#    plt.close()



#### rank devices

device_combination_spec = {
    'p_materials': [pMat1, pMat2, pMat3],
    'n_materials': [nMat1, nMat2, nMat3],
#    'p_interface_mat': None,
#    'p_interface_length': 0,
#    'n_interface_mat': None,
#    'n_interface_length': 0,
    'length': 2/1000,
    'p_area': 0.002**2,
    'n_area': 0.002**2,
    'p_multiplier': 50,
    'n_multiplier': 50,
    'global_env': env,
    'num_ranks': 5,
    'max_num_stages': 3,
    'resolution': 3,
    'mode': 'max power',
    'show_alert': False
}

devs, scores = rank_mats_as_device(**device_combination_spec)
for idx, dev in enumerate(devs):
    fig = dev.plot(length_unit='[mm]', length_multiplier=1e3)
#    plt.title('power = %.2f [W]' % scores[idx])
    #fig.savefig('device_power_rank_%2d.png' % (idx+1))
    #plt.close()