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
    
    file_samples = "data_900_tematdb_meta/"+"tematdb_v1.1.6__meta_samples-scZT_clas_filteres-20250515_130649.csv"
    file_rawTEPs = "data_100_tematdb_csv_converted/"+"tematdb_v1.1.6_completeTEPset.csv"
    file_collocatedTEPs = "data_300_tematdb_extTEP_csv/"  + "tematdb_v1.1.6_extendedTEPset_dT2K.csv"    
    df_tematdb0_samples           = pd.read_csv( file_samples, )
    df_tematdb0_rawTEPs           = pd.read_csv( file_rawTEPs, )
    df_tematdb0_colTEPs           = pd.read_csv( file_collocatedTEPs, )
    df_tematdb0_colTEPs = df_tematdb0_colTEPs[ df_tematdb0_colTEPs.is_Temp_in_TEPZT]    
    
    
    
    # path_tematdb272 = "./teMatDb_publication/teMatDb272_dataset_20250515/"
    # file_rawTEPs = "teMatDb_rawTEPs.csv"
    # file_collocatedTEPs = "teMatDb_collocatedTEPs.csv"    
    # df_tematdb_samples           = pd.read_csv( path_tematdb272 +file_samples, )
    # df_tematdb_rawTEPs           = pd.read_csv( path_tematdb272 +file_rawTEPs, )
    # df_tematdb_colTEPs           = pd.read_csv( path_tematdb272 +file_collocatedTEPs, ) 
    # seeb = df_tematdb_colTEPs.alpha
    # resi = df_tematdb_colTEPs.rho
    # kapp = df_tematdb_colTEPs.kappa
    # Temp = df_tematdb_colTEPs.Temperature    
    # df_tematdb_colTEPs['ZT'] = seeb*seeb*Temp/resi/kapp






figsize=(6,6)
fig, axs = plt.subplots(2,2, figsize=figsize )
ax1, ax2 = axs[0]
ax3, ax4 = axs[1]


f1 = df_tematdb0_samples.copy()
f2 = df_tematdb0_samples[ df_tematdb0_samples.cri_product_def == True].copy()
# labels  = ["teMatDb v1.1.6\n(before filtering)", 
#            "teMatDb272 \n(after sc-ZT filtering)"]
labels  = ["teMatDb v1.1.6\n(before Sc-ZT filtering)", 
           "teMatDb272 \n(after Sc-ZT filtering)"]

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




samples_teMatDb272 = df_tematdb0_samples[ df_tematdb0_samples.cri_product_def == True ].sample_id.unique().tolist()

g1 =  df_tematdb0_colTEPs[ df_tematdb0_colTEPs.is_Temp_in_TEPZT == True ].copy()
g2 =  g1[ g1.sample_id.isin(samples_teMatDb272)]





if (1):
    ax = ax3
    f = g1.copy()
    delZT = f['ZT_author_declared'] - f['ZT_tep_reevaluated']
    res = stats.probplot(delZT,dist=stats.norm, plot=None, rvalue=True)  
        
    slope, intercept, rmR2 = res[1]
    R2 = rmR2**2
    def lin_eq(x,slope,intercept):
        return slope*x+intercept
        
    X0, X1 = -4.5, 4.5
    Y0 = lin_eq(X0,slope,intercept)
    Y1 = lin_eq(X1,slope,intercept)    
        
    ax.scatter( res[0][0], res[0][1], s=20, facecolor='None', edgecolor='C0',
               label=labels[0])    
    ax.plot( [X0,X1],[Y0,Y1], color='black',linestyle='solid',linewidth=1)
    ax.text( 0.05, 0.90, r"R$^2$={:.4f}".format(R2), transform=ax.transAxes,)
            # fontsize=8 )
    ax.set_xlabel('Theoretical quantiles')    
    label=r'$\delta \rm (ZT) $' 
    ax.set_ylabel(label)
    ax.set_title("(c)", loc='left')



if (1):
    ax = ax4
    f = g2.copy()
    delZT = f['ZT_author_declared'] - f['ZT_tep_reevaluated']
    res = stats.probplot(delZT,dist=stats.norm, plot=None, rvalue=True)  
        
    slope, intercept, rmR2 = res[1]
    R2 = rmR2**2
    def lin_eq(x,slope,intercept):
        return slope*x+intercept
        
    X0, X1 = -4.5, 4.5
    Y0 = lin_eq(X0,slope,intercept)
    Y1 = lin_eq(X1,slope,intercept)    
        
    ax.scatter( res[0][0], res[0][1], s=20, facecolor='None', edgecolor='C1',
               label=labels[1])    
    ax.plot( [X0,X1],[Y0,Y1], color='black',linestyle='solid',linewidth=1)
    ax.text( 0.05, 0.90, r"R$^2$={:.4f}".format(R2), transform=ax.transAxes,)
            # fontsize=8 )
    ax.set_xlabel('Theoretical quantiles')    
    label=r'$\delta \rm (ZT) $' 
    ax.set_ylabel(label)
    ax.set_title("(c)", loc='left')


for ax in [ax1, ax2]:
    # ax.set_xlabel( axislabel[0] )
    # ax.set_ylabel( axislabel[1] )
    ax.set_xlim(0,3.6)
    ax.set_ylim(0,3.6)
    ax.legend(loc=2, fontsize=7)
    ax.set_xticks([0,1,2,3])
    ax.set_yticks([0,1,2,3])

for ax in [ax3, ax4]:
    
    ax.legend(loc=4, fontsize=8)



for g in [g1, g2]:
    print( g.sample_id.nunique() )




fig.tight_layout()
plt.show()

figure_path  = "FIG_3_ZTerror_over_teMatDb/"
figure_file0 = figure_path +  "figure"
figure_file  = figure_path + f"figure_{formattedDate}"

fig.savefig(figure_file0+".png",dpi=300)
fig.savefig(figure_file +".png",dpi=300)