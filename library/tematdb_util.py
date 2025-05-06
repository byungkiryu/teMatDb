# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""


import os
import math
import numpy as np
import pandas as pd
from datetime import datetime

from pykeri.scidata.matprop import MatProp
from pykeri.thermoelectrics.TEProp import TEProp
from pykeri.thermoelectrics.TEProp_xls import TEProp as TEProp_xls
# from pykeri.thermoelectrics.TEProp_df import TEProp as TEProp_df
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.environment import Environment
from pykeri.thermoelectrics.solver1d.device import Device

from pykeri.byungkiryu import byungkiryu_util as br

formattedDate, yyyymmdd, HHMMSS = br.now_string()


from matplotlib import pyplot as plt



def draw_mat_teps(mat, label_db="", label_sample_id="", label_doi=""):

    figsize = (8,8)
    fig1, axs1  = plt.subplots(2,2, figsize=figsize)
    fig2, axs2  = plt.subplots(2,2, figsize=figsize)
    (ax1, ax2), (ax3, ax4) = axs1
    (ax5, ax6), (ax7, ax8) = axs2
    fig1.subplots_adjust(wspace=0.1, hspace=0.3)
    fig2.subplots_adjust(wspace=0.1, hspace=0.3)
    
    suptitle = "{} {} {}".format(label_db, label_sample_id, label_doi)
    fig1.suptitle(suptitle)
    fig2.suptitle(suptitle)

    alpha_raw   = np.array( mat.Seebeck.raw_data() ).T
    rho_raw     = np.array( mat.elec_resi.raw_data() ).T    
    kappa_raw   = np.array( mat.thrm_cond.raw_data() ).T
    ZT_raw      = np.array( mat.ZT.raw_data() ).T

    sigma_raw   = rho_raw.copy()
    sigma_raw[1] = (1/rho_raw[1]).copy()
    
    autoTc = mat.min_raw_T
    autoTh = mat.max_raw_T    
    Ts_TEP, Ts_ZT, Ts_TEPZT = get_Ts_TEPZT(mat)
    TcZT, ThZT = min(Ts_ZT), max(Ts_ZT)
    TcTEP, ThTEP = min(Ts_TEP), max(Ts_TEP)
    TcTEPZT, ThTEPZT = min(Ts_TEPZT), max(Ts_TEPZT)
    


    Ts = Ts_TEPZT
    alpha = mat.Seebeck(Ts)
    rho   = mat.elec_resi(Ts)
    sigma = 1/rho
    kappa = mat.thrm_cond(Ts)
    
    RK = rho*kappa
    Lo = 2.44*1e-8
    Lorenz = RK/Ts
    

    def draws_interp_raw():
        ax.scatter( X_raw, Y_raw, label="TEP digitized \n from figure",color='C0')
        ax.plot( Ts, tep_interp, linewidth=10, alpha=0.35,label="TEP interpolated",color='C0')
        ax.set_title(tep_title)
        # ax.legend()
    def draws_interp_ZT():
        ax.scatter( X_raw, Y_raw, label="$ZT$ from figure",color='C1')
        ax.plot( Ts, tep_interp, linewidth=10, alpha=0.35,label="$ZT$ calculated \n from TEP interpolated",color='C2')
        ax.set_title(tep_title)

    def draws_interp_only():
        # ax.scatter( X_raw, Y_raw, label="raw")
        ax.plot( Ts, tep_interp, linewidth=10, alpha=0.35,label="TEP interpolated",color='C2')
        ax.set_title(tep_title)
        # ax.legend()        
    
    ax = ax1
    tep_title = r'Electrical Conductivity: $\sigma$'
    tep_array_raw = sigma_raw
    tep_interp = sigma/100 /1e3
    X_raw = tep_array_raw[0]
    Y_raw = tep_array_raw[1]  /100 /1e3
    draws_interp_raw()
    ax.set_ylabel(r"$\sigma$ [$10^3$ $S \cdot cm^{-1}$]")
    

    ax = ax2
    tep_title = r'Seebeck Coefficient: $\alpha$'
    tep_array_raw = alpha_raw
    tep_interp = alpha*1e3
    X_raw = tep_array_raw[0]
    Y_raw = tep_array_raw[1]*1e3
    draws_interp_raw()
    ax.set_ylabel(r"$\alpha$ [$mV \cdot K^{-1}$]")
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")

    ax = ax3
    tep_title = r'Thermal Conductivity: $\kappa$'
    tep_array_raw = kappa_raw
    tep_interp = kappa    
    X_raw = tep_array_raw[0]
    Y_raw = tep_array_raw[1]  
    draws_interp_raw()
    ax.set_ylabel(r"$\kappa$ [$W \cdot m^{-1} \cdot K^{-1}$]")
    
    ax = ax4
    tep_title = r'Figure of Meirt: $ZT$'
    tep_array_raw = ZT_raw
    tep_interp = alpha*alpha/rho/kappa*Ts
    X_raw = tep_array_raw[0]
    Y_raw = tep_array_raw[1]  
    draws_interp_ZT()
    ax.set_ylabel(r"$ZT$ [1]")
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    
    
    ax = ax5
    tep_title = r'Electrical Resistivity: $\rho$'
    tep_array_raw = rho_raw
    tep_interp = rho *1e5
    X_raw = tep_array_raw[0]
    Y_raw = tep_array_raw[1] *1e5
    draws_interp_raw()
    ax.set_ylabel(r"$\rho$ [$10^{-3}$ $\Omega \cdot cm$]")

    ax = ax6
    tep_title = r'Power Factor (PF): $\alpha^2 \sigma$'
    # tep_array_raw = kappa_raw
    tep_interp = alpha*alpha/rho *1e3
    # X_raw = tep_array_raw[0]
    # Y_raw = tep_array_raw[1]*1e3  
    draws_interp_only()
    ax.set_ylabel(r"$\alpha^2 \sigma$ [$mW \cdot m^{-1} \cdot K^{-2}$]")
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    
    ax = ax7 
    tep_title = r'RK: $\rho \kappa$'
    # tep_array_raw = kappa_raw
    tep_interp = RK
    # X_raw = tep_array_raw[0]
    # Y_raw = tep_array_raw[1]  
    draws_interp_only()
    ax.set_ylabel(r'$\rho \kappa$ [$W \cdot \Omega \cdot K^{-1}$]')

    ax = ax8
    tep_title = r'Lorenz number: $L = \rho \kappa_{\rm tot}  T^{-1}$'
    # tep_array_raw = kappa_raw
    tep_interp = Lorenz *1e8
    # X_raw = tep_array_raw[0]
    # Y_raw = tep_array_raw[1]  *1e8
    draws_interp_only()
    ax.set_ylabel(r'$L$ [$10^{-8}$ $W \cdot \Omega \cdot K^{-2}]$')
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    
    
    TcLowerP = min(TcZT, TcTEP, TcTEPZT)
    ThHigherP = max(ThZT, ThTEP, ThTEPZT)    
    TcLower  = math.floor( TcLowerP/100 - 0.50) * 100 - 50
    ThHigher = math.ceil( ThHigherP/100 + 0.50) * 100 + 50
    
    for ax in [ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8]:
        ax.set_xlim(TcLower,ThHigher)
        ax.set_xlabel(r"Temperature [$K$]")  
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        ax.xaxis.set_tick_params(which='both', direction='in')
        ax.yaxis.set_tick_params(which='both', direction='in')
        ax.legend()
    return fig1, fig2

def err_norm_calc(err, n_norm):
    abserr = np.abs(err)
    nsq_err = 1
    for i in range(n_norm):
        nsq_err= nsq_err * abserr
    mean_nsq_err = np.mean(nsq_err)
    root_mean_nsq_err = mean_nsq_err**(1/n_norm)
    # print(n_norm,root_mean_nsq_err)
    return root_mean_nsq_err

def err_norm_calc2(err, n_norm):
    # abserr = np.abs(err)
    nsq_err = 1
    for i in range(n_norm):
        nsq_err= nsq_err * err
    mean_nsq_err = np.mean(nsq_err)
    if (mean_nsq_err>0):
        root_mean_nsq_err = mean_nsq_err**(1/n_norm)
    else:
        root_mean_nsq_err = -( (-mean_nsq_err)**(1/n_norm) )
    # print(n_norm,root_mean_nsq_err)
    return root_mean_nsq_err

def get_Ts_TEPZT(mat):
    ZT_raw   = np.array( mat.ZT.raw_data() ).T
    
    autoTc = mat.min_raw_T
    autoTh = mat.max_raw_T    
    TcZT = min(ZT_raw[0])
    ThZT = max(ZT_raw[0])    
    TcTEPZT = max(autoTc, TcZT,1)
    ThTEPZT = min(autoTh, ThZT)

    import math
    def generate_Trange(Tmin,Tmax):        
        if (Tmin > Tmax):
            Tmin, Tmax = Tmax, Tmin
        Tceil = math.ceil(Tmax)
        Tfloor = math.floor(Tmin)
        if (Tfloor <1):
            Tfloor=1            
        Ts = np.arange( Tfloor, Tceil+1 )
        return Ts
    
    ## T range setting
    Ts_TEP   = generate_Trange(autoTc, autoTh)
    Ts_ZT    = generate_Trange(TcZT, ThZT )    
    Ts_TEPZT = generate_Trange(TcTEPZT, ThTEPZT)

    return Ts_TEP, Ts_ZT, Ts_TEPZT

def get_ZTs_interp(mat, Ts_TEPZT):
    alpha_interp = mat.Seebeck(Ts_TEPZT)
    rho_interp   = mat.elec_resi(Ts_TEPZT)
    kappa_interp = mat.thrm_cond(Ts_TEPZT)    
    ZT_TEP_on_Ts_TEPZT    = alpha_interp*alpha_interp/rho_interp/kappa_interp*Ts_TEPZT
    ZT_raw_on_Ts_TEPZT    = mat.ZT(Ts_TEPZT)   
    return ZT_raw_on_Ts_TEPZT, ZT_TEP_on_Ts_TEPZT

def get_Zs_interp(mat, Ts_TEPZT):
    alpha_interp = mat.Seebeck(Ts_TEPZT)
    rho_interp   = mat.elec_resi(Ts_TEPZT)
    kappa_interp = mat.thrm_cond(Ts_TEPZT)    
    Z_TEP_on_Ts_TEPZT    = alpha_interp*alpha_interp/rho_interp/kappa_interp
    Z_raw_on_Ts_TEPZT    = mat.ZT(Ts_TEPZT) / Ts_TEPZT   
    return Z_raw_on_Ts_TEPZT, Z_TEP_on_Ts_TEPZT


def tep_generator_from_excel_files(sampleid, interp_opt):    
    # version = "v1.0.0"
    DIR_tematdb = "./data_00_tematdb_raw_excel/"
    # filename1 = "_tematdb_tep_excel_{:s}_{:05d}-{:05d}.xlsx".format(version,1,50)
    # filename2 = "_tematdb_tep_excel_{:s}_{:05d}-{:05d}.xlsx".format(version,51,100)
    # filename3 = "_tematdb_tep_excel_{:s}_{:05d}-{:05d}.xlsx".format(version,101,150)
    # filename4 = "_tematdb_tep_excel_{:s}_{:05d}-{:05d}.xlsx".format(version,151,200)
    # filename5 = "_tematdb_tep_excel_{:s}_{:05d}-{:05d}.xlsx".format(version,201,250)
    # filename6 = "_tematdb_tep_excel_{:s}_{:05d}-{:05d}.xlsx".format(version,251,300)
    # filename7 = "_tematdb_tep_excel_{:s}_{:05d}-{:05d}.xlsx".format(version,301,350)
    # filename8 = "_tematdb_tep_excel_{:s}_{:05d}-{:05d}.xlsx".format(version,351,400)
    # filename9 = "_tematdb_tep_excel_{:s}_{:05d}-{:05d}.xlsx".format(version,401,450)
    files = ['_tematdb_tep_excel_v1.1.6_00001-00050.xlsx',
             '_tematdb_tep_excel_v1.1.6_00051-00100.xlsx',
             '_tematdb_tep_excel_v1.1.6_00101-00150.xlsx',
             '_tematdb_tep_excel_v1.1.6_00151-00200.xlsx',
             '_tematdb_tep_excel_v1.1.6_00201-00250.xlsx',
             '_tematdb_tep_excel_v1.1.6_00251-00300.xlsx',
             '_tematdb_tep_excel_v1.1.6_00301-00350.xlsx',
             '_tematdb_tep_excel_v1.1.6_00351-00400.xlsx',
             '_tematdb_tep_excel_v1.1.6_00401-00450.xlsx']
    
    # files = ['_tematdb_tep_excel_v1.0.0_00001-00050_confirmed_230330.xlsx',
    #   '_tematdb_tep_excel_v1.0.0_00051-00100_confirmed_230411.xlsx',
    #   '_tematdb_tep_excel_v1.0.0_00101-00150_confirmed_220606.xlsx',
    #   '_tematdb_tep_excel_v1.0.0_00151-00200_confirmed_230331.xlsx',
    #   '_tematdb_tep_excel_v1.0.0_00201-00250_confirmed_230407.xlsx',
    #   '_tematdb_tep_excel_v1.0.0_00251-00300_confirmed_230331.xlsx',
    #   '_tematdb_tep_excel_v1.0.0_00301-00350_confirmed_220606.xlsx',
    #   '_tematdb_tep_excel_v1.0.0_00351-00400_confirmed_220606.xlsx',
    #   '_tematdb_tep_excel_v1.0.0_00401-00450_confirmed_230330.xlsx']
    # files = os.listdir(DIR_tematdb)
    
    fileindex = int((sampleid-1)/50)
    filename = files[fileindex]
    sheetname = "#{:05d}".format(sampleid)        
    
    try:
        mat = TEProp_xls.from_dict({'xls_filename': DIR_tematdb+filename,
                                'sheetname': sheetname, 'color': (sampleid/255, 0/255, 0/255)} ) 
        TF_mat_complete = True     
        mat.set_interp_opt(interp_opt)
        print(sampleid, "read successfully by pykeri!!")
        return TF_mat_complete, mat
    except:
        print(filename, sampleid, 'data set is incompelete or empty')
        TF_mat_complete = False
        mat = False        
        return TF_mat_complete, mat

