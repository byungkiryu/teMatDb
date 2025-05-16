# -*- coding: utf-8 -*-
"""
Created on Fri May 16 15:29:12 2025

@author: byungkiryu
"""


import pandas as pd
import numpy as np
import scipy.stats as stats
from matplotlib import pyplot as plt
from pykeri.byungkiryu import byungkiryu_util as br
formattedDate, yyyymmdd, HHMMSS = br.now_string()


if (1):
    path_tematdb = "./teMatDb_publication/teMatDb272_dataset_20250515/"
    file_samples = "data_900_tematdb_meta/"+"tematdb_v1.1.6__meta_samples-scZT_clas_filteres-20250515_130649.csv"
    file_rawTEPs = "data_100_tematdb_csv_converted/"+"tematdb_v1.1.6_completeTEPset.csv"
    file_collocatedTEPs = "data_300_tematdb_extTEP_csv/"  + "tematdb_v1.1.6_extendedTEPset_dT2K.csv"    
    df_tematdb0_samples           = pd.read_csv( file_samples, )
    df_tematdb0_rawTEPs           = pd.read_csv( file_rawTEPs, )
    df_tematdb0_colTEPs           = pd.read_csv( file_collocatedTEPs, )
    df_tematdb0_colTEPs = df_tematdb0_colTEPs[ df_tematdb0_colTEPs.is_Temp_in_TEPZT]    
    seeb = df_tematdb0_colTEPs.alpha
    resi = df_tematdb0_colTEPs.rho
    kapp = df_tematdb0_colTEPs.kappa
    Temp = df_tematdb0_colTEPs.Temperature    
    df_tematdb0_colTEPs['ZT'] = seeb*seeb*Temp/resi/kapp
    
    
    # file_samples_all = ""
       
    # path_starryz11067 = "./../030 starrydata2505 ZT filter  -- 20250515 - simple teps/990_starry_publication/starryz10840/"
    # file_samples = "starryz_samples.csv"
    # file_rawTEPs = "starryz_rawTEPs.feather"
    # file_collocatedTEPs = "starryz_collocatedTEPs.feather"   
    # df_starryz_samples   = pd.read_csv( path_starryz11067+file_samples, )
    # df_starryz_rawTEPs   = pd.read_feather( path_starryz11067+file_rawTEPs, )
    # df_starryz_colTEPs   = pd.read_feather( path_starryz11067+file_collocatedTEPs, )   
    
    







figsize=(5.0,2.8)
fig, axs = plt.subplots(1,2, figsize=figsize )
ax1, ax2 = axs


f1 = df_tematdb0_samples
f2 = df_tematdb0_samples[ df_tematdb0_samples.cri_product_def == True]
labels  = ["teMatDb \n(all, v1.1.6)",  "teMatDb272 \n(cleansed)"]

def draw_ZTZT(ax):
    for idx, f in enumerate([f1,f2]):
        X = f[cols[0]]
        Y = f[cols[1]]
        ax.scatter(X,Y, s=20, alpha=0.5, label=labels[idx] )
        diag = [0,4]
        ax.plot(diag, diag, color='black',linestyle='dashed',linewidth=1)

ax=ax1
cols    = ['avg_ZT_ofTEPEval', 'avg_ZT_ofRawFig']
axislabel   = ["Avg ZT (TEP)",  "Avg ZT (figure)"]
draw_ZTZT(ax)
ax.set_xlabel( axislabel[0] )
ax.set_ylabel( axislabel[1] )

ax=ax2
cols    = ['peak_ZT_ofTEPEval', 'peak_ZT_ofRawFig']
axislabel   = ["Peak ZT (TEP)", "Peak ZT (figure)"]
draw_ZTZT(ax)
ax.set_xlabel( axislabel[0] )
ax.set_ylabel( axislabel[1] )

ax1.set_title("(a)",loc='left')
ax2.set_title("(b)",loc='left')

for ax in [ax1, ax2]:
    # ax.set_xlabel( axislabel[0] )
    # ax.set_ylabel( axislabel[1] )
    ax.set_xlim(0,3.6)
    ax.set_ylim(0,3.6)
    ax.legend(loc=2, fontsize=7.7)
    ax.set_xticks([0,1,2,3])
    ax.set_yticks([0,1,2,3])




# ax1.set_xlim(0,3)
# ax1.set_ylim(0,3)


fig.tight_layout()
plt.show()

figure_path  = "FIG_3_ZTerror_over_data/"
figure_file0 = figure_path +  "figure"
figure_file  = figure_path + f"figure_{formattedDate}"

fig.savefig(figure_file0+".png",dpi=300)
fig.savefig(figure_file +".png",dpi=300)