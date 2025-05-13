# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""


import math
import numpy as np
import pandas as pd
import streamlit as st

from matplotlib import pyplot as plt
import scipy.stats as stats  

from datetime import datetime
 
from pykeri.scidata.matprop import MatProp
from pykeri.thermoelectrics.TEProp import TEProp
from pykeri.thermoelectrics.TEProp_xls import TEProp as TEProp_xls
from pykeri.thermoelectrics.TEProp_df import TEProp as TEProp_df
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.environment import Environment
from pykeri.thermoelectrics.solver1d.device import Device

from pykeri.byungkiryu import byungkiryu_util as br


        
# from library.tematdb_util import get_Ts_TEPZT
from library.tematdb_util import draw_mat_teps, tep_generator_from_excel_files
from library.draw_ZT_errors_with_mat import draw_mat_ZT_errors, draw_ZT_error_correlation, draw3QQ, draw4QQ
# from library.draw_ZT_errors_with_mat import draw_mat_ZT_errors, , draw3QQ, draw4QQ
from library.dev_performance import set_singleleg_device, run_pykeri, draw_dev_perf

formattedDate, yyyymmdd, HHMMSS = br.now_string()

 
# @st.cache_data
def load_csv(filepath):
    return pd.read_csv(filepath)

# @st.cache_data
def load_excel(filepath,sheet_name):
    return pd.read_excel(filepath,sheet_name=sheet_name)

# @st.cache_data
def load_feather(filepath):
    return pd.read_feather(filepath)



# @st.cache_data
# def load_map():
    # return pd.read_excel("./map/"+"map_info_dataframe.xlsx",sheet_name='test')  



st.set_page_config(page_title="teMatDb v1.1.6")

st.title("teMatDb")
st.subheader(":blue[t]hermo:blue[e]lectric :blue[Mat]erial :blue[D]ata:blue[b]ase")
st.markdown("""
            - High quality thermoelectric database, teMatDb (ver1.1.6)
            - That can be used for data analytics, machine learning and AI
            """)


tab_1_tep, tab_2_scZT, tab_dataDist, tab_theory, tab_link, tab_about = st.tabs(["Material Property", 
                                                 "Data Self-Consistency", 
                                                 "Data Distribution",
                                                 "Theory", 
                                                 "Link", 
                                                 "About"])


import tabs.tab_contents_datadistribution as tab_contents_datadistribution
import tabs.tab_contents_theory as tab_contents_theory
import tabs.tab_contents_link as tab_contents_link
import tabs.tab_contents_about as tab_contents_about


with tab_dataDist:  
    # Regarding Data info
    tab_contents_datadistribution.show_dataDistribution()
    
with tab_theory:
    # Regarding theory
    tab_contents_theory.show_data_description()
    tab_contents_theory.show_theory()
    tab_contents_theory.show_reference()

with tab_link:
#     # Regarding link
    tab_contents_link.show_main_link_hub()
#     tab_contents_link.show_network()
    tab_contents_link.show_link()
    tab_contents_link.show_QR_code()
    
with tab_about:   
    # Regarding KERI Info
    tab_contents_about.show_me()
    tab_contents_about.show_about()

     



###############
###############
###############
## Sidebar, choose DB, choose mat

## db info
dbname = 'tematdb'
dbversion = "v1.1.6"

## DIR setting
DIR_00_tematdb_raw_excel         =  "./data_00_tematdb_raw_excel/"
DIR_10_tematdb_converted_to_csv  =  "./data_10_tematdb_csv_converted/"
DIR_30_tematdb_extTEP_csv        =  "./data_30_tematdb_extTEP_csv/"
DIR_40_tematdb_ZT_error          =  "./data_40_tematdb_ZT_error/"

file_tematdb_metadata_excel   =  "./" + "_tematdb_metadata_v1.1.6-20250224.xlsx"
file_tematdb_db_csv         =  DIR_10_tematdb_converted_to_csv + "tematdb_v1.1.6_completeTEPset.csv"
file_tematdb_db_extZT_csv   =  DIR_30_tematdb_extTEP_csv       + "tematdb_v1.1.6_extendedZTset_dT2K.csv"
file_tematdb_error_csv      =  DIR_40_tematdb_ZT_error         + "ZT_error.csv"

df_tematdb_meta             = load_excel( file_tematdb_metadata_excel, 'list')
df_tematdb_csv              = load_csv(file_tematdb_db_csv)
df_tematdb_extended_csv     = load_csv( file_tematdb_db_extZT_csv )
df_tematdb_ZTerr            = load_csv( file_tematdb_error_csv )

df_tematdb_csv["tepvalue"]  = df_tematdb_csv["tepvalue"].apply(lambda x: f"{x:.6e}")



 
with st.sidebar:
    st.subheader(":red[Select TE Mat. DB]")
    display_options =['teMatDb','teMatDb_expt (disabled)','Starrydata (disabled)']
    real_options    =['teMatDb','disabled','disabled']
    
    selected_db_label  = st.radio( 'Select :red[Thermoelectric DB] :',
        options=display_options, 
        index=0,
        label_visibility="collapsed")    
    
    db_mode = real_options[display_options.index(selected_db_label)]
    
    
    if db_mode == 'disabled':
        st.warning("⚠️ `teMatDb_expt` is currently not available.")
        st.warning("⚠️ 'Starrydata2' works only in local environments: using [main2_local_version.py].")
        st.stop()  # 선택되었을 경우 이후 코드 실행 방지
    if db_mode == 'Starrydata2':
        st.warning("⚠️ 'Starrydata2' works only in local environments. "
                   "Due to file size limitations, it cannot be loaded in Streamlit Cloud. "
                   "If needed, you can contact me to download the required files from a private link (to be announced).")
        confirm_run = st.checkbox("I understand the above and wish to proceed with loading Starrydata2.", value=False)
        if not confirm_run:
            st.stop()
        
    
    if (db_mode == 'teMatDb'):
        
        # df_tematdb_meta = pd.read_excel("./"+file_tematdb_metadata_excel, sheet_name='list', )
        # df_tematdb_meta["label_of_targetZT_in_figure"] = df_tematdb_meta["label_of_targetZT_in_figure"].astype(str)
        df_db_meta = df_tematdb_meta        
        df_db_meta.index = list(df_db_meta.sample_id.copy())
        
        df_db_csv = df_tematdb_csv
        
        df_db_extended_csv = df_tematdb_extended_csv.copy()
        df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_autoTcTh_range ]
        df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_ZT_author_declared ] 
        
        err_cols = ['sample_id','JOURNAL', 'YEAR', 
               'Corresponding_author_main', 'Corresponding_author_institute',
               'Corresponding_author_email', 'figure_number_of_targetZT',
               'label_of_targetZT_in_figure', 'figure_label_description',]
        df_db_error0 = df_tematdb_ZTerr
        df_db_error = pd.merge( df_db_error0, df_db_meta[err_cols], on='sample_id', how='left')
        df_db_error.index = list(df_db_error.sample_id.copy())        
         
        ## choose sampleid
        st.subheader(":red[Select sample_id]")
        option_sample_id = list(df_db_meta['sample_id'].unique())
        sample_id = st.selectbox('Select or type sample_id:',
            option_sample_id, index=0,
            label_visibility="collapsed")   
        
        df_db_meta_sample_id = df_db_meta[ df_db_meta['sample_id'] == sample_id]
        doi = df_db_meta_sample_id.DOI.iloc[0]
        doiaddress  = 'http://www.doi.org/{}'.format(doi)
        link_doi    = '[DOI: {}](http://www.doi.org/{})'.format(doi,doi)
        st.markdown(link_doi, unsafe_allow_html=True)
        st.code(doiaddress)
        corrauthor     = df_db_meta_sample_id.Corresponding_author_main.iloc[0]
        corrinstitute  = df_db_meta_sample_id.Corresponding_author_institute.iloc[0] 
        corremail      = df_db_meta_sample_id.Corresponding_author_email.iloc[0] 
        # st.markdown("First Author: :red[need to update]")
        st.markdown("Correspondence: {}".format(corrauthor)) 
        st.markdown("Institute: {}".format(corrinstitute))         
        
        interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
                      MatProp.OPT_EXTEND_LEFT_TO:1,          # ok to 0 Kelvin
                      MatProp.OPT_EXTEND_RIGHT_BY:2000}        # ok to +50 Kelvin from the raw data
        TF_mat_complete, mat = tep_generator_from_excel_files(sample_id, interp_opt)
    
        label_db = "DB: {}".format(db_mode)
        label_sample_id = "sample_id: {}".format(sample_id)
        label_doi = '[DOI: {}]'.format(doi)    
        
        st.subheader(":red[Data Filter]")
 
    elif (db_mode == 'Starrydata2'):
        
        prefix = "20250210_rawdata"
        
        # PATH_metadata = "../030 starrydata2502 to csv and filter  -- 20250210"
        PATh_starry   = "../030 starrydata2502 to csv and filter  -- 20250506/"
        # PATH_metadata = "../030 starrydata2502 to csv and filter  -- 20250506"
        PATH_metadata = PATh_starry + "/999_Starrydata2_rawdata_meta/"
        PATH_metadata = PATH_metadata +"_Starrydata2_20250201_rawdata_meta_ZTfilterable_.xlsx"
        df_starry_meta0 = load_excel(PATH_metadata, sheet_name='20250201_rawdata', )       
        df_db_meta = df_starry_meta0
        df_db_meta.index = list(df_db_meta.sample_id.copy())
        df_db_meta['TF_mat_complete'] = df_db_meta['pykeri_TEPZT_readable']
        df_db_meta['doi'] = df_db_meta['DOI']
        
        PATH_tep_feather  = PATh_starry+"100_teps/"
        df_alpha0 = load_feather(PATH_tep_feather+"20250201_rawdata_alpha.feather")
        df_rho0   = load_feather(PATH_tep_feather+"20250201_rawdata_rho.feather")
        df_kappa0 = load_feather(PATH_tep_feather+"20250201_rawdata_kappa.feather")
        df_ZT0    = load_feather(PATH_tep_feather+"20250201_rawdata_ZT.feather")

        for df in [df_alpha0, df_rho0, df_kappa0, df_ZT0]:
            if 'temperature' in df.columns:
                df['Temperature'] = df['temperature']

        
        df_db_csv = pd.concat( [df_alpha0, df_rho0, df_kappa0, df_ZT0], ignore_index=True)
        
        
        PATH_exTEP = PATh_starry+"300_extended_teps/"
        PATH_exTEP = PATH_exTEP  +"extendedZTset_2K.feather"
        # PATH_exTEP = PATH_exTEP  +"extendedTEPset_2K__20250506_180300.feather"
        df_db_extended_csv = load_feather(PATH_exTEP )
        df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_autoTcTh_range ]
        df_db_extended_csv = df_db_extended_csv[ df_db_extended_csv.is_Temp_in_ZT_author_declared ] 
        
        
        file_tematdb_error_csv = PATh_starry+"400_ZT_error/"
        file_tematdb_error_csv = file_tematdb_error_csv+"ZT_error_table.csv"
        df_db_error0 = pd.read_csv(file_tematdb_error_csv)
        df_db_error = pd.merge( df_db_error0, df_db_meta, on='sample_id', how='left')
        df_db_error.index = list(df_db_error.sample_id.copy())        
        
         
        ## choose sampleid
        st.subheader(":red[Select sample_id]")
        option_sample_id = list(df_db_meta['sample_id'].unique())
        sample_id = st.selectbox('Select or type sample_id:',
            option_sample_id, index=3,
            label_visibility="collapsed")   
        
        df_db_meta_sample_id = df_db_meta[ df_db_meta['sample_id'] == sample_id] 
        doi = df_db_meta_sample_id.DOI.iloc[0]
        doiaddress = 'http://www.doi.org/{}'.format(doi)
        link_doi = '[DOI: {}](http://www.doi.org/{})'.format(doi,doi)
        st.markdown(link_doi, unsafe_allow_html=True)
        st.code(doiaddress)
        # corrauthor = df_db_meta_sampleid.Corresponding_author_main.iloc[0]
        # corrinstitute  = df_db_meta_sampleid.Corresponding_author_institute.iloc[0] 
        # corremail  = df_db_meta_sampleid.Corresponding_author_email.iloc[0] 
        # st.markdown("First Author: :red[need to update]")
        # st.markdown("Correspondence: {}".format(corrauthor)) 
        # st.markdown("Institute: {}".format(corrinstitute))         
        
        df_alpha_sample_id = df_alpha0[ df_alpha0.sample_id == sample_id]
        df_rho_sample_id   = df_rho0[   df_rho0.sample_id == sample_id]
        df_kappa_sample_id = df_kappa0[ df_kappa0.sample_id == sample_id]
        df_ZT_sample_id    = df_ZT0[    df_ZT0.sample_id == sample_id]
        

        
        interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
                      MatProp.OPT_EXTEND_LEFT_TO:1,          # ok to 0 Kelvin
                      MatProp.OPT_EXTEND_RIGHT_BY:2000}        # ok to +50 Kelvin from the raw data

        mat_name = "Starrydata2_{}_{}".format(prefix,sample_id)            
        def get_mat_tep(df_alpha_sample_id, df_rho_sample_id, df_kappa_sample_id, df_ZT_sample_id, mat_name):
            # mat = False
            # TF_mat_complete = False            
            
            try:
                mat = TEProp_df.load_from_df(df_alpha_sample_id, 
                                             df_rho_sample_id, 
                                             df_kappa_sample_id, 
                                             df_ZT_sample_id, mat_name=mat_name)
                mat.set_interp_opt(interp_opt)
                TF_mat_complete = True
                # return TF_mat_complete, mat
            except:
                mat = False
                TF_mat_complete = False
                # return TF_mat_complete, mat
            return TF_mat_complete, mat
  
          
        TF_mat_complete, mat = get_mat_tep(df_alpha_sample_id, 
                                           df_rho_sample_id, 
                                           df_kappa_sample_id, 
                                           df_ZT_sample_id, 
                                           mat_name)

    
        label_db = "DB: {}".format(db_mode)
        label_sample_id = "sample_id: {}".format(sample_id)
        label_doi = '[DOI: {}]'.format(doi)     
        
        st.subheader(":red[Data Filter]")
    else:
        pass
    
    with st.form("Data Error Filter Criteria"):
        st.markdown("Inconsistent TEP data with respect to ZT will be filtered out. (Min. value: 0.02)")
        cri_cols = ['d_avgZT', 
                    'd_peakZT',
                    'errdZT_Linf', 'errdZT_L2',
                    'errdZT_Linf_over_avg_ZT_ofTEPEval',
                    'errdZT_Linf_over_peak_ZT_ofTEPEval'
                    ]
        cri_vals_def = [0.10, 0.10, 0.10, 0.10, 0.20, 0.20]
        cri_vals0 = st.number_input('Crit0: (Avg ZT) err. {} > N'.format(cri_cols[0]),
                                      min_value = 0.02, value=cri_vals_def[0],step=0.05)
        cri_vals1 = st.number_input('Crit1: (Peak ZT) err: {} > N'.format(cri_cols[1]),
                                      min_value = 0.02, value=cri_vals_def[1],step=0.05)
        cri_vals2 = st.number_input('Crit2: Max (ZT err): {} > N'.format(cri_cols[2]),
                                      min_value = 0.02, value=cri_vals_def[2],step=0.05)        
        cri_vals3 = st.number_input('Crit3: L2 (ZT err, std): {} > N'.format(cri_cols[3]),
                                      min_value = 0.02, value=cri_vals_def[3],step=0.05)  
        cri_vals4 = st.number_input('Crit4: Max (ZT err)/(avg ZT): {} > N'.format(cri_cols[4]),
                                      min_value = 0.02, value=cri_vals_def[4],step=0.05) 
        cri_vals5 = st.number_input('Crit5: Max (ZT err)/(peak ZT): {} > N'.format(cri_cols[5]),
                                      min_value = 0.02, value=cri_vals_def[5],step=0.05)  
        
        submitted = st.form_submit_button("Submit Criterias.")
        
        if submitted:                   
            cri_vals = [cri_vals0, cri_vals1, 
                        cri_vals2, cri_vals3, 
                        cri_vals4, cri_vals5,
                        ]
        else:
            cri_vals = cri_vals_def



###############
###############
###############
## Material data for given sampleid
with tab_1_tep:  
    ## Read mat, TEP
    # st.header("[db_mode  = :blue[{}]]".format(db_mode) )
    st.header(":blue[I. DB MetaData Table]")
    with st.expander("See material metadata:", expanded=True):
        st.write(df_db_meta)  
        # st.dataframe(df_db_meta)     

    st.header(":blue[II. Material Data] ")
    st.subheader(":red[[db_mode  = :blue[{}]]]".format(db_mode) + ":red[[sample_id = :blue[{}]]]".format( sample_id))
    
    st.subheader(":red[Material Summary]")
    st.markdown(link_doi, unsafe_allow_html=True)
    
    if (db_mode == 'teMatDb'):
        colnames = ['sample_id', 'DOI', 'JOURNAL', 'YEAR',
                    'GROUP', 'BASEMAT','Composition_by_element', 'Composition_detailed',
                    'mat_dimension(bulk, film, 1D, 2D)', 'SC/PC', 'Reaction', 'Milling',
                    'SINTERING', 'PostProcessing']
        for colname in colnames:
            st.markdown("{}: :blue[{}]".format(colname, df_db_meta_sample_id[colname].iloc[0]))

    if (db_mode == 'Starrydata2'):
        colnames = ['db',
                    'dbversion', 
                    'sample_id', 'SID', 'DOI', 
                    # 'year',
                    'published',
                    # 'db', 
 
                    'composition',
                    # 'df_tep4_sampleids','df_eta4_sampleids','df_tep_extended_sampleids'
                    ]
        for colname in colnames:
            st.markdown("{}: :blue[{}]".format(colname, df_db_meta_sample_id[colname].iloc[0])) 
    
    st.markdown('TF_mat_complete: :blue[{}]'.format(TF_mat_complete) )
    
    st.subheader(":red[Material Information]")
    st.write(df_db_meta_sample_id)

 
    ## print material(mat) tep
    st.subheader(":red[Transport Properties] (Table)")
    df_db_csv_sample_id = df_db_csv[ df_db_csv['sample_id'] == sample_id]
    if not TF_mat_complete:
        st.write(':red[TEP is invalid because TEP set is incomplete..]')    
    if TF_mat_complete:
        with st.expander("See rawdata of material TEPs:"): 
            st.write(df_db_csv_sample_id)
    
    ## draw material(mat) tep
    st.subheader(":red[Transport Properties] (interpolated) (Figure)")
    if not TF_mat_complete:
        st.write(':red[TEP is invalid because TEP set is incomplete..]')    
    if TF_mat_complete:        
        fig1, fig2 = draw_mat_teps(mat, 
                                   label_db=label_db, 
                                   label_sample_id=label_sample_id, 
                                   label_doi=label_doi
                                   )
        with st.expander("See TEP curves:", expanded=True):        
            st.pyplot(fig1)   
            st.caption("Figure. Thermoelectric Properties of :blue[sample_id={}] in :blue[{}].".format(sample_id,db_mode))
        with st.expander("See rho, PF, RK, Loenz curves:", expanded=True):        
            st.pyplot(fig2)        
            st.caption("Figure. Extended Thermoelectric Properties of :blue[sample_id={}] in :blue[{}].".format(sample_id,db_mode))
        with st.expander("See Interpolation schemes:", expanded=False):  
            ZT_raw   = np.array( mat.ZT.raw_data() ).T
            autoTc = mat.min_raw_T
            autoTh = mat.max_raw_T    
            TcZT = min(ZT_raw[0])
            ThZT = max(ZT_raw[0])    
            TcTEPZT = max(autoTc, TcZT,1)
            ThTEPZT = min(autoTh, ThZT)            
            st.markdown(":blue[TEP interpolation interval (Tc, Th) = ({:6.2f} K, {:6.2f} K)]  \n".format(autoTc,autoTh) \
                        + ":red[ZT interpolation interval (Tc, Th) = ({:6.2f} K, {:6.2f} K)]  \n".format(TcZT,ThZT) \
                        + ":green[Union of TEP and ZT interpolation interval (Tc, Th) = ({:6.2f} K, {:6.2f} K)]".format(TcZT,ThZT))

        
    ## Digitized data quality using error analysis
    st.header(":blue[III. ZT Self-consistency Analyzer]")
    st.subheader(":red[[db_mode  = :blue[{}]]]".format(db_mode) + ":red[[sample_id = :blue[{}]]]".format( sample_id))
    st.subheader(":red[Material Error (or Noise) Statistics]")
    if not TF_mat_complete:
        st.write(':red[TEP is invalid because TEP set is incomplete..]')    
    if TF_mat_complete:   
        try:
            df_db_error_sample_id = df_db_error[ df_db_error['sample_id'] == sample_id]
        except:
            st.markdown('Yet, no error reports')
        else:            
            st.write(df_db_error_sample_id)
            
            if ( np.abs( df_db_error_sample_id.d_peakZT.iloc[0] ) > 0.1 ):
                st.markdown("**:red[Warning: peak ZT mismatch is larger than 0.1]**")
            else:
                st.markdown("**:blue[Self-consistent: peak ZT mismatch is smaller than, 0.1]**")
            st.markdown(":red[peak_ZT_ofRawFig (reported ZT from published figure data): peak_ZT_ofRawFig = {:6.2f}]".format(df_db_error_sample_id.peak_ZT_ofRawFig.iloc[0]))
            st.markdown(":red[peak_ZT_ofTEPEval (recalc ZT from TEPs): peak_ZT_ofTEPEval = {:6.2f}]".format(df_db_error_sample_id.peak_ZT_ofTEPEval.iloc[0])) 
                
            if ( np.abs( df_db_error_sample_id.d_avgZT.iloc[0] ) > 0.1 ):
                st.markdown("**:red[Warning: average ZT mismatch is larger than 0.1]**")
            else:
                st.markdown("**:blue[Self-consistent: average ZT mismatch is smaller than, 0.1]**")
            st.markdown(":red[avg_ZT_ofRawFig (reported ZT from published figure data): avg-ZT raw = {:6.2f}]".format(df_db_error_sample_id.avg_ZT_ofRawFig.iloc[0]))
            st.markdown(":red[avg_ZT_ofTEPEval avg-ZT reevaulated (recalc ZT from TEPs): avg-ZT TEP = {:6.2f}]".format(df_db_error_sample_id.avg_ZT_ofTEPEval.iloc[0])) 
        
            with st.expander("How to calculateSee Lp errors and etc...:", expanded=False):        
                st.markdown(":red[error was calculated blah blbah using following equations (to be filled later)]")
                
            fig3 = draw_mat_ZT_errors(mat, label_db=label_db, label_sample_id=label_sample_id, label_doi=label_doi)
            st.pyplot(fig3)        
            st.caption("Figure. ZT error analysis of :blue[sample_id={}] in :blue[{}].".format(sample_id,db_mode))


          
    st.header(":blue[IV. Material Performance]")
    st.subheader(":red[[db_mode  = :blue[{}]]]".format(db_mode) + ":red[[sample_id = :blue[{}]]]".format( sample_id))
    if not TF_mat_complete:
        st.write(':red[TEP is invalid because TEP set is incomplete..]')    
    if TF_mat_complete:
        # st.write(':blue[TEP is valid..]')     
        
        # autoTc, autoTh = float(mat.min_raw_T), float(mat.max_raw_T)
        limitTc = float( math.floor(autoTc/50)*50.0 )
        limitTh = float( math.ceil(autoTh/50)*50.0 )
        
        st.markdown(":blue[TEP interpolation:] piecewise-linear manner.  \n "
                    +":blue[TEP extrapolation:] constant-extrapolated.  \n "    
                    +":blue[TEP interpolation at the interval (Tc, Th) = ({:6.2f} K, {:6.2f} K)]".format(autoTc,autoTh))
        
        
        st.subheader(":red[Singleleg Device Spec.]")
        with st.form("my_form"):
            st.write("Valid temperature range considering Ts of TEPs: Tc > {:6.2f} K, Th < {:6.2f} K".format(autoTc, autoTh))
            
            col1, col2 = st.columns([2,2])
            with col1:
                Tc = st.number_input(r'$T_c$: cold side temperature in [K]',
                                min_value = limitTc, max_value = limitTh, step = 25.0,
                                value = limitTc+25 )
                Th = st.number_input(r'$T_h$: hot side temperature in [K]',
                                min_value = limitTc, max_value = limitTh, step = 25.0,
                                value = limitTh-25 )
            with col2:
                leg_length_in_mm = st.number_input('leg_length in mm',
                                                     min_value = 0.5, max_value = 10.0, step = 0.5,
                                                     value = 3.0)
                leg_area_in_mmsq = st.number_input('leg_area in mm x mm',
                                                     min_value = 0.25, max_value = 25.0, step = 1.0,
                                                     value = 9.0)
                N_leg = st.number_input('number of legs',
                                                      min_value = 1, max_value = 1, step = 1,
                                                      value = 1, disabled=True)
            
            submitted = st.form_submit_button("Calculate Material Performance (singleleg device).")
            if submitted:                   
                leg_length = leg_length_in_mm *1e-3
                leg_area   = leg_area_in_mmsq *1e-6
                N_leg      = 1  
            else:
                leg_length = 3 *1e-3
                leg_area   = 9 *1e-6
                N_leg      = 1 

        dev = set_singleleg_device(mat, leg_length,leg_area,N_leg,Th,Tc)            
        # dev = set_singleleg_device(df_db_csv,sampleid,leg_length,leg_area,N_leg,Th,Tc)
        df_dev_run_currents_result, df_dev_run_powMax_result, df_dev_run_etaOpt_result = run_pykeri(dev, sample_id,leg_length,leg_area,N_leg,Th,Tc)
        fig4 = draw_dev_perf(df_dev_run_currents_result, df_dev_run_powMax_result, df_dev_run_etaOpt_result,
                             label_db, sample_id, label_doi)
        st.pyplot(fig4)
        with st.expander("See Material performance curves:", expanded=True):        
            st.write("currents performances")
            st.write(df_dev_run_currents_result)
            st.write("Power max performances")
            st.write(df_dev_run_powMax_result)
            st.write("Optimal efficiency performances")
            st.write(df_dev_run_etaOpt_result)
            
###############
############### 
###############
## DB Stat
with tab_2_scZT:     

    st.header(":blue[DataFrame for Error Table]")

    # st.write(df_db_error)
    st.dataframe(df_db_error)
    
    st.header(":blue[Error Analysis based on ZT self-consistency]")
    # with st.expander("See analysis:", expanded=True): 
        # cri_cols = ['davgZT', 'dpeakZT','Linf']
        # cri_vals = [0.10, 0.10, 0.10]
        
         
        
    df_db_error_criteria_list = []
    error_criteria_list = []
    sample_id_list_df_db_error_criteria = []
    df4_db_error_filtered = df_db_error.copy()
    df5_db_error_anomaly = df_db_error.copy()
    for cri_col, cri_val in zip(cri_cols, cri_vals):   
        error_criteria = np.abs( df_db_error[cri_col] ) > cri_val 
        error_criteria_list.append(error_criteria.copy())
        df_db_error_criteria = df_db_error[ error_criteria ].copy()
        df_db_error_criteria.sort_values(by=cri_col,ascending=False, inplace=True)
        df_db_error_criteria.set_index('sample_id', inplace=True, drop=False)
        
        df4_db_error_filtered = df4_db_error_filtered[ np.abs( df4_db_error_filtered[cri_col] ) <= cri_val ].copy()
        df5_db_error_anomaly  = df5_db_error_anomaly[ np.abs( df5_db_error_anomaly[cri_col] ) > cri_val ].copy()
        
        cri_str = ":red[Noisy samples: {} > {:.2f}]".format(cri_col, cri_val)
        st.subheader(cri_str)
        st.markdown("There are :red[{}] noisy-cases.".format(len(df_db_error_criteria)) )
        with st.expander("See error table for this criteria:", expanded=False): 
            
            st.write(df_db_error_criteria)
            df_db_error_criteria_list.append(df_db_error_criteria)
            sample_id_list = df_db_error_criteria['sample_id'].unique().tolist()
            st.write(sample_id_list)
            sample_id_list_df_db_error_criteria = sample_id_list_df_db_error_criteria + sample_id_list
        del df_db_error_criteria
    
    
    
    st.header(":blue[DB Before Filtering]")
    num_sample_ids_before_filtering = len( df_db_error[ df_db_error.TF_mat_complete ].sample_id.unique() )
    st.markdown("There are :blue[{}] sampleids.".format(num_sample_ids_before_filtering))
    with st.expander("See plots:", expanded=False):   
        df1 = df_db_extended_csv
        df2 = df_db_error        
        st.subheader(":red[ZT Error Correlation]")   
        draw_ZT_error_correlation(df2)        

    st.subheader(":red[QQ analysis]")
    # X = df1.ZT_author_declared - df1.ZT_tep_reevaluated
    fig_before_filter = draw3QQ(df1,df2,label_db, label_sample_id, label_doi)
    # fig_before_filter = draw4QQ(df1,df2,label_db, label_sampleid, label_doi)
    st.pyplot(fig_before_filter)

 

    st.header(":blue[DB After Filtering]")
    df4_db_error_filtered['notNoisy'] = True
    df3_df_db_extended_csv_filtered = pd.merge( df_db_extended_csv, df4_db_error_filtered[['sample_id','notNoisy']], on='sample_id', how='left')
    df3_df_db_extended_csv_filtered = df3_df_db_extended_csv_filtered[ df3_df_db_extended_csv_filtered.notNoisy == True ].copy()
    df3, df4 = df3_df_db_extended_csv_filtered, df4_db_error_filtered

    num_sampleids_after_filtering = len( df4[ df4.TF_mat_complete ].sample_id.unique() )
    st.markdown("There are :blue[{}] sample_ids.".format(num_sampleids_after_filtering))
    with st.expander("See plots:", expanded=False):           
        st.subheader(":red[ZT Error Correlation]")
        draw_ZT_error_correlation(df4)    
    st.subheader(":red[QQ analysis]")
    # X = df1.ZT_author_declared - df1.ZT_tep_reevaluated
    fig_after_filter = draw3QQ(df3,df4,label_db, label_sample_id, label_doi)
    # fig_after_filter = draw4QQ(df3,df4,label_db, label_sampleid, label_doi)
    st.pyplot(fig_after_filter)      
