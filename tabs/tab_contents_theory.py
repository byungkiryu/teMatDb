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

  
def show_data_description():
    st.header(":blue[Thermoelectric Data]")
    with st.expander("See details.."):
        st.subheader(":red[Data Sources]")  
        st.subheader(":red[Thermoelectric Materials to Digital Data]")  
        st.subheader(":red[Thermoelectric Device Data]")  
        
    st.header(":blue[teMatDb]")
    with st.expander("See details.."):
        st.subheader(":red[Data digitization and teMatDb]")
        st.markdown("Thermoelectric properties data are digitized by humans using \
                    WebPlotDigitizer (https://apps.automeris.io/wpd/).")
        st.subheader(":red[Metadata in teMatDb]")
        st.markdown("We digitize single sample per publication, exhibiting the best peak zT. And we also \
                    gather the material information: doi, composition, synthesis method, author information.")
        st.subheader(":red[Possible Source of Errors]")
        st.markdown("There are many possible source of data error: \
                    (1) material error, (2) measurement error, \
                    (3) publicatoin error, (4) digitization error.\
                    While (1-3) are before digitizatoin, (4) can be made while digitization.\
                    We tested the digitization error while digitizing figure data.\
                    using the figures of 3.5 inch wide and 3.0 ich height, \
                    with 30 filled circles and 30 filled triangles,\
                    whehe their positions are randomly generated between 0 and 100.\
                    The mean deviation is -0.114% and the standard deviation is +0.12% for 300 dpi.\
                    The mean deviation is -0.039% and the standard deviation is +0.23% for 72 dpi.\
                    We would like to note that 72 dpi means ~210 dots for axis. Thus, 1/210 = ~0.5%.\
                    It seems that though 72 dpi is still poor, it might be enough to be digitized.")
        st.subheader(":red[Digitization Error Estimated]")
        st.markdown("Then, we estimate the error in ZT. There are four parameters: ZT = alpha x alpha x sigma / kappa x T.\
                    Each parameter has errors. del(ZT)/ZT = 2 del(alpha)/alpha + \
                    del(sigma)/sigma - del(kappa)/kappa + del(T)/T. Each del(f)/f might be smaller than 0.5%.\
                    Since each parameters are independently digitized, the total error in ZT, del(ZT)/ZT would be\
                    del(ZT)/ZT < sqrt(4+1+1+1) del(f)/f = 2.65 del(f)/f = 1.33%. \
                    Since the highest known ZT value is ~3.1, del(ZT) < 3.1 x del(ZT)/ZT < 0.04.\
                    Considering k=2 (approx. ~95% confidence interval), the ZT digitization error will be 0.08 for most cases.")
        st.subheader(":red[Data Error filtering]")
        st.markdown("However, during digitization, we face poorresolution, data overlap, which can cause a larger error.\
                    In addition to that, an unwanted publicatoin error of ZT inconsistency may cause an error. \
                    This issue can be seen by the Q-Q plot in the first and second tabs in this teMatDb APP.\
                    In this reason, we recommend to use filtered dataset using slidebar inputs in the left side.\
                    The suggested filer value is about 0.1.\
                    ")
        st.subheader(":red[Error Measure between ZT from figure and ZT from TEP digitized]")
        st.markdown("We define three major error values against measurement temperature mismatch, \
                    ZT extrapolation, ZT interpolation.")

def show_theory():        
    st.header(":blue[Theory]")
    with st.expander("See details.."):
        st.subheader(":red[Introduction to Thermoelectricity]")
        st.subheader(":red[Thermoelectric Transport]")
        st.subheader(":red[Thermoelectric Materials]")
        st.subheader(":red[Thermoelectric Device and Modules for Power Generation]")
        st.subheader(":red[Thermoelectric Efficiency]")  
    
    st.header(":blue[Advanced Efficiency Theory and Calculations]")
    with st.expander("See details.."):
        st.subheader(":red[Thermoelectric Conversion Efficiency with Temperature-dependent Thermoelectric Properties]")
        st.subheader(":red[Thermoelectric Differential Equations]")
        st.subheader(":red[Single Parameter Theory I: ZT in Constant-Property Model]")
        st.subheader(":red[Single Parameter Theory II: ZT in Constant-Seebeck coefficient Model]")
        st.subheader(":red[Three Thermoelectric Degrees of Freedom]")
        st.subheader(":red[Thermoelectric Inegtral Equations in the One-dimensional (1-D)]")
        st.subheader(":red[Thermoelectric Efficiency Solving Algorithm]")
        st.subheader(":red[Efficiency Solver: pykeri 2019]")
        st.subheader(":red[High-dimensional analysis: Optimal Leg Aspect Ratio]")
        st.subheader(":red[Dimensional Mapping to 1-D]")

    st.header(":blue[Advanced Device Design Theory]")
    with st.expander("See details.."):
        st.subheader(":red[Thermoelectric Algebra]")
        st.subheader(":red[Thermoelectric Inequality]")
        st.subheader(":red[Thermoelectric Circuit Model]")
        st.subheader(":red[Contact Resistances]")
        
    st.header(":blue[Thermoelectric Efficiency Map]")
    with st.expander("See details.."):
        st.subheader(":red[Best Thermoelectric Efficiency of Ever-Explored Materials], as of 2021-Nov-24")
        
        
def show_reference():    
    st.header(":blue[References]")
    # st.markdown("[1] Chung, Jaywan, and Byungki Ryu. “Nonlocal Problems Arising in Thermoelectrics.” Mathematical Problems in Engineering 2014 (December 15, 2014): e909078. https://doi.org/10.1155/2014/909078.")
    st.markdown("[1] Ryu, Byungki, Jaywan Chung, Eun-Ae Choi, Pawel Ziolkowski, Eckhard Müller, and SuDong Park. “Counterintuitive Example on Relation between ZT and Thermoelectric Efficiency.” Applied Physics Letters 116, no. 19 (May 13, 2020): 193903. https://doi.org/10.1063/5.0003749.")
    st.markdown("[2] Chung, Jaywan, Byungki Ryu, and SuDong Park. “Dimension Reduction of Thermoelectric Properties Using Barycentric Polynomial Interpolation at Chebyshev Nodes.” Scientific Reports 10, no. 1 (August 10, 2020): 13456. https://doi.org/10.1038/s41598-020-70320-7.")
    st.markdown("[3] Ryu, Byungki, Jaywan Chung, and SuDong Park. “Thermoelectric Degrees of Freedom Determining Thermoelectric Efficiency.” iScience 24, no. 9 (September 24, 2021): 102934. https://doi.org/10.1016/j.isci.2021.102934.")
    st.markdown("[4] Chung, Jaywan, Byungki Ryu, and Hyowon Seo. “Unique Temperature Distribution and Explicit Efficiency Formula for One-Dimensional Thermoelectric Generators under Constant Seebeck Coefficients.” Nonlinear Analysis: Real World Applications 68 (December 1, 2022): 103649. https://doi.org/10.1016/j.nonrwa.2022.103649.")
    st.markdown("[5] Ryu, Byungki, Jaywan Chung, Masaya Kumagai, Tomoya Mato, Yuki Ando, Sakiko Gunji, Atsumi Tanaka, et al. “Best Thermoelectric Efficiency of Ever-Explored Materials.” iScience 26, no. 4 (April 21, 2023): 106494. https://doi.org/10.1016/j.isci.2023.106494.")
    st.markdown("[6] Ryu, Byungki, Jaywan Chung, and SuDong Park. “(arXiv) Thermoelectric Algebra Made Simple for Thermoelectric Generator Module Performance Prediction under Constant Seebeck-Coefficient Approximation.” arXiv, October 8, 2024. https://doi.org/10.48550/arXiv.2410.04405.")
    st.markdown("[7] Ryu, Byungki, Seunghyun Oh, Wabi Demeke, Jaywan Chung, Jongho Park, Nirma Kumari, Aadil Fayaz Wani, Seunghwa Ryu, and SuDong Park. “(arXiv) Wiedemann-Franz Law and Thermoelectric Inequalities: Effective ZT and Single-Leg Efficiency Overestimation.” arXiv, November 4, 2024. https://doi.org/10.48550/arXiv.2411.01635.")
    st.write("(Style: Chicago Manual of Style 17th edition (full note))")
     
    return True


if __name__=="__main__":
    tempstring = "this is the tab printer contents."
    print( tempstring)