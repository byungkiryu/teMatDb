# -*- coding: utf-8 -*-
"""
Created on Fri May  9 18:28:07 2025

@author: byungkiryu
"""

import pandas as pd
import numpy as np
from matplotlib import cm
from matplotlib import pyplot as plt
from pykeri.byungkiryu import byungkiryu_util as br
formattedDate, yyyymmdd, HHMMSS = br.now_string()


if (1):

    path_tematdb272 = "../teMatDb_publication/teMatDb272_dataset_20250515/"

    file_samples = "teMatDb_samples.csv"
    file_rawTEPs = "teMatDb_rawTEPs.csv"
    file_collocatedTEPs = "teMatDb_collocatedTEPs.csv"    
    df_tematdb_samples           = pd.read_csv( path_tematdb272 +file_samples, )
    df_tematdb_rawTEPs           = pd.read_csv( path_tematdb272 +file_rawTEPs, )
    df_tematdb_colTEPs           = pd.read_csv( path_tematdb272 +file_collocatedTEPs, )
    
    
    path_starryz11067 = "./../../030 starrydata2505 ZT filter  -- 20250517 - simple teps/990_starry_publication/starryz10840/"
    
    file_samples = "starryz_samples.csv"
    file_rawTEPs = "starryz_rawTEPs.feather"
    file_collocatedTEPs = "starryz_collocatedTEPs.feather"   
    df_starryz_samples   = pd.read_csv( path_starryz11067+file_samples, )
    df_starryz_rawTEPs   = pd.read_feather( path_starryz11067+file_rawTEPs, )
    df_starryz_colTEPs   = pd.read_feather( path_starryz11067+file_collocatedTEPs, )   
    
    

def draw(df):
    T   = df[ df['tepname'] == tepname].Temperature
    TEP  = df[ df['tepname'] == tepname].tepvalue 
    ax.scatter( T, TEP * scale_tep, 
               alpha=alphas.pop(0), 
               color=colors.pop(0), 
               label=labels.pop(0), 
               # edgecolors='none',
               zorder = zorder.pop(0)
               )
    


figsize=(7,7)



fig, axs = plt.subplots(2,2, figsize=figsize )
ax1, ax2 = axs[0]
ax3, ax4 = axs[1]
labels0 = ['teMatDb272','starryz10840']   
colors0 = ['C1','C0'] 
alphas0 = [0.5, 0.2]
# colors0 = [cm.coolwarm(0.9),cm.coolwarm(0.1)] 
# alphas0 = [.6, .5]
zorder0 = [200, 100]

with open(f"FIG_1_representative_teMatDb_vs_Starrydata2/figure_{formattedDate}_meta.txt", "w") as f:
    f.write(f"labels0: {labels0}\n")
    f.write(f"colors0: {colors0}\n")
    f.write(f"alphas0: {alphas0}\n")
    f.write(f"zorder0: {zorder0}\n")


df2 = df_starryz_rawTEPs
df1 = df_tematdb_rawTEPs

if (1):    
    ax = ax4
    tepname = 'ZT'

    scale_tep = 1
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    draw(df2)
    
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel('Figure of merit ZT')


if (1):    
    ax = ax1
    tepname = 'alpha'

    scale_tep = 1e3
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    draw(df2) 
    
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel(r'Seebeck coefficient $\alpha$ (mV K$^{-1}$)')

    
if (1):    
    ax = ax2
    tepname = 'rho'

    scale_tep = 1e0
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    draw(df2)
    
    ax.set_yscale('log')
    
    # ax.set_ylim(1e-4,1e10)
    
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel(r'Electrical resistivity $\rho$ ($\Omega$ m)')
    
      
if (1):    
    ax = ax3
    tepname = 'kappa'

    scale_tep = 1
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    draw(df2)
    
    ax.set_yscale('log')
    
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel(r'Thermal conductivity $\kappa$ (W m$^{-1}$ K$^{-1}$)')
    
    

ax1.set_title("(a)",loc='left')
ax2.set_title("(b)",loc='left')
ax3.set_title("(c)",loc='left')
ax4.set_title("(d)",loc='left')

for ax in [ax1,ax2,ax3,ax4]:
    ax.legend(fontsize=8.5)


plt.tight_layout()
plt.show()


import shutil

figfile1 =  "FIG_1_representative_teMatDb_vs_Starrydata2/figure.png"
figfile2 = f"FIG_1_representative_teMatDb_vs_Starrydata2/figure_{formattedDate}.png"

fig.savefig(figfile1,dpi=300)
# fig.savefig(figfile2,dpi=300)

shutil.copy(figfile1, figfile2) 

