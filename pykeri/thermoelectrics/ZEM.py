# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 10:02:41 2017

@author: Jaywan Chung
"""

import pandas as pd
from pykeri.scidata.read import read_text, sci_table

def read_ZEM_measurements(filename):
    df = read_text(filename, sep='\t')
    df = df.loc[1:, (0,1,4,5)]    # temp[degC], resistivity[Ohm m], Seebeck[V/K], PF[W/m/K^2]
    df = sci_table(df, 0)
    df = df.apply(pd.to_numeric)       # elements as np.float64
    # degC to Kelvin
    df.iloc[:,0] = df.iloc[:,0] + 273.15
    # rename the columns
    df.columns = ('Temperature [K]', 'Resistivity [Ohm m]', 'Seebeck coeff. [V/K]', 'Power factor [W/m/K^2]')
    return df

def average_measurements(dataframe):
    n_rows = len(dataframe)
    # assign group number (no. measurements)
    df = dataframe.assign( group = [0]*n_rows )
    prev_K = 0
    group_id = 0
    for idx in range(n_rows):
        cur_K = df.iloc[idx,0]
        if cur_K <= prev_K:
            group_id += 1
        df.iloc[idx,4] = group_id
        prev_K = cur_K
    # sort the measurements by temperature
    df = df.sort_values(by=df.columns[0])
    def avg_of_list(lst):
        return sum(lst) / len(lst)
    # compute the average
    set_of_group = set([])
    list_for_avg = []
    avg = []
    for idx in range(n_rows):
        prev_n = len(set_of_group)
        group = df.iloc[idx,-1]
        set_of_group.add( group )
        cur_n = len(set_of_group)
        if cur_n == prev_n:  # group is already complete; compute the average of the previous group
            avg.append( avg_of_list(list_for_avg) )   # append the average
            # clear the set and list
            set_of_group = { group }
            list_for_avg = [ df.iloc[idx,:-1] ]           
        else:
            list_for_avg.append( df.iloc[idx,:-1] )
    avg.append( avg_of_list(list_for_avg) )   # append the average for the last element
    return pd.DataFrame(avg).reset_index(drop=True)
    

def read_ZEM_avg(filename):
    """
    Read a ZEM-3 measurement data and return T,rho,Seebeck,PF.
    If there are several measurements according to temperatures, they are averaged.
    WARNING: all the additional information is discarded.
    """
    df = read_ZEM_measurements(filename)
    df = average_measurements(df)
    return df
    

if __name__ == '__main__':
    filename = 'ZEM-3.txt'
    #df = read_ZEM_3_avg('ZEM-3.txt')
    df = read_ZEM_avg(filename)
    print(df)