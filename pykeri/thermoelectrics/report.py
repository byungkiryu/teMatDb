# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 17:15:11 2017

@author: Jaywan Chung
"""

from pykeri.thermoelectrics.ZEM import read_ZEM_avg
from pykeri.thermoelectrics.LFA import read_LFA
from pykeri.thermoelectrics.Lorenz import Lo_parabolic_band_approx
from pykeri.scidata.unitlite import unit
import numpy as np
import xlwt

def write_row_vector(worksheet, starting_row, col, row_vec, style=None):
    if style is None:
        for idx, elem in enumerate(row_vec):
            worksheet.write( starting_row+idx, col, elem )
    else:
        for idx, elem in enumerate(row_vec):
                        worksheet.write( starting_row+idx, col, elem, style )

def write_name_and_unit(worksheet, starting_row, col, name_strg, unit_strg, style=None):
    if style is None:
        worksheet.write( starting_row, col, name_strg )
        worksheet.write( starting_row+1, col, '['+unit_strg+']' )
    else:
        worksheet.write( starting_row, col, name_strg, style )
        worksheet.write( starting_row+1, col, '['+unit_strg+']', style )

def report_to_excel(ZEM_raw_filename, LFA_raw_filename, target_excel_filename):
    """If one of ZEM or LFA raw filename is 'None', the report remains blank."""
    ZEM_df = None
    LFA_df = None
    if ZEM_raw_filename is not None:
        ZEM_df = read_ZEM_avg(ZEM_raw_filename)
    if LFA_raw_filename is not None:
        LFA_df = read_LFA(LFA_raw_filename)
    # prepare data and metric unit
    if ZEM_df is not None:
        T = ZEM_df.iloc[:,0]; unit(T, 'K')     # temperature [K]
        R = ZEM_df.iloc[:,1]; unit(R, 'Ω m')   # resistivity [ohm m]
        sigma = np.array( 1 / R, dtype=np.float64)   # electric conductivity [S/m]
        unit(sigma, 'S/m')
        sigma_in_S_per_cm, unit_strg = unit.to(sigma, 'S/cm'); unit(sigma_in_S_per_cm, unit_strg)
        S = ZEM_df.iloc[:,2]; unit(S, 'V/K')   # Seebeck coeff. [V/K]
        S_in_uV_per_K, unit_strg = unit.to(S, 'μV/K'); unit(S_in_uV_per_K, unit_strg)
        # PF = ZEM_df.iloc[:,3]; unit(PF, 'W/m/K^2')  # power factor [W/m/K^2]  ==> S^2*sigma (unit caution)
        Lo = np.array( [Lo_parabolic_band_approx( elem ) for elem in S], dtype=np.float64 ); unit(Lo, 'W Ω/K^2')
        # Ke = Lo * sigma * T; unit(Ke, 'W/m/K')    # electrical thermal conductivity
        if LFA_df is not None:
            # interpolate thermal diffusivity
            xp = LFA_df.iloc[:,0]  # temperature [K]
            fp = LFA_df.iloc[:,1]  # thermal diffusivity [mm^2/s]
            TD = np.interp( T, xp, fp ); unit(TD, 'mm^2/s')  # linear interpolation
            TD, unit_strg = unit.to(TD, 'm^2/s'); unit(TD, unit_strg) # unit conversion
    elif LFA_df is not None:
        # only LFA is available
        T = LFA_df.iloc[:,0]  # temperature [K]
        TD = LFA_df.iloc[:,1]; unit(TD, 'mm^2/s') # thermal diffusivity [mm^2/s]
        TD, unit_strg = unit.to(TD, 'm^2/s'); unit(TD, unit_strg) # unit conversion

    # prepare the excel file
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Thermoelectric Property')
    # write header (name and unit)
    HEADER = [ (0,'T','K'), (1,'σ','S/cm'), (2,'S','μV/K'), (3,'PF','W/m/K^2'), (4,'K','W/m/K'), \
              (5,'Lo','W Ω/K^2'), (6,'Ke','W/m/K'), (7,'KL','W/m/K'), (8,'ZT','1'), (14,'TD','m^2/s') ]
    for col,name,unit_strg in HEADER:
        write_name_and_unit(ws, 0, col, name, unit_strg)
    # report data for ZEM and LFA  (col, var)
    REPORT = [ (0,T) ]
    if ZEM_df is not None:
        REPORT_ZEM = [ (1,sigma_in_S_per_cm), (2,S_in_uV_per_K), (5,Lo) ]        
        REPORT += REPORT_ZEM
    if LFA_df is not None:
        REPORT_LFA = [ (14,TD) ]
        REPORT += REPORT_LFA
    for col,var in REPORT:
        write_row_vector(ws, 2, col, var)
    # add user input
    style = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin')
    ws.write(0,10,'ρ');  ws.write(0,11,0,style); ws.write(0,12, '[g/m^3]' )
    ws.write(1,10,'Cp'); ws.write(1,11,0,style); ws.write(1,12,'[J/g/K]' )
    # add formulas
    size = 0
    if ZEM_df is not None:
        size = len(T)
    elif LFA_df is not None:
        size = len(TD)
    micro = '*0.000001'
    for idx in range(2,2+size):
        s_idx = str(idx+1)     # python and excel have different index system  (python=0 ==> excel=1)
        # PF formula = S^2*sigma
        ws.write(idx,3, xlwt.Formula('($C'+s_idx+micro+')^2*$B'+s_idx+'*100'))
        # K = Thermal conductivity = TD*density*Cp
        ws.write(idx,4, xlwt.Formula('$O'+s_idx+'*$L$1*$L$2'))
        # Ke = electric thermal conductivity = Lo*sigma*T
        ws.write(idx,6, xlwt.Formula('$F'+s_idx+'*$B'+s_idx+'*100*$A'+s_idx))
        # KL = K-Ke = lattice thermal conductivity
        ws.write(idx,7, xlwt.Formula('$E'+s_idx+'-$G'+s_idx))
        # ZT = sigma[S/m]*S[V/K]^2*T/K
        ws.write(idx,8, xlwt.Formula('$B'+s_idx+'*100*($C'+s_idx+micro+')^2*$A'+s_idx+'/$E'+s_idx))
    wb.save(target_excel_filename)


if __name__ == '__main__':
    ZEM_raw_filename = 'ZEM-3.txt'
    LFA_raw_filename = 'LFA.csv'
    report_to_excel(ZEM_raw_filename, LFA_raw_filename, 'ZEM_and_LFA_output.xls')
    report_to_excel(ZEM_raw_filename, None, 'ZEM_only_output.xls')
    report_to_excel(None, LFA_raw_filename, 'LFA_only_output.xls')