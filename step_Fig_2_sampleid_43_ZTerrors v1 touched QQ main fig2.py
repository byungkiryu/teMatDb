# -*- coding: utf-8 -*-
"""
Created on Fri May  9 18:28:07 2025

@author: byungkiryu
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
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

    # path_tematdb = "./teMatDb_publication/teMatDb272_dataset_20250515/"
    file_samples = "data_900_tematdb_meta/"+"tematdb_v1.1.6__meta_samples-scZT_clas_filteres-20250515_130649.csv"
    file_rawTEPs = "data_100_tematdb_csv_converted/"+"tematdb_v1.1.6_completeTEPset.csv"
    file_collocatedTEPs = "data_300_tematdb_extTEP_csv/"  + "tematdb_v1.1.6_extendedTEPset_dT2K.csv"    
    df_tematdb_samples           = pd.read_csv( file_samples, )
    df_tematdb_rawTEPs           = pd.read_csv( file_rawTEPs, )
    df_tematdb_colTEPs           = pd.read_csv( file_collocatedTEPs, )
    df_tematdb_colTEPs = df_tematdb_colTEPs[ df_tematdb_colTEPs.is_Temp_in_TEPZT]
    
    seeb = df_tematdb_colTEPs.alpha
    resi = df_tematdb_colTEPs.rho
    kapp = df_tematdb_colTEPs.kappa
    Temp = df_tematdb_colTEPs.Temperature
    
    df_tematdb_colTEPs['ZT'] = seeb*seeb*Temp/resi/kapp
    
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
               label="ZT (figure)", 
               # edgecolors='none',
               zorder = zorder.pop(0)
               )

def drawZTline(df):
    T    = df['Temperature']
    TEP  = df[tepname]
    ax.plot( T, TEP * scale_tep, 
               alpha=alphas.pop(0), 
               color='C0', 
               label="ZT (TEP)"  , 
               # edgecolors='none',
               zorder = zorder.pop(0),
               linewidth=linewidth 
               )   

sample_id = 43
# sample_id = 113


figure_path = "FIG_2_total_TEP_TO_ERROR_sampleid43/"
figure_file0 = figure_path +  "figure"
figure_file  = figure_path + f"figure_{formattedDate}"




figsize=(7.2,4.5)
fig, axs = plt.subplots(2,3, figsize=figsize )
ax1, ax2, ax3 = axs[0]
ax4, ax5, ax6 = axs[1]

# figsize=(7,9)
# fig, axs = plt.subplots(3,2, figsize=figsize )
# ax1, ax2 = axs[0]
# ax3, ax4 = axs[1]
# ax5, ax6 = axs[2]

labels0 = ['TEP (figure)',
           'TEP (interp.)']   
colors0 = ['C0','C0'] 
alphas0 = [1, 0.6]
zorder0 = [200, 100]
linewidth = 2

# with open(figure_file+"_meta.txt", "w") as f:
#     f.write(f"labels0: {labels0}\n")
#     f.write(f"colors0: {colors0}\n")
#     f.write(f"alphas0: {alphas0}\n")
#     f.write(f"zorder0: {zorder0}\n")
#     f.write(f"linewidth: {linewidth}\n")



df_rawTEPs = df_tematdb_rawTEPs[ df_tematdb_rawTEPs.sample_id == sample_id  ] 
df_colTEPs = df_tematdb_colTEPs[ df_tematdb_colTEPs.sample_id == sample_id  ] 



df1 = df_rawTEPs
df2 = df_colTEPs


if (1):    
    ax = ax1
    tepname = 'alpha'

    scale_tep = 1e6
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    drawline(df2)
    
    ax.set_xlabel('T (K)')
    ax.set_ylabel(r'$\alpha$ ($\mu$V K$^{-1}$)')

    
if (1):    
    ax = ax2
    tepname = 'rho'

    scale_tep = 1e+5
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    drawline(df2)
    
    # ax.set_yscale('log')
    
    ax.set_xlabel('T (K)')
    ax.set_ylabel(r'$\rho$ (m$\Omega$ cm)')
    
      
if (1):    
    ax = ax3
    tepname = 'kappa'

    scale_tep = 1
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    draw(df1)
    drawline(df2)
    
    # ax.set_yscale('log')
    
    ax.set_xlabel('T (K)')
    ax.set_ylabel(r'$\kappa$ (W m$^{-1}$ K$^{-1}$)')

if (0):    
    ax = ax4
    tepname = 'ZT'

    scale_tep = 1
    labels, colors, alphas, zorder = labels0.copy(), colors0.copy(), alphas0.copy(), zorder0.copy()
    
    drawZT(df1)
    # drawZTline(df2)
    
    ax.set_xlabel('T (K)')
    ax.set_ylabel('ZT')    

df = df_colTEPs
if (1):    
    ax = ax4

    
    Temp = df.Temperature
    seeb = df.alpha
    resi = df.rho
    thrm = df.kappa
    ZT2 = seeb*seeb/resi/thrm*Temp
    ZT1 =df.ZT_author_declared

    diag = [0.4, 1.25] 
    ax.plot( Temp, ZT1, label='ZT (figure)', linewidth=1)
    ax.plot( Temp, ZT2, label='ZT (TEP)', linewidth=1)
        
    ax.set_xlabel('T (K)')
    ax.set_ylabel('ZT')
    

    
if (1):
    ax = ax5
     
    delZTscale = 1
    delZT = ZT1 - ZT2
    delZT = delZTscale*delZT
    
    
    # label=r'$\delta \rm (ZT) \cdot 10^2 $' 
    label=r'$\delta \rm (ZT) \times 10^2 $' 
    label=r'$\delta \rm (ZT) $' 
    
    samplelabel = 'sample_id={}'.format(sample_id)
    ax.scatter( Temp, delZT, s=20, facecolor='None', edgecolor='C1', label=samplelabel)    
    # ax.plot( diag, diag, color='black', linestyle='dashed', alpha=0.5)
    ax.axhline(y=0,color='black',linestyle='dashed',linewidth=1)
        
    deltaZTmax = np.abs( (ZT1-ZT2).max() )
    
    # ax.set_ylabel(r'$\rm \delta (ZT) = (ZT)_{fig} - (ZT)_{TEP}$')
    # ax.set_ylabel(r'$\delta \rm (ZT)$')
    ax.set_ylabel(label)
    


if (1):
    ax = ax6
    

    X = delZT
    # res = stats.probplot(X,dist=stats.norm, plot=ax, rvalue=True)  
    res = stats.probplot(X,dist=stats.norm, plot=None, rvalue=True)  
    
    slope, intercept, rmR2 = res[1]
    R2 = rmR2**2
    def lin_eq(x,slope,intercept):
        return slope*x+intercept
    
    X0, X1 = -2.3, 2.3
    Y0 = lin_eq(X0,slope,intercept)
    Y1 = lin_eq(X1,slope,intercept)
    
    
    ax.scatter( res[0][0], res[0][1], s=20, facecolor='None', edgecolor='C1',label=samplelabel)    
    ax.plot( [X0,X1],[Y0,Y1], color='black',linestyle='solid',linewidth=1)
    ax.text( 0.05, 0.90, r"R$^2$={:.4f}".format(R2), transform=ax.transAxes, fontsize=8 )

    # deltaZTmax = np.abs( (ZT1-ZT2).max() )
    
    # ax.set_ylabel(r'$\rm \delta (ZT) = (ZT)_{fig} - (ZT)_{TEP}$')
    
    # ax.set_title('sample_id={}'.format(sample_id),fontsize=10)
    # ax.set_title('')
    ax.set_xlabel('Theoretical quantiles')    
    ax.set_ylabel(label)
    
    
ax1.set_title("(a)",loc='left')
ax2.set_title("(b)",loc='left')
ax3.set_title("(c)",loc='left')
ax4.set_title("(d)",loc='left')
ax5.set_title("(e)",loc='left')
ax6.set_title("(f)",loc='left')


for ax in [ax1,ax2,ax3,ax4,ax5]:
    ax.set_xlim(300, 600)
    ax.set_xlabel('T (K)')    
    # ax.legend(fontsize=8)

ax1.set_ylim(130,230)
ax2.set_ylim(0,3)
ax3.set_ylim(0.5,1.5)
ax4.set_ylim(0,1.4)
# ax4.set_ylim(diag)
ax5.set_ylim(-0.013, 0.033)
# ax5.set_ylim(-0.03*delZTscale, 0.03*delZTscale)
ax6.set_ylim(-.006,0.033)

for ax in [ax1,ax2,ax3]:
    ax.legend(loc=4,fontsize=8)
ax4.legend(loc=3,fontsize=8)
ax5.legend(loc=4,fontsize=8)
ax6.legend(loc=4,fontsize=8)
# fig.savefig(figure_file0+".png",dpi=300)
# fig.savefig(figure_file +".png",dpi=300)






fig.tight_layout()
plt.show()



fig.savefig(figure_file0+".png",dpi=300)
fig.savefig(figure_file +".png",dpi=300)
# # shutil.copy(figfile1, figfile2) 

