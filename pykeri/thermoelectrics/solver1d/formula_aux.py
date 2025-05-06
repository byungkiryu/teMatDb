# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 20:19:42 2020

@author: byungkiryu
"""



import datetime
import time as time
import math
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np

from pykeri.thermoelectrics.TEProp import TEProp

from scipy import integrate
from scipy.integrate import cumulative_trapezoid as cumtrapz
from scipy.integrate import trapezoid as trapz

from pykeri.scidata.matprop import MatProp
from pykeri.thermoelectrics.TEProp import TEProp
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.environment import Environment
from pykeri.thermoelectrics.solver1d.device import Device
from pykeri.util.interp_utils import BarycentricLagrangeChebyshevNodes
from pykeri.util.interp_utils import find_maximum

cumintegrate = lambda y,x: cumtrapz(y,x,initial=0)
integrate = lambda y,x: trapz(y,x)

debug_talking = False

def CHEVYSHEV_NODE(MIN_VALUE, MAX_VALUE, NUMBER_OF_NODES):
    CHEVYSHEV_array = (MIN_VALUE-MAX_VALUE)/2*np.cos(np.pi * np.linspace(0, NUMBER_OF_NODES - 1, NUMBER_OF_NODES) / (NUMBER_OF_NODES - 1)) + (MIN_VALUE+MAX_VALUE)/2
    return CHEVYSHEV_array


def EtaMaxFormula(Th,Tc,Zgeneral,tau,beta):
    deltaT  = Th - Tc
    ThPrime = Th - deltaT * tau
    TcPrime = Tc - deltaT * (tau+beta)
    TmPrime = (ThPrime+TcPrime)/2
    gammaEtaMaxFormula   = np.sqrt(1+Zgeneral*TmPrime)
    etaMaxFormula = (deltaT)/(ThPrime) * (gammaEtaMaxFormula-1)/(gammaEtaMaxFormula+TcPrime/ThPrime)
    return gammaEtaMaxFormula, etaMaxFormula

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
    
    print(I0, I1)
    
    if ( np.abs(I1/I0-1) < tol_gamma ):
        convergent_status = "____Conv. current I_Ref found using bisection method"
    else:
        convergent_status = "____Fail to find I_ref using bisection method"
    
    return I1, convergent_status

def get_zero_V_current(dev):
    log_report = ""
    module_outputdata_dictionary = {}
    df_current_search_log = pd.DataFrame()
    idx = 0
    try:

        dev_result = dev.fast_run_with_max_efficiency()
        module_outputdata_dictionary = dev.get_report_dict_full()
        module_outputdata_dictionary['dev_run_mode'] = 'fast_run_with_max_efficiency'
        
        current0 = dev.I * 1       
        current_dI = dev.I * 0.1
        
        xa = current0 
        xb = xa + current_dI
        xc = xb + current_dI

        ya = dev.Vgen - dev.I * dev.R_TE
        if (1):
            df_current_search_log.loc[idx,'iter'] = idx
            df_current_search_log.loc[idx,'dev_run_mode'] = 'xa__from_fast_run_with_max_efficiency'
            df_current_search_log.loc[idx,'current_xa'] = xa
            df_current_search_log.loc[idx,'voltage_ya'] = ya
            df_current_search_log.loc[idx,'is_pykeri_converged'] = dev_result
        
        dev.run_with_given_I(xb)
        yb = dev.Vgen - dev.I * dev.R_TE
        if (1):
            idx = idx+1
            df_current_search_log.loc[idx,'iter'] = idx
            df_current_search_log.loc[idx,'dev_run_mode'] = 'xb'
            df_current_search_log.loc[idx,'current_xb'] = xb
            df_current_search_log.loc[idx,'voltage_yb'] = yb
            df_current_search_log.loc[idx,'is_pykeri_converged'] = dev_result
        
        dev.run_with_given_I(xc)
        yc = dev.Vgen - dev.I * dev.R_TE
        if (1):
            idx = idx+1
            df_current_search_log.loc[idx,'iter'] = idx
            df_current_search_log.loc[idx,'dev_run_mode'] = 'xc'        
            df_current_search_log.loc[idx,'current_xc'] = xc
            df_current_search_log.loc[idx,'voltage_yc'] = yc
            df_current_search_log.loc[idx,'is_pykeri_converged'] = dev_result          
        

        for N_idx in range(10):             
            
            x_list = [xa,xb,xc]
            y_list = [ya,yb,yc]
            
            coeffs = np.polyfit(x_list,y_list,2)
            if (coeffs[0] < 0):
                x_near_root = np.max(np.roots(coeffs))
            else:
                x_near_root = np.min(np.roots(coeffs))
            
            if ( x_near_root.imag != 0 ):
                coeffs = np.polyfit(x_list,y_list,1)
                x_near_root = np.max(np.roots(coeffs))  
                x_near_root = xc + (x_near_root-xc)/2
                # print("hello")
            
            current_ref = x_near_root.real       
            x_near_root = current_ref
            
            # print("x_list ={}".format(x_list) )
            # print("iter={}, x_near_root={}".format(N_idx, x_near_root))
            dev_result = dev.run_with_given_I(current_ref)
            y_near_root = dev.Vgen - dev.I*dev.R_TE
                                
            if ( np.abs( xa - x_near_root) > np.abs( xc-x_near_root  )  ):
                x_list_update = [xb,xc,x_near_root]
                y_list_update = [yb,yc,y_near_root]
            else:
                x_list_update = [xa,xc,x_near_root]
                y_list_update = [ya,yc,y_near_root]
            # x_list_update.sort()
            sorted_arg = np.argsort(x_list_update)
            x_list_update = [x_list_update[i] for i in sorted_arg]
            y_list_update = [y_list_update[i] for i in sorted_arg]
            
            xa,xb,xc = x_list_update
            ya,yb,yc = y_list_update                
   
            V_near_root = dev.Vgen - dev.I*dev.R_TE
           
            log_report_each = "    iter.= {} I_ref ={:15.8f} A V ={:15.4f} V Voc ={:15.8f} V/Vgen ={:15.8f}".format(
                N_idx, x_near_root, V_near_root, dev.Vgen, V_near_root/ dev.Vgen )

            log_report = log_report + log_report_each + "\n"

            idx = idx+1
            df_current_search_log.loc[idx,'iter'] = idx
            df_current_search_log.loc[idx,'dev_run_mode'] = 'next x'     
            df_current_search_log.loc[idx,'current_xa'] = xa
            df_current_search_log.loc[idx,'current_xb'] = xb
            df_current_search_log.loc[idx,'current_xc'] = xc
            df_current_search_log.loc[idx,'current_x_near_root'] = current_ref
            df_current_search_log.loc[idx,'voltage_ya'] = ya
            df_current_search_log.loc[idx,'voltage_yb'] = yb
            df_current_search_log.loc[idx,'voltage_yc'] = yc
            df_current_search_log.loc[idx,'voltage_y_near_root'] = y_near_root
            df_current_search_log.loc[idx,'VoverVgen'] = V_near_root/dev.Vgen
            df_current_search_log.loc[idx,'is_pykeri_converged'] = dev_result

            df_current_search_log = df_current_search_log[['iter','dev_run_mode',
                                  'current_xa','current_xb','current_xc','current_x_near_root',
                                  'voltage_ya','voltage_yb','voltage_yc','voltage_y_near_root',
                                  'VoverVgen','is_pykeri_converged'
                                  ]]
            
            
            if ( np.abs( V_near_root/dev.Vgen ) < 0.01 ):
                break   


            
        # if ( type( current_ref ) == complex ):
        #     return_dictionary , module_outputdata_dictionary = get_zero_V_current_avoid_complex(dev)
        #     return return_dictionary , module_outputdata_dictionary 
            
        return_dictionary = {}
        return_dictionary['dev_result'] = dev_result
        return_dictionary['current_ref'] = current_ref
        return_dictionary['V_over_Vgen_at_Iref'] = (V_near_root/dev.Vgen).copy()
        return_dictionary['zero_V_search_log'] = log_report
        return return_dictionary, module_outputdata_dictionary, df_current_search_log
    
    except:
        return_dictionary = {}
        return_dictionary['dev_result'] = dev_result 
        return_dictionary['zero_V_search_log'] = "       fail for fast mode"
        return return_dictionary , module_outputdata_dictionary, df_current_search_log



def do_generate_mat(temp_grid, alpha_grid, rho_grid, kappa_grid, interp_opt):   
    Seebeck_raw_data = tuple((a_elem,b_elem) for (a_elem,b_elem) in zip(temp_grid,alpha_grid))
    elec_resi_raw_data = tuple((a_elem,b_elem) for (a_elem,b_elem) in zip(temp_grid,rho_grid))
    thrm_cond_raw_data = tuple((a_elem,b_elem) for (a_elem,b_elem) in zip(temp_grid,kappa_grid))
    mat = TEProp.from_raw_data(elec_resi_raw_data, Seebeck_raw_data, thrm_cond_raw_data, name="random")    
    mat.set_interp_opt(interp_opt)
    return mat

def generate_temperature_pair(TcRange,ThRange, Tstep):
    Tc = TcRange+.0
    ThRange = ThRange+.0
    Th_LIST = [Tc+1,Tc+2,Tc+4,Tc+10,Tc+20]
    if (small_temperature_range==False):
        Th_LIST = []
    Th_LIST = Th_LIST + list(np.arange(TcRange+Tstep, ThRange+Tstep, Tstep))
    # print(Th_LIST)
    TEMPERATURE_PAIR_LIST = []
    for Th in Th_LIST:
        TEMPERATURE_PAIR_LIST.append([Tc,Th])
    return TEMPERATURE_PAIR_LIST

def generate_interface_mat(IF_mode, if_length, rho_C, kappa_C, interface_label):
    if (IF_mode == True):
        IF = interface_mat(if_length, rho_C, kappa_C, interface_label)
    else:
        if_length, rho_C, kappa_C = 1e-4, 1e-12, 1e8
        IF = interface_mat(if_length, rho_C, kappa_C, interface_label)
        if_length = 0
    return IF, if_length, rho_C, kappa_C


def interface_mat(if_length, rho_C, kappa_C, interface_label):
    rho_C = rho_C     / if_length
    kappa_C = kappa_C * if_length    
    elec_resi_raw_data = ((1,    rho_C),(3000,    rho_C ))
    Seebeck_raw_data   = ((1,        0),(3000,        0 ))
    thrm_cond_raw_data = ((1,  kappa_C),(3000,  kappa_C ))    
    tep = TEProp.from_raw_data(elec_resi_raw_data, Seebeck_raw_data, thrm_cond_raw_data, name=interface_label)    
    return tep


def temperature_checker(mat,Tc,Th,autoTh_BUFFER):
    autoTc = mat.min_raw_T
    autoTh = mat.max_raw_T
    if(  Th <= autoTh + autoTh_BUFFER and autoTh > Tc  ):
        return True, autoTc, autoTh
    else:
        return False, autoTc, autoTh

def search_current_ref(dev, tol_gamma=1e-3):
    # N_idx = 10
    # SCALE = 0.95
    
    dev.run_with_given_gamma(0)
    if ( np.abs(dev.gamma) < tol_gamma ):
        if (debug_talking==True):
            print("______ Gamma is     conveged to be  {:.6g}. And current_ref is  {:.6f}.".format(dev.gamma,dev.I))    
        current_ref = dev.Vgen / dev.R_TE
        convergent_status = "____Conv. current I_Ref found using gamma running"
    else: 
        if (debug_talking==True):
            print("______ Gamma is not converged to be {:.6g}. And current_ref is {}.".format(dev.gamma,dev.I))   
        dev.fast_run_with_max_efficiency()
        I0 = dev.Vgen / dev.R_TE
        # V0 = dev.Vgen - dev.I * dev.R_TE
        
        dev.run_with_given_I(I0)
        I1 = dev.Vgen / dev.R_TE
        # V1 = dev.Vgen - dev.I * dev.R_TE

        # Ierr = np.abs(I0-I1)/I1
        current_ref, convergent_status = do_bisection_method(dev, I0, I1, tol_gamma)
        
        if (debug_talking==True):
            print("______ doing bisection method for gamma and current_ref search")
            print("______ Gamma is     converged to be {:.6g}. And current_ref is {}.".format(dev.gamma,dev.I))    
    return current_ref, convergent_status

def do_get_TEP_curves(mat,Temperature_array):
    alpha = mat.Seebeck(Temperature_array)
    rho  = mat.elec_resi(Temperature_array)
    sigma = 1/rho
    kappa = mat.thrm_cond(Temperature_array)
    PF_curve = alpha*alpha/rho
    zT_curve = PF_curve/kappa * Temperature_array
    compatibility_curve = ( np.sqrt( 1 + zT_curve ) - 1 ) / alpha / Temperature_array
    if (Temperature_array[0]==0):
        zT_curve[0]=0
    return alpha, rho, sigma, kappa, PF_curve, zT_curve, compatibility_curve

def do_calc_eff_inf_cascade_array(Temperature_array, zT_curve):
    gamma_curve = np.sqrt( zT_curve + 1)
    eta_red = (gamma_curve - 1)/ (gamma_curve+1)
    exponent = cumintegrate(eta_red/Temperature_array, Temperature_array)
    etaMax_inf_cascade_array = 1 - np.exp(-exponent)
    return etaMax_inf_cascade_array

def do_calc_eff_int_cascade_value(Temperature_array, zT_curve):
    gamma_curve = np.sqrt( zT_curve + 1)
    eta_red = (gamma_curve - 1)/ (gamma_curve+1)
    exponent = integrate(eta_red/Temperature_array, Temperature_array)
    etaMax_inf_cascade_value = 1 - np.exp(-exponent)
    return etaMax_inf_cascade_value  

def do_calc_eff_int_cascade_value_for_mat(Tc,Th,mat):
    num_Tpts = int( max( Th-Tc+1, 100) )
    Temperature_array = np.linspace(Tc,Th,num_Tpts)
    tep_curves = do_get_TEP_curves(mat,Temperature_array)
    alpha, rho, sigma, kappa, PF_curve, zT_curve, compatibility_curve = tep_curves
    eta_Max_inf_cascade_value = do_calc_eff_int_cascade_value(Temperature_array, zT_curve)
    etaCascade = eta_Max_inf_cascade_value
    return etaCascade

def one_shot_linear(dev,mat):
    temperature_pair = [dev.Tc, dev.Th]
    alphaC, alphaH = mat.Seebeck(temperature_pair)
    rhoC, rhoH = mat.elec_resi(temperature_pair)
    kappaC, kappaH = mat.thrm_cond(temperature_pair)

    if (dev.alphaBar == 0):
        tau0lin = 0
    else:
        tau0lin = 1/6 * (alphaC-alphaH)/dev.alphaBar
    if (dev.R_TE * dev.K_TE == 0):
        beta0lin = 0
    else:
        beta0lin = 1/6 * (rhoH*kappaH - rhoC*kappaC) / dev.R_TE / dev.K_TE
    
    return dev.Zgeneral, dev.tau, dev.beta, tau0lin, beta0lin


def do_calculate_peakzT(mat,Tc,Th):
    
    num_T_pts = 1000
    
    temperature = np.linspace(Tc,Th,num_T_pts)
    alpha = mat.Seebeck(temperature)
    rho = mat.elec_resi(temperature)
    kappa = mat.thrm_cond(temperature)
    zT_curve = alpha*alpha/rho/kappa*temperature
    peakzT = np.max(zT_curve)
    
    return peakzT
    
def calculate_ZTminANDrowe(mat,Tc,Th):
    deltaT = Th-Tc
    num_T_pts = 1000
    
    temperature = np.linspace(Tc,Th,num_T_pts)
    alpha = mat.Seebeck(temperature)
    rho = mat.elec_resi(temperature)
    kappa = mat.thrm_cond(temperature)
    
    alphaBar = integrate( alpha, temperature)/ deltaT
    RK = integrate( rho*kappa, temperature) / deltaT
    
    alpha_H = mat.Seebeck(Th)
    alpha_C = mat.Seebeck(Tc)
    
    beta = 1/deltaT * ( alpha_H *Th - alpha_C *Tc - alphaBar * deltaT )
    alpha_eff = (alpha_H - beta*deltaT/2/Th)
    Zm = alpha_eff**2 / RK
    Tm = (Th+Tc)/2
    ZTm = Zm*Tm
    
    gammaEtaMax_MinRowe, etaMax_MinRowe = EtaMaxFormula(Th,Tc,Zm,0,0)
    
    # print(Zm,Tm, ZTm, etaMax_MinRowe)
    
    return Tc, Th, ZTm, gammaEtaMax_MinRowe, etaMax_MinRowe
    
    ## See Min, Rowe, Kontostavlakis, J. Phys. D: Appl. Phys. 37, 1301 (2004). ##
    
    

def calculate_ZTeng_parameter(mat,Tc,Th):
    
    deltaT = Th-Tc
    num_T_pts = 1000
    
    temperature = np.linspace(Th,Tc,num_T_pts)  ## be careful T=Th at 0, T=Tc at L.
    alpha = mat.Seebeck(temperature)
    rho = mat.elec_resi(temperature)
    kappa = mat.thrm_cond(temperature)
    
    V = integrate( alpha, temperature)
    intRhodT = integrate( rho, temperature)
    intKapdT = integrate( kappa, temperature)
    
    PFeng = V*V/intRhodT
    ZTeng = PFeng/intKapdT * deltaT
    
    temp = cumintegrate(rho, temperature)
    temp2 = integrate( temp, temperature)
    W_joule = - temp2 / deltaT / integrate( rho, temperature )
    
    thomson = np.gradient(alpha)/np.gradient(temperature)*temperature
    temp = cumintegrate( thomson, temperature )
    temp2 = integrate( temp, temperature )
    if( integrate(thomson, temperature) == 0 ):
        W_thomson=0
    else:
        W_thomson = - temp2 / deltaT / integrate( thomson, temperature )
    
    etaC = deltaT / Th
    alpha_H = mat.Seebeck(Th)
    
    alpha_0 = alpha_H * deltaT / integrate( -alpha, temperature ) - integrate( thomson, temperature ) / integrate( alpha, temperature ) * W_thomson * etaC - 0 * W_joule * etaC
    alpha_1 = alpha_H * deltaT / integrate( -alpha, temperature ) - integrate( thomson, temperature ) / integrate( alpha, temperature ) * W_thomson * etaC - 1 * W_joule * etaC
    alpha_2 = alpha_H * deltaT / integrate( -alpha, temperature ) - integrate( thomson, temperature ) / integrate( alpha, temperature ) * W_thomson * etaC - 2 * W_joule * etaC
    
    gamma_ZTeng = np.sqrt( 1+ ZTeng * alpha_1 / etaC )
    etaMax_ZTeng = etaC / alpha_0 * ( gamma_ZTeng - 1 ) / (gamma_ZTeng + alpha_2)
    
    
    return Tc, Th, ZTeng, W_joule, W_thomson, alpha_0, alpha_1, alpha_2, etaMax_ZTeng, gamma_ZTeng    

##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################


def generate_tep_array(Tc,Th,ZTgen0,NUM_T_Chevy_Nodes):
    temp_array = CHEVYSHEV_NODE(Tc, Th, NUM_T_Chevy_Nodes)
    alpha_array = np.random.rand(NUM_T_Chevy_Nodes)
    rho_array = np.random.rand(NUM_T_Chevy_Nodes)*3+1
    kappa_array = np.random.rand(NUM_T_Chevy_Nodes)*3+1

    Tstep = 25
            
    temp_func = BarycentricLagrangeChebyshevNodes(temp_array, temp_array)
    alpha_func = BarycentricLagrangeChebyshevNodes(temp_array, alpha_array)
    rho_func = BarycentricLagrangeChebyshevNodes(temp_array, rho_array)
    kappa_func = BarycentricLagrangeChebyshevNodes(temp_array, kappa_array)

    Th = temp_array[-1]
    Tc = temp_array[0]
    deltaT = Th -Tc
    Tmid = (Th+Tc)/2

    num_T_pts = int(deltaT/Tstep)+1
    temp_grid = np.linspace(Tc-100,Th+200,num_T_pts)
    
    alphaBar = integrate( alpha_func(temp_grid), temp_func(temp_grid) ) / deltaT
    R0K0 = integrate( rho_func(temp_grid)*kappa_func(temp_grid), temp_func(temp_grid) ) / deltaT
    K0 = integrate( kappa_func(temp_grid), temp_func(temp_grid)) / deltaT
    R0 = R0K0/K0
    
    alpha_grid = alpha_func( temp_grid) / alphaBar * np.sqrt(ZTgen0/Tmid) * np.sqrt(1e-5)
    rho_grid = rho_func(temp_grid) / R0 *1e-5
    kappa_grid = kappa_func(temp_grid) / K0
    
    return temp_grid, alpha_grid, rho_grid, kappa_grid