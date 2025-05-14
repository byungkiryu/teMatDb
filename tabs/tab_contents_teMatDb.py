# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""

import os
import streamlit as st

# import math
# import numpy as np
# import pandas as pd
# import streamlit as st

# from matplotlib import pyplot as plt
# import scipy.stats as stats  

# from datetime import datetime

# from pykeri.scidata.matprop import MatProp
# from pykeri.thermoelectrics.TEProp import TEProp
# from pykeri.thermoelectrics.TEProp_xls import TEProp as TEProp_xls
# from pykeri.thermoelectrics.TEProp_df import TEProp as TEProp_df
# from pykeri.thermoelectrics.solver1d.leg import Leg
# from pykeri.thermoelectrics.solver1d.environment import Environment
# from pykeri.thermoelectrics.solver1d.device import Device

# from pykeri.byungkiryu import byungkiryu_util as br


        
# from library.tematdb_util import get_Ts_TEPZT
# from library.tematdb_util import draw_mat_teps, tep_generator_from_excel_files
# from library.draw_ZT_errors_with_mat import draw_mat_ZT_errors, draw_ZT_error_correlation, draw3QQ, draw4QQ
# from library.dev_performance import set_singleleg_device, run_pykeri, draw_dev_perf

# formattedDate, yyyymmdd, HHMMSS = br.now_string()

# st.set_page_config(page_title="teMatDb")


# st.title("teMatDb")
# st.subheader(":blue[t]hermo:blue[e]lectric :blue[Mat]erial :blue[D]ata:blue[b]ase")
# st.markdown("- High quality thermoelectric (TE) database (DB), teMatDb (ver1.1.1)")
# st.markdown("- That can be used for data analytics, machine learning and AI")

HERE = os.path.dirname(os.path.abspath(__file__))
report_path_teMatDb272 = "../teMatDb_publication/teMatDb272_dataset_20250515/z_teMatDb_report.txt"
REPORT_PATH_teMatDb272 = os.path.join(HERE, report_path_teMatDb272)

def show_dataDistribution():
    dbpubs = 'teMatDb272 characteristics'
    st.header(":blue[TEP distribution]")    
    with st.expander("See data characteristics", expanded=False):    
        st.subheader(":green[Fig. 1 ZT distribution vs. Starrydata2]")    
        st.subheader(":green[Fig. 2 TEP digitization and ZT error] ")    
        st.markdown("(a) Digitization and continuation for sample_id = 43.") 
        st.markdown("(b) ZT-ZT plot, deviation, and its Q-Q plot") 
        st.subheader(":green[Fig. 3 ZT from Figs vs. ZT from TEPs] ")    
        st.markdown("(a) ZT-ZT before sc-ZT filtered and (b) Q-Q analysis before filtering")    
        st.markdown("(c) ZT-ZT before sc-ZT filtered and (d) Q-Q analysis after filtering")    
        st.subheader(":green[Fig. 4 sc-ZT filter validation in Starrydata2 20250501]")  
        st.subheader(":green[Fig. 5 TEP distribution for teMatDb272]")  
        st.markdown(r"$\alpha$, $\rho$, $\sigma$, Power factor, $\kappa$, $\rho\kappa$")    
        st.subheader(":green[Fig. 6 TEP analysis]")  
        st.markdown(r"Relation between $\alpha$, thermoelectric Lorenz number ($L_{\rm TE}$), and ZT, where $L_{\rm TE}:=\frac{\rho \kappa}{T}$.")    
        st.markdown(r"L(T) curve, L-$\alpha$ with ZT color")    
        st.subheader(":green[Fig. 7 Application. Device performance prediction]") 
        st.markdown(r"Thermoelectric efficiency and power plot with $\Delta$T")    
     
    return True


def show_report_teMatDb272():
    st.header(":blue[DB publication]")   
    # 파일 읽기
    with st.expander("How to constructued?", expanded=False):            
 
            
        with open(REPORT_PATH_teMatDb272, "r", encoding="utf-8") as file:
            report_text = file.read()
        st.subheader(":red[Data construction infomation] (z_teMatDb_report.txt)")
        st.text(report_text)




