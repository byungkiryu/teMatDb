# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""


import os
import numpy as np
import pandas as pd
import datetime

from pykeri.scidata.matprop import MatProp
from pykeri.thermoelectrics.TEProp_xls import TEProp as TEProp_xls
from pykeri.thermoelectrics.TEProp_df import TEProp as TEProp_df
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.environment import Environment
from pykeri.thermoelectrics.solver1d.device import Device
from pykeri.thermoelectrics.solver1d.formula_aux import CHEVYSHEV_NODE

from pykeri.util.interp_utils import BarycentricLagrangeChebyshevNodes
from pykeri.util.interp_utils import find_maximum

from library.tematdb_util import draw_mat_teps, tep_generator_from_excel_files

from pykeri.byungkiryu import byungkiryu_util as br
from matplotlib import pyplot as plt

formattedDate, yyyymmdd, HHMMSS = br.now_string()

import math
debug_talking = True



def do_bisection_method(dev, I0, I1, tol_gamma):    
    if ( math.isnan(I0) ):
        return I0
    if (I0 > I1):
        I0, I1 = I1, I0
    dev.run_with_given_I(I0)
    V0 = dev.Vgen - dev.I * dev.R_TE    
    dev.run_with_given_I(I1)
    V1 = dev.Vgen - dev.I * dev.R_TE    
    N_idx = 20
    SCALE_I = 1.15    
    for idx in range(N_idx):
        if (V0>0):
            pass
        else:
            I0 = I0/SCALE_I
        dev.run_with_given_I(I0)
        V0 = dev.Vgen - dev.I * dev.R_TE        
        if (V1<0):
            pass
        else:
            I1 = I1 * SCALE_I
        dev.run_with_given_I(I1)
        V1 = dev.Vgen - dev.I * dev.R_TE
        if (debug_talking==True):
            print("check I0,I1 for starting", idx, I0,I1, V0,V1)        
        if (V0>0 and V1<0):
            break
    
    for idx in range(N_idx):
        Imid = (I0+I1)/2
        dev.run_with_given_I(Imid)
        Vmid = dev.Vgen - dev.I * dev.R_TE
        if (Vmid > 0 ):
            I0 = Imid
        else:
            I1 = Imid
        IrelErr = np.abs( (I1-I0 )/I0 )
        if ( IrelErr < tol_gamma ):
            break
        else:
            pass
        if (debug_talking==True):
            print(idx, Imid)
    return I1


def search_current_ref(dev):
    # N_idx = 10
    # SCALE = 0.95
    tol_gamma= 1e-2
    dev.run_with_given_gamma(0)
    if ( np.abs(dev.gamma) < tol_gamma ):
        if (debug_talking==True):
            print("______ Gamma is     conveged to be  {:.6g}. And current_ref is  {:.6f}.".format(dev.gamma,dev.I))    
        current_ref = dev.Vgen / dev.R_TE
    else: 
        if (debug_talking==True):
            print("______ Gamma is not converged to be {:.6g}. And current_ref is {}.".format(dev.gamma,dev.I))   
        I0 = dev.Vgen / dev.R_TE
        # V0 = dev.Vgen - dev.I * dev.R_TE
        
        dev.run_with_given_I(I0)
        I1 = dev.Vgen / dev.R_TE
        # V1 = dev.Vgen - dev.I * dev.R_TE

        # Ierr = np.abs(I0-I1)/I1
        current_ref = do_bisection_method(dev, I0, I1, tol_gamma)
        if (debug_talking==True):
            print("______ doing bisection method for gamma and current_ref search")
            print("______ Gamma is     converged to be {:.6g}. And current_ref is {}.".format(dev.gamma,dev.I))    
    return current_ref




# if (1):    
def set_singleleg_device(mat, leg_length,leg_area,N_leg,Th,Tc):
    
        
    # df_db_csv_sampleid = df_db_csv[ df_db_csv.sampleid == sampleid]    
    # df_alpha = df_db_csv_sampleid[ df_db_csv_sampleid.tepname == 'alpha']
    # df_rho   = df_db_csv_sampleid[ df_db_csv_sampleid.tepname == 'rho'  ]
    # df_kappa = df_db_csv_sampleid[ df_db_csv_sampleid.tepname == 'kappa']
    # df_ZT    = df_db_csv_sampleid[ df_db_csv_sampleid.tepname == 'ZT'   ]    
    
    # interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
    #           MatProp.OPT_EXTEND_LEFT_TO:1,          # ok to 0 Kelvin
    #           MatProp.OPT_EXTEND_RIGHT_BY:2000}        # ok to +50 Kelvin from the raw data   
    # mat = TEProp_df.load_from_df(df_alpha, df_rho, df_kappa, df_ZT, mat_name='test')
    # mat.set_interp_opt(interp_opt)
    
    # TF_mat_complete, mat = tep_generator_from_excel_files(sampleid, interp_opt)
    # TF_mat_complete, mat = tep_generator_from_excel_files(sampleid, interp_opt)
    

    singleLeg_dict =  {
            'type': 'p',
            'length': leg_length,    
            'area':   leg_area,
            'materials': [mat],
            'material_ratios': [100],   # 'material_lengths' is also possible
            # 'interfaces': [IF]*2,
            # 'interface_lengths': [if_length]*2,
            'min_length_per_grid': 2/1000/1000,        # for mesh generation
            'max_num_of_grid_per_interval': 100   # for mesh generation; omissible
            }
    device_spec = {
    #        'type': 'common',
    #        'length': 1,
    #        'area': 0.04*0.04,
            # 'global_env': env,
    #        'legs': [pLeg, nLeg],
            # 'legs': [singleLeg],
            'environments': [None]*2,             # can define separate environments
            'multipliers': [N_leg]
            }
    
    env = Environment.from_dict( {
        'Th': Th,  
        'Tc': Tc
        } )     
    device_spec['global_env'] = env 
    singleLeg = Leg.from_dict( singleLeg_dict )  
    
    device_spec['legs'] = [singleLeg]
    device_spec['global_env'] = env 
    dev = Device.from_dict(device_spec)
    
    return dev
    

def run_pykeri(dev, sampleid, leg_length, leg_area, N_leg, Th, Tc):
    
    # dev = set_singleleg_device(df_db_csv,sampleid,leg_length,leg_area,N_leg,Th,Tc)
    
    try:
        current_ref = search_current_ref(dev)              
        # checker_dict['pass_get_Imax'] = True
    except:      
        # checker_dict['pass_get_Imax'] = False   
        dev.run_with_given_I(0)
        current_ref = dev.Vgen / dev.R_TE * 1.2
        # continue

    
    NUM_RELATIVE_CURRENTS = 11
    MIN_RELATIVE_CURRENT, MAX_RELATIVE_CURRENT = 0.0, 1.0
    RELATIVE_CURRENT_ARRAY = CHEVYSHEV_NODE(MIN_RELATIVE_CURRENT, MAX_RELATIVE_CURRENT, NUM_RELATIVE_CURRENTS)

    # Temperature_pair = [dev.Tc,dev.Th]

    mat_dev_data_dictionary_list_powMax = []
    mat_dev_data_dictionary_list_etaMax = []
    
    pow_array = np.zeros(len(RELATIVE_CURRENT_ARRAY)) 
    eff_array = np.zeros(len(RELATIVE_CURRENT_ARRAY)) 

    mat_dev_data_dictionary_list =[]    
    mat_data_dictionary = {}
    mat_data_dictionary["sampleid"] = sampleid
    # mat_data_dictionary["autoTc"] = autoTc
    # mat_data_dictionary["autoTh"] = autoTh
    # mat_data_dictionary["IF_mode"] = IF_mode
    # mat_data_dictionary["rho_C"] = rho_C
    # mat_data_dictionary["kappa_C"] = kappa_C
    
    # mat_data_dictionary["if_length"] = if_length
    # mat_data_dictionary["leg_teMat_length"] = leg_length - 2*if_length
    mat_data_dictionary["leg_length"] = leg_length 
    mat_data_dictionary["leg_area"] = leg_area
    mat_data_dictionary["N_leg"] = N_leg

    for current_idx, current_relative in enumerate(RELATIVE_CURRENT_ARRAY):
        current = current_relative * current_ref
        now = datetime.datetime.now()       
        mat_data_dictionary["current_idx"] = current_idx
        mat_data_dictionary["current_mode"] = "current"   
        dev_data_dictionary = {}
        try:
            dev_run_succeed = dev.run_with_given_I(current)                    
            dev_data_dictionary['datetime_now'] = now
            dev_run_not_crashed = True
            dev_data_dictionary['dev_run_not_crashed'] = dev_run_not_crashed     
            
        except:
            dev_data_dictionary['datetime_now'] = now
            dev_run_not_crashed = False
            dev_data_dictionary['dev_run_crashed'] = dev_run_not_crashed
            continue
        
        # print('sampleid={}, current_idx={}'.format(sampleid, current_idx))
        dev_data_dictionary = dev.get_report_dict_full()
        dev_data_dictionary['dev_run_succeed'] = dev_run_succeed
        
        mat_dev_data_dictionary = {**mat_data_dictionary,**dev_data_dictionary}
        mat_dev_data_dictionary_list.append(mat_dev_data_dictionary)

        
        pow_array[current_idx] = dev.power
        eff_array[current_idx] = dev.efficiency
    
    # do_optimization = True
    if (dev_run_not_crashed == True):                         
        power_func = BarycentricLagrangeChebyshevNodes(RELATIVE_CURRENT_ARRAY, pow_array)
        efficiency_func = BarycentricLagrangeChebyshevNodes(RELATIVE_CURRENT_ARRAY, eff_array)
        
        max_power, relative_I_power_max, success_power_max = find_maximum(power_func, 0.5)
        max_efficiency, relative_I_efficiency_max, success_efficiency_max = find_maximum(efficiency_func, 0.5)


        mat_data_dictionary["current_mode"] = "powMax"   
        mat_data_dictionary["current_idx"] = -1
        dev.run_with_given_I(relative_I_power_max*current_ref)

        # Zgeneral, tau, beta, taulin, betalin = one_shot_linear(dev,mat,Temperature_pair)
        # gammaEtaMaxFormulalin, etaMaxFormulalin =  EtaMaxFormula(Th,Tc,Zgeneral, taulin, betalin)
        # mat_data_dictionary["taulin"] = taulin
        # mat_data_dictionary["betalin"] = betalin
        # mat_data_dictionary["etaMaxFormulalin"] = etaMaxFormulalin                 
        dev_data_dictionary = dev.get_report_dict_full()
        mat_dev_data_dictionary = {**mat_data_dictionary,**dev_data_dictionary}
        mat_dev_data_dictionary_list_powMax.append(mat_dev_data_dictionary)


        mat_data_dictionary["current_mode"] = "etaOpt"
        mat_data_dictionary["current_idx"] = -2
        dev.run_with_given_I(relative_I_efficiency_max*current_ref)      
                            
        # Zgeneral, tau, beta, taulin, betalin = one_shot_linear(dev,mat,Temperature_pair)
        # gammaEtaMaxFormulalin, etaMaxFormulalin =  EtaMaxFormula(Th,Tc,Zgeneral, taulin, betalin)
        # mat_data_dictionary["taulin"] = taulin
        # mat_data_dictionary["betalin"] = betalin
        # mat_data_dictionary["etaMaxFormulalin"] = etaMaxFormulalin                    
        dev_data_dictionary = dev.get_report_dict_full()
        mat_dev_data_dictionary = {**mat_data_dictionary,**dev_data_dictionary}
        mat_dev_data_dictionary_list_etaMax.append(mat_dev_data_dictionary)

    df_dev_run_currents_result = pd.DataFrame(mat_dev_data_dictionary_list)   
    df_dev_run_powMax_result   = pd.DataFrame(mat_dev_data_dictionary_list_powMax)   
    df_dev_run_etaOpt_result   = pd.DataFrame(mat_dev_data_dictionary_list_etaMax)   
    
    # df_dev_run_result = pd.concat(df_dev_run_currents_result, )
    
    
    return df_dev_run_currents_result, df_dev_run_powMax_result, df_dev_run_etaOpt_result



def draw_dev_perf(df_dev_run_currents_result, df_dev_run_powMax_result, df_dev_run_etaOpt_result, 
                  label_db, label_sampleid, label_doi):
    Is = df_dev_run_currents_result.current
    Vs = df_dev_run_currents_result.voltage
    QhAs = df_dev_run_currents_result.QhA
    pows = df_dev_run_currents_result.power
    etas = df_dev_run_currents_result.efficiency
    
    Imax   = df_dev_run_powMax_result.iloc[0].current
    powMax = df_dev_run_powMax_result.iloc[0].power *1e3
    etaMax = df_dev_run_powMax_result.iloc[0].efficiency *1e2
    
    Iopt   = df_dev_run_etaOpt_result.iloc[0].current
    powOpt = df_dev_run_etaOpt_result.iloc[0].power *1e3
    etaOpt = df_dev_run_etaOpt_result.iloc[0].efficiency *1e2
    
    figsize=(8,8)
    fig, axs = plt.subplots(2,2, figsize=figsize)
    fig.subplots_adjust(wspace=0.1, hspace=0.3)
    (ax1, ax2), (ax3, ax4) = axs
    
    suptitle = "{} {} {}".format(label_db, label_sampleid, label_doi)
    fig.suptitle(suptitle)
    
    title = "$I - V$ Characteristic"
    ax = ax1
    Xs = Is
    Ys = Vs
    ax.plot(Xs,Ys)
    ax.scatter(Xs,Ys)
    ax.set_xlabel(r'Current induced [$A$]')
    ax.set_ylabel(r'Voltage generated [$V$]')
    ax.set_title(title)
    
    title = "$I - P$ characteristic"
    ax = ax1
    ax = ax2
    Xs = Is
    Ys = pows*1e3
    ax.plot(Xs,Ys)
    ax.scatter(Xs,Ys)
    ax.scatter([Imax],[powMax],marker="o",edgecolor='C2',facecolor='white',s=70)
    ax.scatter([Iopt],[powOpt],marker="*",edgecolor='C2',facecolor='white',s=200)
    ax.set_xlabel(r'Current induced [$A$]')
    ax.set_ylabel(r'Power generated [$mW_{\rm el}$]')
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.set_title(title)
    
    title = r"$I - Q_h$ characteristic"
    ax = ax3
    Xs = Is
    Ys = QhAs*1e3
    ax.plot(Xs,Ys)
    ax.scatter(Xs,Ys)
    ax.set_xlabel(r'Current induced [$A$]')
    ax.set_ylabel(r'Hot side heat input [$mW_{\rm th}$]')
    ax.set_title(title)
    
    title = r"$I - \eta$ characteristic"
    ax = ax4
    Xs = Is
    Ys = etas*100
    ax.plot(Xs,Ys)
    ax.scatter(Xs,Ys)
    ax.scatter([Imax],[etaMax],marker="o",edgecolor='C2',facecolor='white',s=70)
    ax.scatter([Iopt],[etaOpt],marker="*",edgecolor='C2',facecolor='white',s=200)
    ax.set_xlabel(r'Current induced [$A$]')
    ax.set_ylabel(r'Efficiency $\eta$ [$\%$]')
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.set_title(title)
    
    return fig
       

if __name__ == "__main__":
    db_mode = 'teMatDb'    
    sampleid = 2
    doi = "10.1038/nature11439"
    leg_length = 1e-3 * 10 
    leg_area = 1e-6   * 3*3
    N_leg = 1  
    Tc, Th = 300, 900     
    
    interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
                  MatProp.OPT_EXTEND_LEFT_TO:1,          # ok to 0 Kelvin
                  MatProp.OPT_EXTEND_RIGHT_BY:2000}        # ok to +50 Kelvin from the raw data
    TF_mat_complete, mat = tep_generator_from_excel_files(sampleid, interp_opt)
    
    label_db = "DB: {}".format(db_mode)
    label_sampleid = "sampleid: {}".format(sampleid)
    label_doi = '[DOI: {}]'.format(doi)   
    
    # try:
    #     data_csv_path = "../data_csv/"
    #     df_db_csv = pd.read_csv(data_csv_path+"tematdb_v1.0.0_completeTEPset.csv")
    # except:
    # # if(1):
    #     data_csv_path = "./data_csv/"
    #     df_db_csv = pd.read_csv(data_csv_path+"tematdb_v1.0.0_completeTEPset.csv")
        
    dev = set_singleleg_device(mat, leg_length,leg_area,N_leg,Th,Tc)   
    df_dev_run_currents_result, df_dev_run_powMax_result, df_dev_run_etaOpt_result = run_pykeri(dev, sampleid,leg_length,leg_area,N_leg,Th,Tc)
    fig3 = draw_dev_perf(df_dev_run_currents_result, df_dev_run_powMax_result, df_dev_run_etaOpt_result,
                         label_db, label_sampleid, label_doi)
    fig3.show()

    