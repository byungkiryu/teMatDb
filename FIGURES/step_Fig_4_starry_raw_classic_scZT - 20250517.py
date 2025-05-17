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
    
    path_starrypub = "../../030 starrydata2505 ZT filter  -- 20250517 - simple teps/990_starry_publication/"
    
    file_starryz10840 =  "starryz10840"
    file_starryz15053 =  "starryz15053"
    file_starryz15532 =  "starryz15532"
    
    target = "starryz_samples.csv"
    
    file_starryz = file_starryz10840
    path = path_starrypub+file_starryz+"/"+target
    df_10840 = pd.read_csv( path )
    
    file_starryz = file_starryz15053
    path = path_starrypub+file_starryz+"/"+target
    df_15053 = pd.read_csv( path )
    
    file_starryz = file_starryz15532
    path = path_starrypub+file_starryz+"/"+target
    df_15532 = pd.read_csv( path )
    
    
    df_starryz  = df_10840.copy()
    df_classic  = df_15053.copy()
    df_raw      = df_15532.copy()
    

df_list = [df_raw, df_classic, df_starryz]




figsize = (7,3.5)
fig, axs = plt.subplots(1,2, figsize=figsize,dpi=300)
ax1, ax2 = axs
alpha = 0.5

ZT1 = 'peak_ZT_ofRawFig'
ZT2 = 'peak_ZT_ofTEPEval'

# ZT1_label = "Peak ZT from figure raw ZT"
# ZT2_label = "Peak ZT from TEP reevaluated"


ZT1_label = "Peak ZT (figure)"
ZT2_label = "Peak ZT (TEP)"



filtering_list = ['Rawdata 250501','Classical filter','Sc-ZT filter']
label_list     = ['Starrydata\n(250501)','Classical\nfilter','Sc-ZT\nfilter']

for idx, filtering in enumerate(filtering_list):
    
    label = label_list[idx]
    
    df = df_list[idx]
    
    # print(filtering, len(filteredd) )
    
    peak_ZT_ofRawFig = df.peak_ZT_ofRawFig
    peak_ZT_ofTEPEval = df.peak_ZT_ofTEPEval
    
    for ax in [ax1,ax2]    :
        ax.scatter( peak_ZT_ofRawFig, peak_ZT_ofTEPEval, label=label, alpha=alpha, edgecolors='none')



for ax in [ax1, ax2]:
    ax.set_xlabel(ZT1_label)
    ax.set_ylabel(ZT2_label)
    
    diag = [1e-8,1e2]
    
    ax.plot(diag,diag,ls='dotted',color='black')
    ax.legend(fontsize=8)

ax1.set_title("(a)",loc='left')
ax2.set_title("(b)",loc='left')

ax1.set_xscale('log')
ax1.set_yscale('log')
# # plt.xlim(-0.5,10.5)
# # plt.ylim(-0.5,10.5)
# for ax


ax2.set_xlim(-0.5,6.5)
ax2.set_ylim(-0.5,6.5)



fig.tight_layout()
plt.show()

figure_path  = "FIG_4_ScZT_filter_validation_w_starryz/"
figure_file0 = figure_path +  "figure"
figure_file  = figure_path + f"figure_{formattedDate}"

fig.savefig(figure_file0+".png",dpi=300)
fig.savefig(figure_file +".png",dpi=300)