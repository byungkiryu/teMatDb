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

df_tematdb_colTEPs['alpha'] = alpha*1e6
df_tematdb_colTEPs['sigma'] = sigma/100
df_tematdb_colTEPs['rho'] = rho*1e5
df_tematdb_colTEPs['PF'] = PF *1e3
df_tematdb_colTEPs['Z']  = Z
df_tematdb_colTEPs['ZT']  = ZT
df_tematdb_colTEPs['Lorenz'] = Lorenz

df0 = df_tematdb_colTEPs.copy()


elec    = 1.602176634e-19
k_B     = 1.380649e-23 

L00 = (np.pi**2) / 3 * (k_B/elec)**2
L02 = 2.44e-8
L0 = L00


# figsize = (3.5,3)
# figsize = (7.2,5.3)
figsize = (7.2,8.0)
fig, axs = plt.subplots(3,2, figsize=figsize,dpi=500)
ax1, ax2 = axs[0]
ax3, ax4 = axs[1]
ax5, ax6 = axs[2]
# ax1 = axs

units = {}
units['Temperature'] = r" (K)"
units['alpha'] = r" ($\mu$V K$^{-1}$)"
units['sigma'] = r" (S cm$^{-1})$"
units['rho'] = r" (m$\Omega$ cm)$"
units['kappa'] = r" (W m$^{-1}$ K$^{-1})$"
units['ZT'] = ""
units['PF'] = r" (mW m$^{-1}$ K$^{-2}$)"

tepnames = {}
tepnames['Temperature'] = "T"
tepnames['alpha'] = r"$\alpha$"
tepnames['sigma'] = r"$\sigma$"
tepnames['rho'] = r"$\rho$"
tepnames['kappa'] = r"$\kappa$"
tepnames['ZT'] = "ZT"
tepnames['PF'] = "PF"

symbolsize = 36

Tmin = 000
Tmax = 900
df0 = df0[ df0.Temperature >= Tmin]
df0 = df0[ df0.Temperature <= Tmax]


if (1):
    ax = ax1
    df = df0
    
    xx = 'sigma'
    yy = 'alpha'
    zz = 'PF'
    
    df = df.sort_values(by=zz)
    sc = ax.scatter( df[xx], df[yy], c=df[zz], cmap='inferno',s=symbolsize,
                    vmin=0 )
    ax.set_xlabel(tepnames[xx]+units[xx] )
    ax.set_ylabel(tepnames[yy]+units[yy] )    
    ax.set_xscale('log')
    
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*0.1, numticks=10))
    ax.set_yticks([-600, -300, 0, 300, 600])
    ax.set_ylim(-600,600)
    ax.set_xlim(0.8e0,2e4)
    
    cbar = plt.colorbar(sc, ax=ax, shrink=1.0, pad=0.02)
    cbar.set_label(tepnames[zz]+units[zz],fontsize=8)
    cbar.ax.tick_params(labelsize=8)

if (1):
    ax = ax2
    df = df0
    
    xx = 'sigma'
    yy = 'alpha'
    zz = 'ZT'
    
    df = df.sort_values(by=zz)
    sc = ax.scatter( df[xx], df[yy], c=df[zz], cmap='inferno',s=symbolsize,
                    vmin=0 )
    ax.set_xlabel(tepnames[xx]+units[xx] )
    ax.set_ylabel(tepnames[yy]+units[yy] )    
    ax.set_xscale('log')
    
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*0.1, numticks=10))
    ax.set_yticks([-600, -300, 0, 300, 600])
    ax.set_ylim(-600,600)
    ax.set_xlim(0.8e0,2e4)
    
    cbar = plt.colorbar(sc, ax=ax, shrink=1.0, pad=0.02)
    cbar.set_label(tepnames[zz]+units[zz],fontsize=8)
    cbar.ax.tick_params(labelsize=8)



if (1):
    ax = ax3
    df = df0
    
    xx = 'sigma'
    yy = 'kappa'
    zz = 'ZT'
    
    df = df.sort_values(by=zz)
    sc = ax.scatter( df[xx], df[yy], c=df[zz], cmap='inferno',s=symbolsize,
                    vmin=0 )
    ax.set_xlabel(tepnames[xx]+units[xx] )
    ax.set_ylabel(tepnames[yy]+units[yy] )    
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*0.1, numticks=10))
    
    ax.set_xlim(0.8e0,2e4)
    ax.set_ylim(0.1,20)
    
    cbar = plt.colorbar(sc, ax=ax, shrink=1.0, pad=0.02)
    cbar.set_label(tepnames[zz]+units[zz],fontsize=8)    
    cbar.ax.tick_params(labelsize=8)


if (1):
    ax = ax4
    df = df0
    
    xx = 'alpha'
    yy = 'kappa'
    zz = 'ZT'
    
    df = df.sort_values(by=zz)
    sc = ax.scatter( df[xx], df[yy], c=df[zz], cmap='inferno',s=symbolsize,
                    vmin=0 )
    ax.set_xlabel(tepnames[xx]+units[xx] )
    ax.set_ylabel(tepnames[yy]+units[yy] )    
    # ax.set_xscale('log')
    ax.set_yscale('log')
    
    ax.set_xticks([-600, -300, 0, 300, 600])
    ax.set_xlim(-600,600)
    ax.set_ylim(0.1,20)
    
    cbar = plt.colorbar(sc, ax=ax, shrink=1.0, pad=0.02)
    cbar.set_label(tepnames[zz]+units[zz],fontsize=8)    
    cbar.ax.tick_params(labelsize=8)
        
    
if (1):
    ax = ax5
    df = df0
    
    xx = 'PF'
    yy = 'ZT'
    zz = 'Temperature'
    
    df = df.sort_values(by=zz)
    sc = ax.scatter( df[xx], df[yy], c=df[zz], cmap='inferno',s=symbolsize,vmin=Tmin, vmax=Tmax )
    ax.set_xlabel(tepnames[xx]+units[xx] )
    ax.set_ylabel(tepnames[yy]+units[yy] )    
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    ax.set_xlim(1e-3,2e1)
    ax.set_ylim(1e-6,1e1)
    
    cbar = plt.colorbar(sc, ax=ax, shrink=1.0, pad=0.02)
    cbar.set_label(tepnames[zz]+units[zz],fontsize=8)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_ticks([0, 300, 600, 900])
    
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*0.1, numticks=10))

if (1):
    ax = ax6
    df = df0
    
    xx = 'kappa'
    yy = 'ZT'
    zz = 'Temperature'
    
    df = df.sort_values(by=zz)
    sc = ax.scatter( df[xx], df[yy], c=df[zz], cmap='inferno',s=symbolsize,vmin=Tmin, vmax=Tmax )
    ax.set_xlabel(tepnames[xx]+units[xx] )
    ax.set_ylabel(tepnames[yy]+units[yy] )    
    ax.set_xscale('log')
    ax.set_yscale('log')   
    
    ax.set_xlim(0.1,20)
    ax.set_ylim(1e-6,1e1)
    
    cbar = plt.colorbar(sc, ax=ax, shrink=1.0, pad=0.02)
    cbar.set_label(tepnames[zz]+units[zz],fontsize=8)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_ticks([0, 300, 600, 900])
    
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*0.1, numticks=10))
    
    
stemp = ""
ax1.set_title("(a)"+stemp,loc='left')
ax2.set_title("(b)"+stemp,loc='left')
ax3.set_title("(c)"+stemp,loc='left')
ax4.set_title("(d)"+stemp,loc='left')
ax5.set_title("(e)"+stemp,loc='left')
ax6.set_title("(f)"+stemp,loc='left')

for ax in [ax1,ax2,ax3,ax4,ax5,ax6]:
    ax.text(1,1, "teMatDb272", transform=ax.transAxes,
            fontsize=7, va='bottom', ha='right')


# for ax in [ax2,ax3,ax4]:
#     ax.axvline(1, color='black', linestyle='dotted', linewidth=1)
#     ax.axvline(0.5, color='black', linestyle='dotted', linewidth=1)
#     ax.axvline(0.2, color='black', linestyle='dotted', linewidth=1)
    

fig.tight_layout()
plt.show()

figure_path  = "FIG_5a_TEP_TEP_plots_for_lowTs_{:03}_{}/".format(Tmin,Tmax)
figure_file  = figure_path + f"figure_{formattedDate}.png"


fig.savefig(figure_file,dpi=300)

import shutil
shutil.copy(figure_file, figure_path+"figure.png") 