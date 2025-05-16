# -*- coding: utf-8 -*-
"""
Created on Fri May 16 15:29:12 2025

@author: byungkiryu
"""

import os
import pandas as pd
import numpy as np
import scipy.stats as stats
from matplotlib import pyplot as plt
from pykeri.byungkiryu import byungkiryu_util as br
formattedDate, yyyymmdd, HHMMSS = br.now_string()


if (1):
    
    path_tematdb272 = "./teMatDb_publication/teMatDb272_dataset_20250515/"
    file_rawTEPs = "teMatDb_rawTEPs.csv"
    file_collocatedTEPs = "teMatDb_collocatedTEPs.csv"    
    
    file_samples = 'teMatDb_samples.csv'
    file_rawTEPs = 'teMatDb_rawTEPs.csv'
    file_colTEPs = 'teMatDb_collocatedTEPs.csv'
    
    df_tematdb_samples           = pd.read_csv( path_tematdb272 +file_samples, )
    df_tematdb_rawTEPs           = pd.read_csv( path_tematdb272 +file_rawTEPs, )
    df_tematdb_colTEPs           = pd.read_csv( path_tematdb272 +file_collocatedTEPs, ) 
    


alpha       = df_tematdb_colTEPs.alpha
rho         = df_tematdb_colTEPs.rho
sigma       = 1/rho
kappa       = df_tematdb_colTEPs.kappa
Temperature = df_tematdb_colTEPs.Temperature   

PF = alpha*alpha*sigma
Z  = PF/kappa
ZT = Z*Temperature

RK = rho*kappa
Lorenz  = RK/Temperature

df_tematdb_colTEPs['sigma'] = sigma
df_tematdb_colTEPs['PF'] = PF
df_tematdb_colTEPs['Z']  = Z
df_tematdb_colTEPs['ZT']  = ZT
df_tematdb_colTEPs['Lorenz'] = Lorenz

df0 = df_tematdb_colTEPs.copy()


L0 = 2.44e-8


# figsize = (3.5,3)
figsize = (7,7)
fig, axs = plt.subplots(2,2, figsize=figsize,dpi=500)
ax1, ax2 = axs[0]
ax3, ax4 = axs[1]
# ax1 = axs


if (1):
    ax = ax1
    df = df0
    
    ax.scatter( df.Temperature, df.Lorenz, c=df.ZT, cmap='viridis' )
    ax.set_xlabel('T (K)')    
    ax.set_xlim(-100,1300)
    ax.set_ylabel(r"L$_{\rm TE}$ :=$(\rho\kappa) \cdot $ T$^{-1}$ (V$^2$ K$^{-2}$)")
    ax.axhline(L0, color='black', linestyle='dotted', linewidth=1)
    ax.axhline(L0*.5, color='black', linestyle='dotted', linewidth=1)
    ax.axhline(L0*.2, color='black', linestyle='dotted', linewidth=1)
    ax.set_yscale('log')
    # ax.set_ylim(3e-9,5e-5)


if (0):
    ax = ax4
    
    sample_id_list = [43, 296, 374, 404]
    cmaplist = ['viridis', 'plasma','spring','inferno']
    # cmaplist = ['viridis', 'plasma','spring','inferno']
    
    for idx, sample_id in enumerate(sample_id_list):
        
        cmap = cmaplist[idx]
        df = df0[ df0.sample_id == sample_id].copy()
        ax.plot( df.Temperature, df.Lorenz / L0, 
                   # c=df.ZT, 
                   # cmap=cmap,
                   # alpha = 0.2,
                   label=f'sample_id = {sample_id}' )
    
    
    
    ax.set_xlabel('T (K)')    
    ax.set_xlim(-100,1300)
    ax.set_ylabel(r"L$_{\rm TE}$ / L0")
    # ax.axhline(1, color='black', linestyle='dotted', linewidth=1)
    # ax.axhline(0.5, color='black', linestyle='dotted', linewidth=1)
    # ax.axhline(0.2, color='black', linestyle='dotted', linewidth=1)
    ax.legend(loc=2)
    ax.set_ylim(0,4)


if (0):
    ax = ax1
    
    ax.scatter( (df0.alpha)*1e3, df0.ZT, c=np.log(df0.Lorenz), cmap='viridis',
               # alpha=0.2
               )
    # ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$\alpha$ (mV K$^{-1}$)')
    ax.set_ylabel('ZT')

if (1):
    ax = ax2
    ax.scatter( df0.Lorenz/ L0, df0.ZT, c=np.abs( (df0.alpha)*1e3 ), cmap='viridis',
               # alpha=0.2
               )
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r"L$_{\rm TE}$ / L$_0$")
    ax.set_ylabel('ZT')
    # ax.set_ylabel(r'$\alpha$ (mV K$^{-1}$)')

if (1):
    ax = ax3
    ax.scatter( df0.Lorenz/ L0, df0.sigma, c=df0.ZT, cmap='viridis',
               # alpha=0.2
               )
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r"L$_{\rm TE}$ / L$_0$")
    ax.set_ylabel(r'$\sigma$ (S m$^{-1}$)')
    # ax.set_ylabel(r'$\alpha$ (mV K$^{-1}$)')

if (1):
    ax = ax4
    ax.scatter( df0.Lorenz / L0, df0.alpha*1e3, c=df0.ZT, cmap='viridis',
               # alpha=0.2
               )
    ax.set_xscale('log')
    # ax.set_yscale('log')
    ax.set_xlabel(r"L$_{\rm TE}$ / L$_0$")
    ax.set_ylabel(r'$\alpha$ (mV K$^{-1}$)')

ax1.set_title("(a)",loc='left')
ax2.set_title("(b)",loc='left')
ax3.set_title("(c)",loc='left')
ax4.set_title("(d)",loc='left')

for ax in [ax2,ax3,ax4]:
    ax.axvline(1, color='black', linestyle='dotted', linewidth=1)
    ax.axvline(0.5, color='black', linestyle='dotted', linewidth=1)
    ax.axvline(0.2, color='black', linestyle='dotted', linewidth=1)
    

fig.tight_layout()
plt.show()

figure_path  = "FIG_5_Lorenz_Stats_from_collocatedTEPs/"
figure_file0 = figure_path +  "figure"
figure_file  = figure_path + f"figure_{formattedDate}"

fig.savefig(figure_file0+".png",dpi=300)
fig.savefig(figure_file +".png",dpi=300)