# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 16:13:28 2017

@author: Jaywan Chung
"""

import pandas as pd
import numpy as np
from pykeri.scidata.read import read_text, sci_table

def read_LFA(filename):
    df = read_text(filename, sep=',')
    # ignore header
    rows = np.where(df.iloc[:,0]=='##Results')[0]
    df = df.iloc[rows[0]+1:,:]
    df = sci_table(df, 0)
    # gather all mean values
    rows = np.where(df.iloc[:,0]=='#Mean')[0]
    mean_list = []
    for row in rows:
        row_df = pd.to_numeric( df.iloc[row,[2,4]] )
        row_df.iloc[0] += 273.15   # convert to [K]
        mean_list.append( row_df )
    df = pd.DataFrame(mean_list).reset_index(drop=True)
    df.columns = ('Temperature [K]','Thermal Diffusivity [mm^2/s]')
    return df


if __name__ == '__main__':
    filename = 'LFA.csv'
    df = read_LFA(filename)
    print(df)