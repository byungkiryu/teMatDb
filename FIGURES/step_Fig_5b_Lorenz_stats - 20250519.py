# -*- coding: utf-8 -*-
"""
Created on Fri May 16 15:29:12 2025

@author: byungkiryu
"""
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
    
import pandas as pd
import numpy as np
import scipy.stats as stats
from matplotlib import pyplot as plt
from matplotlib.ticker import LogLocator
from pykeri.byungkiryu import byungkiryu_util as br
formattedDate, yyyymmdd, HHMMSS = br.now_string()


if (1):
    
    path_tematdb272     = "../teMatDb_publication/teMatDb272_dataset_20250515/"
    file_rawTEPs        = "teMatDb_rawTEPs.csv"
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

df00 = df_tematdb_colTEPs.copy()


elec    = 1.602176634e-19
k_B     = 1.380649e-23 

L00 = (np.pi**2) / 3 * (k_B/elec)**2
L02 = 2.44e-8
L0 = L00


figsize = (7.2,5.3)
fig, axs = plt.subplots(2,2, figsize=figsize,dpi=500)
ax1, ax2 = axs[0]
ax3, ax4 = axs[1]


symbolsize = 36
ccmap = 'viridis'
# ccmap = 'inferno'


# # 1. 그룹별 최대 ZT값을 구함
# group_peak = df0.groupby('sample_id')['ZT'].max().reset_index()

# # 2. ZT 높은 순으로 정렬
# group_peak_sorted = group_peak.sort_values(by='ZT', ascending=False)

# # 3. 정렬된 sample_id 순서 가져오기
# sorted_ids = group_peak_sorted['sample_id']

# # 4. 원래 df를 sample_id 기준으로 정렬된 순서로 재정렬
# df_sorted = df0.set_index('sample_id').loc[sorted_ids].reset_index()


if (1):
    ax = ax1
    df0 = df00.sort_values(by='ZT')
    
    sc = ax.scatter( df0.Temperature, df0.Lorenz, c=df0.ZT, cmap=ccmap ,s=symbolsize,
                    vmin = 0)
    ax.set_xlabel('T (K)')  
    ax.set_ylabel(r"L$_{\rm TE}$ (V$^2$ K$^{-2}$)")

    ax.set_yscale('log')
    
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("ZT",fontsize=8)
    cbar.ax.tick_params(labelsize=8)

    
    
if (1):
    ax = ax2
    sc = ax.scatter(  df0.Lorenz, df0.alpha*1e6, c=df0.ZT, cmap=ccmap, s=symbolsize,
                    vmin = 0)
    ax.set_xscale('log')
    ax.set_xlabel(r"L$_{\rm TE}$ (V$^2$ K$^{-2}$)")
    ax.set_ylabel(r'$\alpha$ ($\mu$V K$^{-1}$)')
    
    ax.set_yticks([-600, -300, 0, 300, 600])
    ax.set_ylim(-600,600)
    
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("ZT",fontsize=8)
    cbar.ax.tick_params(labelsize=8)
    
    
if (1):
    ax = ax3
    sc = ax.scatter(  df0.Lorenz, df0.sigma/100, c=df0.ZT, cmap=ccmap, s=symbolsize,
                    vmin = 0)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r"L$_{\rm TE}$ (V$^2$ K$^{-2}$)")
    ax.set_ylabel(r'$\sigma$ (S cm$^{-1}$)')
    
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*0.1, numticks=10))

    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("ZT",fontsize=8)
    cbar.ax.tick_params(labelsize=8)



if (1):
    ax = ax4
    sc = ax.scatter( df0.Lorenz, df0.kappa, c=df0.ZT,  cmap=ccmap,s=symbolsize,
                    vmin = 0)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r"L$_{\rm TE}$")
    ax.set_ylabel(r'$\kappa$ (W m$^{-1}$ K$^{-1}$)')
    
    ax.set_ylim(0.1,20)
    # ax.set_ylabel()
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("ZT",fontsize=8)
    cbar.ax.tick_params(labelsize=8)
    
    
ax1.set_title("(a)",loc='left')
ax2.set_title("(b)",loc='left')
ax3.set_title("(c)",loc='left')
ax4.set_title("(d)",loc='left')

for ax in [ax4, ax2, ax3]:
    ax.axvline(1*L0, color='black', linestyle='dashed', linewidth=1)
    ax.axvline(0.5*L0, color='black', linestyle='dashdot', linewidth=1)
    ax.axvline(0.2*L0, color='black', linestyle='dotted', linewidth=1)

for ax in [ax1, ]:
    ax.axhline(1*L0, color='black', linestyle='dashed', linewidth=1)
    ax.axhline(0.5*L0, color='black', linestyle='dashdot', linewidth=1)
    ax.axhline(0.2*L0, color='black', linestyle='dotted', linewidth=1)
    
for ax in [ax1,ax2,ax3,ax4 ]:
    ax.text(1,1, "teMatDb272", transform=ax.transAxes,
            fontsize=7, va='bottom', ha='right')
    
    
fig.tight_layout()
plt.show()

figure_path  = "FIG_5b_Lorenz_Stats_from_collocatedTEPs/"

figure_file  = figure_path + f"figure_{formattedDate}.png"
fig.savefig(figure_file,dpi=300)
import shutil
shutil.copy(figure_file, figure_path+"figure.png") 