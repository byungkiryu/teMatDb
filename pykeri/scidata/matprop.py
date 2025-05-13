# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 08:27:22 2017

@author: Jaywan Chung
"""

import numpy as np
from scipy.interpolate import interp1d
from pykeri.scidata.measured import Measured


class MatProp:
    INTERP_LINEAR = 'linear_wo_extrap'
    INTERP_LINEAR_W_CONST_EXTRAP = 'linear_w_const_extrap'
    INTERP_LINEAR_W_ZERO_EXTRAP = 'linear_w_zero_extrap'
    OPT_INTERP = 'interp'
    OPT_EXTEND_LEFT_TO = 'extend_left_to'
    OPT_EXTEND_RIGHT_TO = 'extend_right_to'
    OPT_EXTEND_LEFT_BY = 'extend_left_by'
    OPT_EXTEND_RIGHT_BY = 'extend_right_by'
    default_interp_opt = {OPT_INTERP:INTERP_LINEAR,
                          OPT_EXTEND_LEFT_TO:None,
                          OPT_EXTEND_RIGHT_TO:None,
                          OPT_EXTEND_LEFT_BY:None,
                          OPT_EXTEND_RIGHT_BY:None}
    
    def __init__(self,names,units,raw_data,\
                 interp_opt=default_interp_opt):
        if len(names) != len(units):
            raise ValueError("'names' and 'units' arguments must have the same lengths.")
            
        self.__names = tuple(names)
        self.__units = tuple(units)
        self.__raw_data = tuple( [tuple(item) for item in raw_data] )
        self.set_interp_opt(interp_opt)

        pass
    
    def __call__(self,xs):
        xs = to_real_values(xs,self.__units[:-1])
        return self.__interp_func(xs)
        pass
    
    def __repr__(self):
        repr_str  = 'MatProp(names=' + str(self.__names) + ',\n\t'
        repr_str += 'units=' + str(self.__units) + ',\n\t'
        repr_str += 'raw_data=' + str(self.__raw_data) + ',\n\t'
        repr_str += "interp_opt=" + str(self.__interp_opt) +")"
        return repr_str
    
    def set_interp_opt(self,interp_opt):
        if len(self.__names) == 2:
            x = np.array([item[0] for item in self.__raw_data])
            y = np.array([item[1] for item in self.__raw_data])
            x_at_left_end = np.min(x)
            x_at_right_end = np.max(x)
            y_at_left_end = y[np.argmin(x)]
            y_at_right_end = y[np.argmax(x)]
            if interp_opt.get(MatProp.OPT_EXTEND_LEFT_TO) is not None:
                extended_left_x = interp_opt[MatProp.OPT_EXTEND_LEFT_TO]
                x = np.append(x,[extended_left_x])
                y = np.append(y,[y_at_left_end])
            elif interp_opt.get(MatProp.OPT_EXTEND_LEFT_BY) is not None:
                extended_left_x = x_at_left_end - interp_opt[MatProp.OPT_EXTEND_LEFT_BY]
                x = np.append(x,[extended_left_x])
                y = np.append(y,[y_at_left_end])
            if interp_opt.get(MatProp.OPT_EXTEND_RIGHT_TO) is not None:
                extended_right_x = interp_opt[MatProp.OPT_EXTEND_RIGHT_TO]
                x = np.append(x,[extended_right_x])
                y = np.append(y,[y_at_right_end])
            elif interp_opt.get(MatProp.OPT_EXTEND_RIGHT_BY) is not None:
                extended_right_x = x_at_right_end + interp_opt[MatProp.OPT_EXTEND_RIGHT_BY]
                x = np.append(x,[extended_right_x])
                y = np.append(y,[y_at_right_end])

            if interp_opt[MatProp.OPT_INTERP] == MatProp.INTERP_LINEAR:
                x = tuple( x )
                y = tuple( y )
                #self.__interp_func = interp1d(x,y,kind='linear')
                self.__interp_func = interp1d(x,y,kind='linear')
            elif interp_opt[MatProp.OPT_INTERP] == MatProp.INTERP_LINEAR_W_CONST_EXTRAP:
                x = tuple( x )
                y = tuple( y )
                self.__interp_func = interp1d(x,y,kind='linear', bounds_error=False, fill_value=(x[0], x[-1]))
            elif interp_opt[MatProp.OPT_INTERP] == MatProp.INTERP_LINEAR_W_ZERO_EXTRAP:
                x = tuple( x )
                y = tuple( y )
                self.__interp_func = interp1d(x,y,kind='linear', bounds_error=False, fill_value=(x[0], 0.0))
            else:
                raise ValueError("Invalid interpolation method.")
        else:
            raise ValueError("Sorry we do not support 2D or more dimensions for now.")
        self.__interp_opt = interp_opt.copy()            
    
    def unit(self):   # unit of the output material property
        return self.__units[-1]
    
    def input_units(self):
        return self.__units[:-1]
    
    def names(self):
        return self.__names
    
    def units(self):
        return self.__units
    
    def raw_data(self):
        return self.__raw_data
    
    def raw_input(self,col=0):
        result = []
        for row in self.__raw_data:
            result.append(row[col])
        return tuple(result)
    
    def raw_output(self):
        return self.raw_input(col=-1)
    
    def raw_interval(self,col=0):
        raw = self.raw_input(col)
        return (min(raw), max(raw))
    
    def has_structure(self,names,units):
        if list(names) == list(self.__names):
            if list(units) == list(self.__units):
                return True
        else:
            return False
        
    def to_units(self,new_units):
        rows = self.__raw_data
        units = self.__units
        # compute new raw_data
        is_not_iterable = False
        try:
            _ = iter(rows)
        except TypeError:
            # not a iterable
            rows = (rows,)
            is_not_iterable = True
        try:
            _ = iter(units)
        except TypeError:
            units = (units,)
        result = []
        for row in rows:
            row_item = []
            is_a_single_xp = False
            try:
                _ = iter(row)
            except TypeError:
                row = (row,)
                is_a_single_xp = True
            for idx,col in enumerate(row):
                prev_unit = units[idx]
                new_unit = new_units[idx]
                # exception handling: temperature conversion
                temperature = ['K','degC','°C','degF','°F']
                if (prev_unit in temperature) and (new_unit in temperature):
                    if isinstance(col,Measured):
                        col = col.value
                    col = temperature_conversion(col,prev_unit,new_unit)
                    prev_unit = new_unit
                # usual cases
                if isinstance(col,Measured):
                    col = col.to(new_unit).drop_zero_exponent().value  # unit conversion
                else:
                    col = Measured(col,prev_unit).to(new_unit).drop_zero_exponent().value
                row_item.append(float(col))
            if is_a_single_xp:
                result.append(row_item[0])
            else:
                result.append(tuple(row_item))
        if is_not_iterable:
            result = result[0]
        else:
            result = tuple(result)
        # return the result as a MatProp
        return MatProp(self.__names,new_units,result,interp_opt=self.__interp_opt)
        
    
def to_real_values(xs,units):
    is_not_iterable = False
    try:
        _ = iter(xs)
    except TypeError:
        # not a iterable
        xs = (xs,)
        is_not_iterable = True
    try:
        _ = iter(units)
    except TypeError:
        units = (units,)
    result = []
    for row in xs:
        row_item = []
        is_a_single_xp = False
        try:
            _ = iter(row)
        except TypeError:
            row = (row,)
            is_a_single_xp = True
        for idx,col in enumerate(row):
            default_unit = units[idx]
            if isinstance(col,Measured):
                col = col.to(default_unit).drop_zero_exponent().value  # unit conversion
            row_item.append(float(col))
        if is_a_single_xp:
            result.append(row_item[0])
        else:
            result.append(tuple(row_item))
    if is_not_iterable:
        result = result[0]
    else:
        result = tuple(result)
    return result

def temperature_conversion(value,unit,new_unit):
    if unit in ['degF','°F']:
        if new_unit in ['degF','°F']:
            return value
        elif new_unit in ['degC','°F']:
            return (value-32)*5/9
        elif new_unit == 'K':
            return (value-32)*5/9+273.15
    elif unit in ['degC','°C']:
        if new_unit in ['degF','°F']:
            return (value*9/5)+32
        elif new_unit in ['degC','°C']:
            return value
        elif new_unit == 'K':
            return value+273.15
    elif unit == 'K':
        if new_unit in ['degF','°F']:
            return (value-273.15)*9/5+32
        elif new_unit in ['degC','°C']:
            return value-273.15
        elif new_unit == 'K':
            return value
    raise ValueError("No proper conversion found.")