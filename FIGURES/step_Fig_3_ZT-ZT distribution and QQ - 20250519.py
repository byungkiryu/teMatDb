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
import scipy.stats as stats
from matplotlib import pyplot as plt
from matplotlib import cm
from pykeri.byungkiryu import byungkiryu_util as br
formattedDate, yyyymmdd, HHMMSS = br.now_string()


if (1):
    
    file_samples =        "../data_900_tematdb_meta/"+"tematdb_v1.1.6__meta_samples-scZT_clas_filteres-20250515_130649.csv"
    file_rawTEPs =        "../data_100_tematdb_csv_converted/"+"tematdb_v1.1.6_completeTEPset.csv"
    file_collocatedTEPs = "../data_300_tematdb_extTEP_csv/"  + "tematdb_v1.1.6_extendedTEPset_dT2K.csv"    
    df_tematdb0_samples = pd.read_csv( file_samples, )
    df_tematdb0_rawTEPs = pd.read_csv( file_rawTEPs, )
    df_tematdb0_colTEPs = pd.read_csv( file_collocatedTEPs, )
    df_tematdb0_colTEPs = df_tematdb0_colTEPs[ df_tematdb0_colTEPs.is_Temp_in_TEPZT]    
    
    


figsize=(7,6)
fig, axs = plt.subplots(2,2, figsize=figsize )
ax1, ax2 = axs[0]
ax3, ax4 = axs[1]


f1 = df_tematdb0_samples.copy()
f2 = df_tematdb0_samples[ df_tematdb0_samples.cri_product_def == True].copy()

labels  = ["teMatDb v1.1.6 \n(before Sc-ZT filtering)", 
           "teMatDb272 \n(after Sc-ZT filtering)"]



# cols    = ['avg_ZT_ofTEPEval', 'avg_ZT_ofRawFig']
axislabels   = ["Peak ZT (TEP)",  "Peak ZT (figure)"]
# draw_ZTZT(ax)


def drawxxx(ax,idx=1):
    
    ftemp = f.sort_values(by='errdZT_Linf').reset_index(drop=True)
    
    X = ftemp['peak_ZT_ofTEPEval']
    Y = ftemp['peak_ZT_ofRawFig']
    sizes = ftemp.errdZT_Linf * 200 
    
    # ax.plot( [0,3],[0,3], zorder=1, color='black', linewidth=10, alpha=0.4)
    sc = ax.scatter(X,Y, c=ftemp.errdZT_L2,  s=sizes, 
                    # label=labels[idx], 
                    # cmap='coolwarm',
                    cmap='inferno',
                    vmin=0, vmax=0.2526)
    ax.set_xlabel( axislabels[0] )
    ax.set_ylabel( axislabels[1] )
    ax.text(0.03,0.97, labels[idx], transform=ax.transAxes,
                  fontsize=8, va='top', ha='left')

    cbar = plt.colorbar(sc, ax=ax, shrink=1.0, pad=0.02)
    cbar.set_label(r"RMS $\delta$(ZT) per sample",fontsize=9)
    # cbar.ax.tick_params(labelsize=8)

colors = ['C0','C1']


ax = ax1
f = f1
# axislabel = axislabels[0]
drawxxx(ax,idx=0)


ax = ax2
f = f2
# axislabel = axislabels[1]
drawxxx(ax,idx=1)


# for ax in [ax1,ax2,ax3,ax4,ax5,ax6]:
#     ax.text(1,1, "teMatDb272", transform=ax.transAxes,
#             fontsize=7, va='bottom', ha='right')



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
        
    ax.scatter( res[0][0], res[0][1], s=15, 
               color = cm.coolwarm(0.8) ,
               # facecolor='None', edgecolor='red',
               label=labels[0])    
    ax.plot( [X0,X1],[Y0,Y1], color='black',linestyle='dotted' ,linewidth=1)
    
    ax.text(0.03,0.97, labels[0], transform=ax.transAxes,
                  fontsize=8, va='top', ha='left')
    ax.text( 0.97, 0.03, r"R$^2$={:.4f}".format(R2), transform=ax.transAxes,
            fontsize=10, va='bottom', ha='right')
            # fontsize=8 )
    ax.set_xlabel('Theoretical quantiles')    
    label=r'$\delta \rm (ZT) $' 
    ax.set_ylabel(label)
    # ax.set_title("(c)", loc='left')



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
        
    ax.scatter( res[0][0], res[0][1], s=15, 
               color = cm.coolwarm(0.2) ,
               # facecolor='None', edgecolor='red',
               label=labels[0])    
    ax.plot( [X0,X1],[Y0,Y1], color='black',linestyle='dotted',linewidth=1)
    
    ax.text(0.03,0.97, labels[1], transform=ax.transAxes,
                  fontsize=8, va='top', ha='left')
    ax.text( 0.97, 0.03, r"R$^2$={:.4f}".format(R2), transform=ax.transAxes,
            fontsize=10, va='bottom', ha='right')
    
    ax.set_xlabel('Theoretical quantiles')    
    label=r'$\delta \rm (ZT) $' 
    ax.set_ylabel(label)


ax1.set_title("(a)", loc='left')
ax2.set_title("(b)", loc='left')
ax3.set_title("(c)", loc='left')
ax4.set_title("(d)", loc='left')

# for ax in [ax3, ax4]:
#     ax.legend(fontsize=8)

for g in [g1, g2]:
    print( g.sample_id.nunique() )





fig.tight_layout()
plt.show()

figure_path  = "FIG_3/"
figure_file  = figure_path + f"figure_{formattedDate}.png"


fig.savefig(figure_file,dpi=300)

import shutil
shutil.copy(figure_file, figure_path+"figure.png") 