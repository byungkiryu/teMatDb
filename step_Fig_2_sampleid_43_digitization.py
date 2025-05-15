# -*- coding: utf-8 -*-
"""
Created on Fri May  9 18:28:07 2025

@author: byungkiryu
"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pykeri.byungkiryu import byungkiryu_util as br
formattedDate, yyyymmdd, HHMMSS = br.now_string()


if (1):

    path_tematdb272 = "./teMatDb_publication/teMatDb272_dataset_20250515/"

    file_samples = "teMatDb_samples.csv"
    file_rawTEPs = "teMatDb_rawTEPs.csv"
    file_collocatedTEPs = "teMatDb_collocatedTEPs.csv"    
    df_tematdb_samples           = pd.read_csv( path_tematdb272 +file_samples, )
    df_tematdb_rawTEPs           = pd.read_csv( path_tematdb272 +file_rawTEPs, )
    df_tematdb_colTEPs           = pd.read_csv( path_tematdb272 +file_collocatedTEPs, )
    df_tematdb_colTEPs['ZT'] = df_tematdb_colTEPs['ZT_author_declared']
    
    path_starryz11067 = "./../030 starrydata2505 ZT filter  -- 20250515 - simple teps/990_starry_publication/starryz10840/"
    
    file_samples = "starryz_samples.csv"
    file_rawTEPs = "starryz_rawTEPs.feather"
    file_collocatedTEPs = "starryz_collocatedTEPs.feather"   
    df_starryz_samples   = pd.read_csv( path_starryz11067+file_samples, )
    df_starryz_rawTEPs   = pd.read_feather( path_starryz11067+file_rawTEPs, )
    df_starryz_colTEPs   = pd.read_feather( path_starryz11067+file_collocatedTEPs, )   
    
    

def draw(df):
    T    = df[ df['tepname'] == tepname].Temperature
    TEP  = df[ df['tepname'] == tepname].tepvalue 
    ax.scatter( T, TEP * scale_tep, 
               alpha=alphas.pop(0), 
               color=colors.pop(0), 
               label=labels.pop(0), 
               # edgecolors='none',
               zorder = zorder.pop(0)
               )

def drawline(df):
    T    = df['Temperature']
    TEP  = df[tepname]
    ax.plot( T, TEP * scale_tep, 
               alpha=alphas.pop(0), 
               color=colors.pop(0), 
               label=labels.pop(0), 
               # edgecolors='none',
               zorder = zorder.pop(0),
               linewidth=linewidth 
               )    

def drawZT(df):
    T    = df[ df['tepname'] == tepname].Temperature
    TEP  = df[ df['tepname'] == tepname].tepvalue 
    ax.scatter( T, TEP * scale_tep, 
               alpha=alphas.pop(0), 
               color='C1', 
               label="ZT from figure", 
               # edgecolors='none',
               zorder = zorder.pop(0)
               )

def drawZTline(df):
    T    = df['Temperature']
    TEP  = df[tepname]
    ax.plot( T, TEP * scale_tep, 
               alpha=alphas.pop(0), 
               color='C2', 
               label=r"ZT from TEP, " + r"[$\alpha^2 T / (\rho  \kappa)$]"  , 
               # edgecolors='none',
               zorder = zorder.pop(0),
               linewidth=linewidth 
               )   

sample_id = 43
figure_path = "FIG_2_sampleid_43_digitization/"
figure_file = figure_path + f"figure_{formattedDate}"

figsize=(7,6)



fig, axs = plt.subplots(2,2, figsize=figsize )
ax1, ax2 = axs[0]
ax3, ax4 = axs[1]
labels0 = [f'sample_id ={sample_id}','TEP-interpolated']   
colors0 = ['C0','C0'] 
alphas0 = [1, 0.2]
zorder0 = [200, 100]
linewidth = 8

with open(figure_file+"_meta.txt", "w") as f:
    f.write(f"labels0: {labels0}\n")
    f.write(f"colors0: {colors0}\n")
    f.write(f"alphas0: {alphas0}\n")
    f.write(f"zorder0: {zorder0}\n")
    f.write(f"linewidth: {linewidth}\n")



df_rawTEPs = df_tematdb_rawTEPs[ df_tematdb_rawTEPs.sample_id == sample_id  ] 
df_colTEPs = df_tematdb_colTEPs[ df_tematdb_colTEPs.sample_id == sample_id  ] 



df1 = df_rawTEPs
df2 = df_colTEPs

if (1):    
    ax = ax4
    tepname = 'ZT'

    scale_tep = 1
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    drawZT(df1)
    drawZTline(df2)
    
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel('Figure of merit ZT')


if (1):    
    ax = ax1
    tepname = 'alpha'

    scale_tep = 1e6
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    drawline(df2)
    
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel(r'Seebeck coefficient [$\mu$V K$^{-1}$]')

    
if (1):    
    ax = ax2
    tepname = 'rho'

    scale_tep = 1e+5
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    drawline(df2)
    
    # ax.set_yscale('log')
    
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel(r'Electrical resistivity [m$\Omega$ cm]')
    
      
if (1):    
    ax = ax3
    tepname = 'kappa'

    scale_tep = 1
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    drawline(df2)
    
    # ax.set_yscale('log')
    
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel(r'Thermal conductivity [W m$^{-1}$ K$^{-1}$]')
    
    

ax1.set_title("(a)",loc='left')
ax2.set_title("(b)",loc='left')
ax3.set_title("(c)",loc='left')
ax4.set_title("(d)",loc='left')

for ax in [ax1,ax2,ax3,ax4]:
    ax.legend()
    ax.set_xlim(280, 620)

ax1.set_ylim(150,250)
ax2.set_ylim(1,3)
ax3.set_ylim(0.5,1.5)
ax4.set_ylim(0,1.4)


plt.tight_layout()
plt.show()


# import shutil

# figfile1 =  "FIG_1_representative_teMatDb_vs_Starrydata2/figure.png"
# figfile2 = f"FIG_1_representative_teMatDb_vs_Starrydata2/figure_{formattedDate}.png"

fig.savefig(figure_file+".png",dpi=300)
# shutil.copy(figfile1, figfile2) 

