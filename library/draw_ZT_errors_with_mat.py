# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""

        
import math
import numpy as np
import pandas as pd

import scipy.stats as stats
import streamlit as st

from datetime import datetime

from pykeri.scidata.matprop import MatProp
# from pykeri.thermoelectrics.TEProp import TEProp
# from pykeri.thermoelectrics.TEProp_xls import TEProp as TEProp_xls
from pykeri.thermoelectrics.TEProp_df import TEProp as TEProp_df
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.environment import Environment
from pykeri.thermoelectrics.solver1d.device import Device

from pykeri.byungkiryu import byungkiryu_util as br

from library.tematdb_util import get_Ts_TEPZT, get_ZTs_interp
from library.tematdb_util import draw_mat_teps, tep_generator_from_excel_files
from library.dev_performance import set_singleleg_device, run_pykeri, draw_dev_perf

from matplotlib import pyplot as plt

formattedDate, yyyymmdd, HHMMSS = br.now_string()

def draw3QQ(df1,df2, label_db="", label_sample_id="", label_doi=""):
    suptitle = "{}".format(label_db)     
    figsize = (13,4) 
    # fig, axs = plt.subplots(1,3,figsize=figsize, sharex=True, constrained_layout=True )  
    fig, axs = plt.subplots(1,3,figsize=figsize, sharex=True,  )  
    fig.subplots_adjust(wspace=0.4, top=0.8)
    (ax1, ax2, ax3) = axs 
    fig.suptitle(suptitle)
    
    ax = ax1
    tep_title = r'Q-Q plot of $\delta$($ZT)$'
    X = df1.ZT_author_declared - df1.ZT_tep_reevaluated
    stats.probplot(X,dist=stats.norm, plot=ax, rvalue=True)     
    ax.set_ylabel(r"$\delta$($ZT$)")
    # Xlim = max( np.abs(X) ) 
    # print(Xlim)
    # Xlim2 = (math.ceil(Xlim/0.1)+0.0) *0.1
    # # Xrange = np.arange(-Xlim2, Xlim2+0.05,0.1)
    # Xlim3 = Xlim2 *1.1
    # ax.set_ylim(-Xlim3,Xlim3)
    ax.set_xlim(-4.5,4.5)
    # ax.legend(loc=2)
    ax.set_title(tep_title)

    ax = ax2
    tep_title = r'Q-Q plot of $\delta$(avg-$ZT$)'
    X = df2.dropna(axis=0,subset='d_avgZT').d_avgZT
    stats.probplot(X,dist=stats.norm, plot=ax, rvalue=True)    
    ax.set_ylabel(r"$\delta$(avg-$ZT$)")    
    # Xlim = max( np.abs(X) ) 
    # Xlim2 = (math.ceil(Xlim/0.1)+0.0) *0.1
    # # Xrange = np.arange(-Xlim2, Xlim2+0.05,0.1)
    # Xlim3 = Xlim2 *1.1
    # ax.set_ylim(-Xlim3,Xlim3)
    ax.set_xlim(-4.5,4.5)
    ax.set_title(tep_title)

    ax = ax3
    tep_title = r'Q-Q plot of $\delta$(peak-$ZT$)'
    X = df2.dropna(axis=0,subset='d_peakZT').d_peakZT
    stats.probplot(X,dist=stats.norm, plot=ax, rvalue=True)    
    ax.set_ylabel(r"$\delta$(peak-$ZT$)")    
    # Xlim = max( np.abs(X) ) 
    # Xlim2 = (math.ceil(Xlim/0.1)+0.0) *0.1
    # # Xrange = np.arange(-Xlim2, Xlim2+0.05,0.1)
    # Xlim3 = Xlim2 *1.1
    # ax.set_ylim(-Xlim3,Xlim3)
    ax.set_xlim(-4.5,4.5)
    ax.set_title(tep_title)
    
    for ax in (ax1, ax2, ax3):
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        ax.xaxis.set_tick_params(which='both', direction='in', labelbottom=True)
        ax.yaxis.set_tick_params(which='both', direction='in', labelbottom=True)        
    return fig

def draw4QQ(df1,df2, label_db="", label_sample_id="", label_doi=""):
    suptitle = "{}".format(label_db)        
    figsize = (8,8)        
    fig, axs  = plt.subplots(2,2, figsize=figsize, sharex=True)
    fig.subplots_adjust(wspace=0.1, hspace=0.3)
    (ax1, ax2), (ax3, ax4) = axs
    fig.suptitle(suptitle)
    
    ax = ax1
    tep_title = r'Q-Q plot of $\delta(ZT)$'
    X = df1.ZT_author_declared - df1.ZT_tep_reevaluated
    stats.probplot(X,dist=stats.norm, plot=ax, rvalue=True)     
    ax.set_ylabel(r"$\delta$($ZT$)")
    Xlim = max( np.abs(X) ) 
    Xlim2 = (math.ceil(Xlim/0.1)+0.0) *0.1
    # Xrange = np.arange(-Xlim2, Xlim2+0.05,0.1)
    Xlim3 = Xlim2 *1.1
    ax.set_ylim(-Xlim3,Xlim3)
    ax.set_xlim(-4.5,4.5)
    # ax.legend(loc=2)
    ax.set_title(tep_title)

    ax = ax2
    tep_title = r'Q-Q plot of $\delta(ZT)/ZT$'
    X = df1.ZT_author_declared / df1.ZT_tep_reevaluated -1
    stats.probplot(X,dist=stats.norm, plot=ax, rvalue=True)     
    ax.set_ylabel(r"$\delta$($ZT$)/$ZT$")
    Xlim = max( np.abs(X) ) 
    Xlim2 = (math.ceil(Xlim/0.1)+0.0) *0.1
    # Xrange = np.arange(-Xlim2, Xlim2+0.05,0.1)
    Xlim3 = Xlim2 *1.1
    ax.set_ylim(-Xlim3,Xlim3)
    ax.set_xlim(-4.5,4.5)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")    
    # ax.legend(loc=2)
    ax.set_title(tep_title)

    ax = ax3
    tep_title = r'Q-Q plot of $\delta (avg-ZT)$ deviation'
    X = df2.dropna(axis=0,subset='davgZT').davgZT
    stats.probplot(X,dist=stats.norm, plot=ax, rvalue=True)    
    ax.set_ylabel(r"$\delta$(avg-$ZT$)")    
    Xlim = max( np.abs(X) ) 
    Xlim2 = (math.ceil(Xlim/0.1)+0.0) *0.1
    Xlim3 = Xlim2 *1.1
    ax.set_ylim(-Xlim3,Xlim3)
    ax.set_xlim(-4.5,4.5)
    ax.set_title(tep_title)

    ax = ax4
    tep_title = r'Q-Q plot of $\delta (peak-ZT)$ deviation'
    X = df2.dropna(axis=0,subset='dpeakZT').dpeakZT
    stats.probplot(X,dist=stats.norm, plot=ax, rvalue=True)    
    ax.set_ylabel(r"$\delta$(peak-$ZT$)")    
    Xlim = max( np.abs(X) ) 
    Xlim2 = (math.ceil(Xlim/0.1)+0.0) *0.1        
    Xlim3 = Xlim2 *1.1
    ax.set_ylim(-Xlim3,Xlim3)        
    ax.set_xlim(-4.5,4.5)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")    
    ax.set_title(tep_title)
    
    for ax in [ax1,ax2,ax3,ax4]:
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        ax.xaxis.set_tick_params(which='both', direction='in')
        ax.yaxis.set_tick_params(which='both', direction='in')
    return fig

def draw_ZT_error_correlation(df_db_error):
    df_to_plotly = df_db_error[ df_db_error.errdZT_Linf > 0].copy()
    hover_data = ['sample_id','doi','d_avgZT','d_peakZT','errdZT_Linf','errdZT_L2']
    
    import plotly.express as px    
    fig = px.scatter(
        df_to_plotly,
        x='peak_ZT_ofTEPEval',
        y='peak_ZT_ofRawFig',
        size='errdZT_Linf',
        color='peak_ZT_ofRawFig',        
        hover_name="sample_id",
        hover_data=hover_data
        )
    figa = fig
    st.plotly_chart(figa)
    st.caption("Peak ZT bias plot: ZT_raw from author publication vs. ZT_TEP from TEP reevalulation. Size is Linf. Color is peakZT_raw_on_Ts_ZT.")

    fig = px.scatter(
        df_to_plotly,
        x='avg_ZT_ofTEPEval',
        y='avg_ZT_ofRawFig',
        size='errdZT_Linf',
        color='avg_ZT_ofRawFig',        
        hover_name="sample_id",
        hover_data=hover_data
        )
    figa = fig
    st.plotly_chart(figa)
    st.caption("ZT average bias plot: ZT_raw from author publication vs. ZT_TEP from TEP reevalulation. Size is Linf. Color is peakZT_raw_on_Ts_ZT.")
    
    figc = px.scatter(
        df_to_plotly,
        x='d_avgZT',
        y='d_peakZT',
        size='errdZT_Linf',
        color='peak_ZT_ofRawFig', 
        hover_name="sample_id",
        hover_data=hover_data
        )
    st.plotly_chart(figc)    
    st.caption("ZT deviation correlation between d(peakZT) and d(avgZT). Size is Linf. Color is peakZT_raw_on_Ts_ZT.")
        
    fig = px.scatter(
        df_to_plotly,
        x='errdZT_L2',
        y='d_peakZT',
        size='errdZT_Linf',
        color='peak_ZT_ofRawFig',   
        hover_name="sample_id",
        hover_data=hover_data
        )
    figb = fig
    st.plotly_chart(figb)
    st.caption("Error Effect on ZT bias. Size is Linf. Color is peakZT_raw_on_Ts_ZT. Size is Linf. Color is peakZT_raw_on_Ts_ZT.")
    
    # fig = px.scatter(
    #     df_to_plotly,
    #     x='errdZT_L1',
    #     y='d_peakZT',
    #     size='errdZT_Linf',
    #     color='peak_ZT_ofRawFig',   
    #     hover_name="sample_id",
    #     hover_data=hover_data
    #     )
    # figb = fig
    # st.plotly_chart(figb)
    # st.caption("Error Effect on ZT bias")    
    
    # fig = px.scatter(
    #     df_to_plotly,
    #     x='Linf',
    #     y='dpeakZT',
    #     size='L2',
    #     color='peakZT_raw_on_Ts_ZT',   
    #     hover_name="sample_id",
    #     hover_data=hover_data
    #     )
    # figb = fig
    # st.plotly_chart(figb)
    # st.caption("Error Effect on ZT bias")          
     
    # fig = px.scatter(
    #     df_to_plotly,
    #     x='dZT_mean',
    #     y='dZT_std_ddof1',
    #     size='Linf',
    #     color='peakZT_raw_on_Ts_ZT',   
    #     hover_name="sample_id",
    #     hover_data=hover_data
    #     )
    # figb = fig
    # st.plotly_chart(figb)
    # st.caption("Error Effect on ZT bias")   


def draw_mat_ZT_errors(mat, label_db="", label_sample_id="", label_doi=""):
    suptitle = "{} {} {}".format(label_db, label_sample_id, label_doi)
    
    figsize = (8,8)
    
    fig, axs1  = plt.subplots(2,2, figsize=figsize)
    fig.subplots_adjust(wspace=0.1, hspace=0.3)
    (ax1, ax2), (ax3, ax4) = axs1
    fig.suptitle(suptitle)

    # (ax5, ax6), (ax7, ax8) = axs2
    # fig2, axs2  = plt.subplots(2,2, figsize=figsize, sharex=True)
    # fig2.suptitle(suptitle)

    alpha_raw   = np.array( mat.Seebeck.raw_data() ).T
    rho_raw     = np.array( mat.elec_resi.raw_data() ).T    
    kappa_raw   = np.array( mat.thrm_cond.raw_data() ).T
    ZT_raw   = np.array( mat.ZT.raw_data() ).T

    sigma_raw   = rho_raw.copy()
    sigma_raw[1] = (1/rho_raw[1]).copy()    

    autoTc = mat.min_raw_T
    autoTh = mat.max_raw_T
    
    Ts_TEP, Ts_ZT, Ts_TEPZT = get_Ts_TEPZT(mat)
    TcZT, ThZT = min(Ts_ZT), max(Ts_ZT)
    TcTEP, ThTEP = min(Ts_TEP), max(Ts_TEP)
    TcTEPZT, ThTEPZT = min(Ts_TEPZT), max(Ts_TEPZT)
    
    
    ZT_raw_on_Ts_TEPZT, ZT_TEP_on_Ts_TEPZT = get_ZTs_interp(mat, Ts_TEPZT)
    ZT_raw_on_Ts_TEP,   ZT_TEP_on_Ts_TEP   = get_ZTs_interp(mat, Ts_TEP)
    ZT_raw_on_Ts_ZT,    ZT_TEP_on_Ts_ZT    = get_ZTs_interp(mat, Ts_ZT)
    
    ZT_error_on_Ts_TEPZT = ZT_raw_on_Ts_TEPZT - ZT_TEP_on_Ts_TEPZT
    
    peakZT_raw_on_Ts_ZT  = np.max(ZT_raw_on_Ts_ZT)
    peakZT_TEP_on_Ts_TEP = np.max(ZT_TEP_on_Ts_TEP)
    ZT_dev_max = np.max( np.abs(ZT_error_on_Ts_TEPZT) )*1.2

    T_plot_min = min(autoTc,min(ZT_raw[0]))
    T_plot_max = min(autoTh,max(ZT_raw[0]))
    T_plot_min = math.floor(T_plot_min/100)*100-50
    T_plot_max = math.ceil(T_plot_max/100)*100+50
    
    ax = ax1
    tep_title = r'Figure of Meirt: $ZT$'
    ax.plot( Ts_TEP, ZT_TEP_on_Ts_TEP, linewidth=10, alpha=0.35,label="$ZT$ calculated \n from TEP interpolated",color='C2')
    # ax.plot( Ts_ZT, ZT_raw_on_Ts_ZT, color='C1')
    ax.scatter( ZT_raw[0], ZT_raw[1], label="$ZT$ from figure",color='C1')
    ax.set_title(tep_title)
    ax.set_xlim(T_plot_min,T_plot_max)
    ax.set_ylim(-0.3, max( max(ZT_raw_on_Ts_ZT), max(ZT_raw_on_Ts_TEP))+.3)
    ax.legend()    
    ax.set_ylabel(r"$ZT$ [1]")
    ax.set_xlabel("Temperature [K]")
    
     
    ax = ax2
    tep_title = r'$ZT$-$ZT$ plot'
    ax.plot( [-0.1,max(ZT_raw_on_Ts_TEPZT)+0.1], [-0.1,max(ZT_raw_on_Ts_TEPZT)+0.1], 
            linestyle='--',color='C0',)
    ax.scatter( ZT_TEP_on_Ts_TEPZT, ZT_raw_on_Ts_TEPZT,color='C1')
    ax.set_xlabel(r"$ZT$ calculated from TEP ($ZT_{\rm TEP}$)")
    ax.set_ylabel(r"$ZT$ from figure ($ZT_{\rm fig}$)")
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")    
    ax.set_title(tep_title)


    ax = ax3
    tep_title = r'Deviation in $ZT$: $\delta(ZT)$'
    ax.plot( Ts_TEPZT, ZT_raw_on_Ts_TEPZT - ZT_TEP_on_Ts_TEPZT , label=r"$\delta(ZT)$",color='C1')
    ax.plot( Ts_TEPZT, Ts_TEPZT*0 , linestyle='--',color='C0',)
    ax.set_ylim(-ZT_dev_max,+ZT_dev_max)    
    ax.set_title(tep_title)
    ax.set_xlim(T_plot_min,T_plot_max)
    ax.legend()    
    ax.set_ylabel(r"$\delta (ZT) := ZT_{\rm fig} - ZT_{\rm TEP}$")
    ax.set_xlabel("Temperature [K]")
    
    
    ax = ax4
    # ax = ax2
    tep_title = r'Q-Q plot of $\delta(ZT)$'
    x = np.array(ZT_error_on_Ts_TEPZT)
    res4 = stats.probplot(x,dist=stats.norm, plot=ax, rvalue=True)
    ax.set_title(tep_title)
    ax.set_ylabel(r"$\delta (ZT) := ZT_{\rm fig} - ZT_{\rm TEP}$")
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")    
    
    for ax in [ax1,ax2,ax3,ax4]:
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        ax.xaxis.set_tick_params(which='both', direction='in')
        ax.yaxis.set_tick_params(which='both', direction='in')
    return fig


if __name__ == "__main__":
    db_mode = 'teMatDb'
    sample_id = 1
    
    file_tematdb_metadata_csv = "_tematdb_metadata_v1.0.0-20230407_brjcsjp.xlsx"
    file_tematdb_db_csv  =  "tematdb_v1.0.0_completeTEPset.csv"
    df_db_meta = pd.read_excel("../"+file_tematdb_metadata_csv, sheet_name='list', )
    df_db_csv = pd.read_csv("../data_csv/"+file_tematdb_db_csv)
    
    df_db_meta_sample_id = df_db_meta[ df_db_meta.sample_id == sample_id]
    doi = df_db_meta_sample_id.DOI.iloc[0]
    label_db = "DB: {}".format(db_mode)
    label_sample_id = "sample_id: {}".format(sample_id)
    label_doi = '[DOI: {}]'.format(doi)    
    
    
    interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
                  MatProp.OPT_EXTEND_LEFT_TO:1,          # ok to 0 Kelvin
                  MatProp.OPT_EXTEND_RIGHT_BY:2000}        # ok to +50 Kelvin from the raw data
    df_db_csv_sample_id = df_db_csv[ df_db_csv.sample_id == sample_id]
    df_alpha = df_db_csv_sample_id[ df_db_csv_sample_id.tepname == 'alpha']
    df_rho   = df_db_csv_sample_id[ df_db_csv_sample_id.tepname == 'rho'  ]
    df_kappa = df_db_csv_sample_id[ df_db_csv_sample_id.tepname == 'kappa']
    df_ZT    = df_db_csv_sample_id[ df_db_csv_sample_id.tepname == 'ZT'   ]
    try:
        mat = TEProp_df.load_from_df(df_alpha, df_rho, df_kappa, df_ZT, mat_name='test')
        mat.set_interp_opt(interp_opt)
        TF_mat_complete = True
    except:
        TF_mat_complete = False

    fig = draw_mat_ZT_errors(mat, label_db=label_db, label_sample_id=label_sample_id, label_doi=label_doi)
    