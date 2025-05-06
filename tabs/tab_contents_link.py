# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:24:07 2023

@author: cta4r

This is the program to visualize 

"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px

HERE = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(HERE, "map_info_dataframe.xlsx")

def show_main_link_hub():
    st.header(":blue[Main Link Hub]")
    st.markdown("""
                :red[Here are all the links to TES at KERI.]    
                Content: Main Link Hub github page - research, data, machine learning, simulators, and webpages.  
                Link: https://byungkiryu.github.io/link-home/
                """)
                
def show_network():
    st.subheader("Network")
    
    # df_map = pd.read_excel("./map/"+"map_info_dataframe.xlsx",sheet_name='test')    
    df_map = pd.read_excel(EXCEL_PATH, sheet_name="read")  
    hover_data = ['City', 'site', 'who', 'Collaboration']
    fig = px.scatter_mapbox(df_map, lat="latitude", lon="longitude", 
                            text = 'who',  
                            color = 'color',
                            # size = 'size',
                            hover_data = hover_data ,
                            # opacity = 0.5,
                            center = {'lat':35.190691,'lon':128.717674},
                            zoom=1)
    
    mapbox_stype = "open-street-map"
    # mapbox_stype = "dark"
    # mapbox_stype = "stamen-watercolor"
    fig.update_layout(mapbox_style=mapbox_stype)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)     
    return True


def show_link():        
    st.subheader(":blue[Thermoelectric Power Generator Web Simulator Lite ver.0.53a]")
    st.markdown("""
                Link-a, https://tes.keri.re.kr/   
                Link-b, https://github.com/jaywan-chung/teg-sim-lite/
                """)
    
    # st.subheader("Korea Electrotechnology Research Institute (KERI)")
    # st.write(":blue[https://www.keri.re.kr/]")
   
    st.subheader(":blue[Alloy Design DB (v0.33)]")
    st.markdown("""
                Link, https://byungkiryu-alloydesigndb-demo-v0-33-main-v0-33-u86ejf.streamlit.app/
                """)

    return True

def show_QR_code():
    st.header(":blue[QR Code]")
    
    with st.expander("Web QR link for teMatDb:", expanded=False):            
        st.image(os.path.join(HERE, "/../images/qrcode_tematdb.streamlit.app") )
        st.subheader("https://tematdb.streamlit.app/")     



if __name__=="__main__":
    df_map = pd.read_excel(EXCEL_PATH, sheet_name="read")  
    print( df_map)