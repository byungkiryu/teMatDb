# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""

import os
import pandas as pd
import streamlit as st




from pykeri.byungkiryu import byungkiryu_util as br


        
# from library.tematdb_util import get_Ts_TEPZT
# from library.tematdb_util import draw_mat_teps, tep_generator_from_excel_files
# from library.draw_ZT_errors_with_mat import draw_mat_ZT_errors, draw_ZT_error_correlation, draw3QQ, draw4QQ
# from library.dev_performance import set_singleleg_device, run_pykeri, draw_dev_perf

formattedDate, yyyymmdd, HHMMSS = br.now_string()


HERE = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(HERE, "map_info_dataframe.xlsx")
# IMAGE_PATH = os.path.join(HERE, "map_info_dataframe.xlsx")


def show_me():
    # st.header(":blue[I'm Byungki Ryu from KERI, Korea]")
    st.markdown("""
                :blue[I am Byungki Ryu] from ThermoElectric Science (TES) group at KERI, Changwon, Korea.
                Although many papers have  reported thermoelectric properties,
                the material space remains highly fragmented,
                making it difficult to develop a unified understanding of thermoelectric transport.
                As a theoretical physicist, I have been deeply motivated by this challenge.
                Over the past decade, I have worked to develop an ultra-high-quality database for thermoelectric materials.
                This effort has led to the creation of the self-consistent ZT filter and teMatDb, which have also
                been applied to the world's largest thermoelectric database, Starrydata2.
                The method and protocol behind this database and filtering approach will be publilhsed oon.
                The next step will be the development of a data structure for thermoelectric experimental data,
                under the name teMatDb_expt.
                 
                """)



def show_about():
    st.header(":blue[ThermoElectric Science Group (TES) at KERI]")
    # st.write("ThermoElectric Science Group at KERI, Korea")
    df_map = pd.read_excel(EXCEL_PATH, sheet_name="read")
    df_map_keri = df_map[0:1]
    st.map(df_map_keri, zoom=12)
    
    
    
    
    with st.expander("See Members:", expanded=True):   
        st.subheader("SuDong Park, Dr. (박수동)")
        st.markdown("- TE leader scientist,metallurigst")
        st.subheader("Byungki Ryu, Dr. (류병기) (2013.12~)")
        st.markdown("- Transdisciplinary Scientist, based on physics and theory")
        # st.markdown("- thermoelectrics: from materials to energy conversion devices, efficiency theory")
        # st.markdown("- defects in semiconductors, their interfaces; defect complexes in thermoelectrics")
        st.subheader("Jaywan Chung, Dr. (정재환)")
        st.markdown("- mathematics, PDE, heat equation, machine learning thermoelectric data, diffusion theory")
        st.subheader("Jongho Park, Mr. (박종호)")
        st.markdown("- TE module fabrications, characterization")
        st.subheader("JiHui Son, Ms. (손지희)")
        st.markdown("- BiTe, materials synthesis, TE data structure")
        st.subheader("Jeongin Jang, Miss (장정인)")
        st.markdown("- BiTe, Higher-manganese silicide (HMS), materials synthesis")
        st.subheader("Seunghyun Oh, Miss (오승현) (2023.~")
        st.markdown("- Thermoelectric energy circuits, FEM simulations")
        st.subheader("Nirma Kumari, Post-doc. (2024.10~)")
        st.markdown("- Thermoelectric materials, leg measurements")
        st.subheader("Aadil Fayaz Wani, Post-doc. (2024.10~)")
        st.markdown("- First-principles, Thermoelectric transport calcualtions, interface design")
    with st.expander("See Alumni Members:", expanded=True):   
        st.subheader("Jae Ki Lee, Dr. (이재기, postdoc)")
        st.subheader("Min-Ho Lee, Dr. (이민호, postdoc)")
        st.subheader("Sungjin Park, Dr. (박성진, postdoc)")
    with st.expander("International Visitors:", expanded=True):   
        st.subheader("Johannes de Boor, Prof. Dr., ")    
        st.markdown("- from German Aerospace Center (DLR), Germany // 2024-Nov-24 to 2024-Dec-10")    
        
    st.header(":blue[Visit KERI. How to Come?]")


    with st.expander("See Maps:", expanded=False):        
        # HERE2 = "./"
        st.markdown("")
        st.image(os.path.join(HERE, "../images/southkorea_map_screenshot.png")   ) 
        st.caption("(South Korea Map) Changwon-si")
        # st.image(HERE2+"../images/changwon_map_screenshot.png")    
        # st.caption("(Changwon Map) Korea Electrotechnology Research Institute (KERI)")
        # st.image(HERE2+"../images/map_2023.jpg")   
        # st.caption("(KERI map) Office and Lab, building #3 and #5")
        # st.markdown("")
        # st.image(HERE+"./../images/southkorea_map_screenshot.png")    
        # st.caption("(South Korea Map) Changwon-si")
        # st.image(HERE+"/../images/changwon_map_screenshot.png")    
        # st.caption("(Changwon Map) Korea Electrotechnology Research Institute (KERI)")
        # st.image(HERE+"/../images/map_2023.jpg")   
        # st.caption("(KERI map) Office and Lab, building #3 and #5")    
    st.header(":blue[QR Code]")
    # with st.expander("See QR code (v1.1.1):", expanded=False):            
    #     st.image(HERE+"/../images/qrcode_tematdb-v1-1-main-v1-1-1-abc.streamlit.app.png")
    #     st.subheader("https://tematdb-v1-1-main-v1-1-1-abc.streamlit.app/")
    # with st.expander("See QR code (v1.1.0):", expanded=False):            
    #     # st.image(HERE+"qrcode_tematdb-v1-1-main-v1-1-0-abc.streamlit.app.png")
    #     st.subheader("https://tematdb-v1-1-main-v1-1-0-abc.streamlit.app/")
    # with st.expander("See QR code (v1.0.2):", expanded=False):            
    #     st.image(HERE+"qrcode_tematdb-v1-0-0-main-v1-0-2-abc.streamlit.app.png")
    #     # st.header("https://qrco.de/bds6GG/")
    # with st.expander("See QR code (v1.0.1):", expanded=False):            
    #     st.image("./image/"+"qrcode_tematdb-v1-0-0-main-v1-0-1-abc.streamlit.app.png")
    #     # st.header("https://qrco.de/bds6GG/")
    # with st.expander("See QR code (v1.0.0):", expanded=False):            
    #     st.image("./image/"+"qrcode_tematdb-v1-0-0-main-v1-0-0-abc.streamlit.app.png")
     
    return True


if __name__=="__main__":
    df_map = pd.read_excel(EXCEL_PATH, sheet_name="read")  
    print( df_map)