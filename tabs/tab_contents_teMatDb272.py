# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""

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



def show_dataDistribution():
    st.header(":blue[teMatDb vs. Starrydata2]")    
    st.subheader(":red[TEP distribution]")    
    st.subheader(":red[ZT distribution]")    
    st.subheader(":red[Efficiency distribution]") 
     
    return True