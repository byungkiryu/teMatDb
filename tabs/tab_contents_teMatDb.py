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
    
        
    ##################
    ##################
    ##################
    img_path = os.path.join(HERE, "..", "FIGURES",
                            "FIG_1_representative_teMatDb_vs_Starrydata2",
                            "figure.png")
    st.image( img_path )
    st.subheader(":green[Fig. 1 Thermoelectric data base, teMatDb]")           
    st.markdown("""
                (a-d) Seebeck coeffciient, electrical resistivity, thermal conductivity, and ZT
                with temperatures for cleaned :red[teMatDb272] against starryz10840.
                    """) 
    
    
    
    ##################
    ##################
    ##################
    img_path = os.path.join(HERE, "../", "FIGURES",
                            "FIG_2_total_TEP_TO_ERROR_sampleid43", 
                            "figure.png")
    st.image( img_path )
    st.subheader(":green[Fig. 2 TEP digitization and ZT error] ")    
    st.markdown(r"""
                :red[ZT error case: Data bia error itself in sample_id=43]         
                (a-d) Seebeck coeffciient, electrical resistivity, thermal conductivity, and ZT.            
                (e) $\delta$(ZT) with temperature and (f) theoretical quantiles.
                """) 
                
    with st.expander("See error cases", expanded=False):    
        
        img_path = os.path.join(HERE, "..", "FIGURES",
                                "FIG_2s_total_TEP_TO_ERROR_sampleid95", 
                                "figure.png")
        st.image( img_path )   
        st.markdown(r"""
                    :red[ZT error case: Data bia error itself in sample_id=95]         
                    (a-d) Seebeck coeffciient, electrical resistivity, thermal conductivity, and ZT.            
                    (e) $\delta$(ZT) with temperature and (f) theoretical quantiles.
                    """) 
        
        img_path = os.path.join(HERE, "..", "FIGURES",
                                "FIG_2s_total_TEP_TO_ERROR_sampleid113", 
                                "figure.png")
        st.image( img_path )  
        st.markdown(r"""
                    :red[ZT error case: fitting-induced error in sample_id=113]    
                    (a-d) Seebeck coeffciient, electrical resistivity, thermal conductivity, and ZT.            
                    (e) $\delta$(ZT) with temperature and (f) theoretical quantiles.
                    """) 
        
        img_path = os.path.join(HERE, "..", "FIGURES",
                                "FIG_2s_total_TEP_TO_ERROR_sampleid300", 
                                "figure.png")
        st.image( img_path ) 
        st.markdown(r"""
                    :red[ZT error case: phase transformation and interpolation-induced error in sample_id=300]    
                    (a-d) Seebeck coeffciient, electrical resistivity, thermal conductivity, and ZT.     
                    (e) $\delta$(ZT) with temperature and (f) theoretical quantiles.
                    """) 
                
        img_path = os.path.join(HERE, "..", "FIGURES",
                                "FIG_2s_total_TEP_TO_ERROR_sampleid415", 
                                "figure.png")
        st.image( img_path ) 
        st.markdown(r""":red[ZT error case: data-bias error itself in sample_id=415]    
                    (a-d) Seebeck coeffciient, electrical resistivity, thermal conductivity, and ZT.     
                    (e) $\delta$(ZT) with temperature and (f) theoretical quantiles.
                    """) 
    
    # st.markdown("(a) Digitization and continuation for sample_id = 43.") 
    # st.markdown("(b) ZT-ZT plot, deviation, and its Q-Q plot") 
    
    ##################
    ##################
    ##################
    img_path = os.path.join(HERE, "..", "FIGURES",
                            "FIG_3", 
                            # "FIG_3_ZTerror_over_teMatDb", 
                            "figure.png")
    st.image( img_path )  
    st.subheader(":green[Fig. 3 ZT self-consistency between figures and TEPs] ")  
    st.markdown("""
                (a) Average ZT's ZT(figure)-ZT(TEP) plot before and after Sc-ZT filtering,     
                (b) Peak ZT's ZT(figure)-ZT(TEP) plot before and after Sc-ZT filtering Q-Q plot,     
                (c) before and (d) after Sc-ZT filtering
                """)
    
    
    ##################
    ##################
    ##################    
    img_path = os.path.join(HERE, "..",  "FIGURES",
                            "FIG_4_ScZT_filter_validation_w_starryz", 
                            "figure.png")
    st.image( img_path )
    st.subheader(":green[Fig. 4 Sc-ZT filter and Starrydata2]")  
    st.markdown("""
                (a) ZT distribution: Peak ZT (TEP) over Peak ZT (figure), 
                before/after applying Sc-ZT filter for Starrydata2 (250501) resulting in starryz15532.
                (b) Zoom-in for reliable ZT ranges
                """)
    
    ##################
    ##################
    ##################    
    img_path = os.path.join(HERE, "..", "FIGURES",
                            "FIG_5_TEP_TEP_plots_allTemp", 
                            "figure.png")
    st.image( img_path )
    st.subheader(":green[Fig. 5 TEP-TEP relations]")  
    st.markdown(r"""
                (a) $\alpha$ vs $\sigma$ with PF color and (b) with ZT color,    
                (c) $\kappa$ vs $\sigma$, 
                (d) $\kappa$ vs $\alpha$,    
                (e) ZT vs PF, 
                (f) ZT vs $\kappa$.
                """)

    
    # st.subheader(":green[Fig. 5 TEP distribution for teMatDb272]")  
    # st.markdown(r"$\alpha$, $\rho$, $\sigma$, Power factor, $\kappa$, $\rho\kappa$")    
    # st.subheader(":green[Fig. 6 TEP analysis]")  
    # st.markdown(r"""
    #             :red[Scheduled for Later Release].     
    #             Relation between TEPs and thermoelectric Lorenz number ($L_{\rm TE}$), and ZT, 
    #             where $L_{\rm TE}:=\frac{\rho \kappa}{T}$.
    #             """)
    with st.expander(":red[Scheduled for Later Release]", expanded=False):    
        
        img_path = os.path.join(HERE, "..", "FIGURES",
                                "FIG_5b_Lorenz_Stats_from_collocatedTEPs", 
                                "figure.png")
        st.image( img_path )   
        st.subheader(":green[Fig. 6 Lorenz number and TEP relations]")  
        st.markdown(r"""
                    :red[Thermoelectric Lorenz number (L$_{\rm TE}$) distribution]         
                    (a) Temperature dependent L$_{\rm TE}$(T),    
                    (b-d) TEPs versus L$_{\rm TE}$.
                    """) 
                    
                    
                    
        st.subheader(":green[Fig. 7 Application. Device performance prediction]") 
        st.markdown(r"""
                    :red[Scheduled for Later Release].         
                    Thermoelectric efficiency and power plot with $\Delta$T.
                    """)
     
    return True


