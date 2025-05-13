# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 12:01:06 2017

@author: Jaywan Chung

Last updated on Tue Mar 28 2017
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pykeri.scidata.read import read_excel_scidata, sci_table
from pykeri.scidata.functional import Functional
#from scidata.settings import Settings


# Ex: read excel data
#settings_in_sheets, tables_in_sheets, sheet_names = read_excel_scidata('test_table.xlsx')
#print('First sheet is ' + sheet_names[0])
#print('Device is ' + str( settings_of('Device',settings_in_sheets[0])[0] ))
#print('Third table is:\n' + str( tables_in_sheets[0][2]))



#tables_in_sheets, sheet_names = read_excel_scidata('TE-MAT-DB-TEST.xlsx', ignore_settings=True)
#print('Fourth table is:\n' + str( tables_in_sheets[0][3]))

#df = read_text('1-Te',sep='\t')
#settings, tables = read_text_scidata('ZEM-3_raw-data',sep='\t')
#settings.describe()
#print(tables[0])


#del sheet_names
if not ('sheet_names' in locals()):
    #tables_in_sheets, sheet_names = read_excel_scidata('TE-MAT-DB-TEST.xlsx', ignore_settings=True)  # 3 secs
    tables_in_sheets, sheet_names = read_excel_scidata('MAT-TEP-DATA_v5_00001-00050.xlsx', ignore_settings=True)  # 3 secs
    #print('First sheet is ' + sheet_names[0])
    #print('Device is ' + str( settings_of('Device',settings_in_sheets[0])[0] ))
    #print('Third table is:\n' + str( tables_in_sheets[0][2]))
    #print('Fourth table is:\n' + str( tables_in_sheets[0][3]))

#table = tables_in_sheets[0][3]
#df = sci_table(table, col_irow=0, unit_irow=1)

# computation
temp = 350
sigma_list = []
alpha_list = []
sheet_list = []
for i in range(len(sheet_names)):
    tables = tables_in_sheets[i]
    table = tables[3]
    df = sci_table(table.iloc[:,range(8)], col_irow=0, unit_irow=1)
    Tsigma_table = df.iloc[:,[0,1]]
    Talpha_table = df.iloc[:,[2,3]]
    if Tsigma_table.any().all() and Talpha_table.any().all():
        sigma = Functional(Tsigma_table, extrap='no')
        alpha = Functional(Talpha_table, extrap='no')
        sigma_list.append(sigma[temp])
        alpha_list.append(alpha[temp])
        sheet_list.append(sheet_names[i])
    else:
        pass
sigma_label = 'Electrical Conductivity [S/m]'
alpha_label = 'Seebeck Coefficient [V/K]'
df = pd.DataFrame({sigma_label:sigma_list, \
                          alpha_label:alpha_list, \
                          'Sheet':sheet_list})

# postprocessing: ignores NaNs
alpha_med = df.median()[1]
upper_df = df.loc[df[alpha_label]>alpha_med].sort_values(by=sigma_label, ascending=False)
lower_df = df.loc[df[alpha_label]<=alpha_med].sort_values(by=sigma_label, ascending=True)
pisarenko = upper_df.append(lower_df).reset_index(drop=True).copy()


print(pisarenko)
# plot
xs = pisarenko[sigma_label]
ys = pisarenko[alpha_label]
#plt.scatter(xs, ys)
#plt.plot(xs, ys)
#plt.xlim([0,300000])
#plt.ylim([-0.0005,+0.0006])
#plt.show()

#pisarenko.to_excel('pisarenko.xlsx', sheet_name='Pisarenko')