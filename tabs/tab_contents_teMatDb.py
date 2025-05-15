# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""

import os
import streamlit as st



HERE = os.path.dirname(os.path.abspath(__file__))
report_path_teMatDb272 = "../teMatDb_publication/teMatDb272_dataset_20250515/z_teMatDb_report.txt"
REPORT_PATH_teMatDb272 = os.path.join(HERE, report_path_teMatDb272)



def show_report_teMatDb272():
    st.title(":red[teMatDb272]")   
    st.markdown("👉 [Download teMatDb272](https://github.com/byungkiryu/teMatDb/tree/main/teMatDb_publication)")
    st.header(":blue[DB publication]")           
    with st.expander("How to constructued?", expanded=False):            
        with open(REPORT_PATH_teMatDb272, "r", encoding="utf-8") as file:
            report_text = file.read()
        st.subheader(":red[Data construction infomation] (z_teMatDb_report.txt)")
        st.text(report_text)






def show_dataDistribution():
    dbpubs = 'teMatDb272 characteristics'
    st.header(":blue[TEP distribution]")    
    with st.expander("See data characteristics", expanded=True):    
        
        st.subheader(":green[Fig. 1 TEP and ZT distribution]")           
        img_path = os.path.join(HERE, "..", "FIG_1_representative_teMatDb_vs_Starrydata2", "figure_20250516_011802.png")
        st.image( img_path )
        st.markdown("""
                    (a-d) Seebeck coeffciient, electrical resistivity, thermal conductivity, and ZT
                    with temperatures for cleaned :red[teMatDb272] against starryz10840.
                    """) 
        
        st.subheader(":green[Fig. 2 TEP digitization and ZT error] ")    
        img_path = os.path.join(HERE, "..", "FIG_2_sampleid_43_digitization", "figure_20250516_031111.png")
        st.image( img_path )
        
        
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


