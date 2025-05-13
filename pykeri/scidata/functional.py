# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 09:02:49 2017

@author: Jaywan Chung

Last updated on Tue Mar 28 2017
"""

import pandas as pd
import numpy as np

class Functional:
    """
    Functional has a x-y DataFrame which defines a functional y=f(x).
    The class computes the value "y" when "x" is given.
    """
    
    _interp_methods = ['piecewise linear']
    _extrap_methods = ['const', 'no']
    
    def __init__(self, xy_dataframe, interp='piecewise linear', \
                 x_min=np.nan, x_max=np.nan, extrap='const'):
        if isinstance(xy_dataframe, Functional):
            given_functional = xy_dataframe
            for vars in given_functional.__dict__:
                setattr(self,vars, getattr(given_functional,vars))
        else:
            self.set_xy_table(xy_dataframe=xy_dataframe)
            self.set_interp_method(interp)
            self.set_extrap_method(extrap)
            self.set_x_range(x_min=x_min, x_max=x_max)

    def __repr__(self):
        return 'Functional with XY-table:\n' + self._xy_df.__repr__() \
            + "\nwith '" + self._interp + "' interpolation"\
            + "\nand '" + self._extrap + "' extrapolation."
        
    def __str__(self):
        return self._xy_df.__str__()
    
    def __getitem__(self, x):
        return self.at(x)
    
    def at(self, x):
        y = np.nan
        interp_idx = Functional._interp_methods.index(self._interp)
        if interp_idx == 0:  # piecewise linear interpolation
            y = self.piecewise_linear_interp(x)        
        if np.isnan(y):
            extrap_idx = Functional._extrap_methods.index(self._extrap)
            if extrap_idx == 0:  # constant extrapolation
                y = self.const_extrap(x)
            if extrap_idx == 1:  # no extrapolation
                y = self.no_extrap(x)
        return y
    
    def set_xy_table(self, xy_dataframe):
        xy_dataframe = pd.DataFrame(xy_dataframe)
        assert( len(xy_dataframe.columns) == 2 )
        x_col = xy_dataframe.columns[0]
        xy_dataframe = xy_dataframe.dropna()\
            .drop_duplicates(subset=x_col)\
            .sort_values(by=x_col)\
            .reset_index(drop=True).copy()
        self._xy_df = xy_dataframe
        self._x_min_in_df = self._xy_df[x_col].iloc[0]
        self._x_max_in_df = self._xy_df[x_col].iloc[-1]
        
    def eval_xy_table(self, x_list):
        if np.isscalar(x_list):
            x_list = list([x_list])
        else:
            x_list = list(x_list)
        y_list = []
        for x in x_list:
            y_list.append(self.at(x))

        x_col_name = self._xy_df.columns[0]
        y_col_name = self._xy_df.columns[1]
        return pd.DataFrame({x_col_name:x_list, y_col_name:y_list})
        
    def set_interp_method(self, interp):
        assert(interp in Functional._interp_methods)
        self._interp = interp
        
    def set_extrap_method(self, extrap):
        assert(extrap in Functional._extrap_methods)
        self._extrap = extrap
        
    def set_x_range(self, x_min=np.nan, x_max=np.nan):
        if np.isnan(x_min):
            x_min = self._x_min_in_df
        if np.isnan(x_max):
            x_max = self._x_max_in_df
        self._x_min = x_min
        self._x_max = x_max
    
    def dataframe(self):
        return self._xy_df
    
    def plot(self, x_list=np.nan, *args, **kwds):
        x_col = self._xy_df.columns[0]
        if np.isnan(x_list).any():
            self.dataframe().plot(x=x_col, *args,**kwds)
        else:
            self.eval_xy_table(x_list).plot(x=x_col, *args,**kwds)
        
    def piecewise_linear_interp(self,x):
        if (x < self._x_min_in_df) or (x > self._x_max_in_df): # there is no info to process
            return np.nan
        df = self._xy_df  # for brevity
        x_col = df.columns[0]
        (xl,yl) = df.loc[df[x_col]<=x].iloc[-1]
        (xr,yr) = df.loc[df[x_col]>=x].iloc[0]
        if(xl < xr):
            y = (yr-yl)*(x-xl)/(xr-xl)+yl
        else:
            y = yl
        return y
    
    def const_extrap(self,x):
        df = self._xy_df  # for brevity       
        y_col = df.columns[1]
        if (x < self._x_min_in_df):
            return df[y_col].iloc[0]
        elif (x > self._x_max_in_df):
            return df[y_col].iloc[-1]
        else:
            raise ValueError('The x-value is in the interpolation region.')
            
    def no_extrap(self,x):
        return np.nan

if __name__ == '__main__':
    df = pd.DataFrame({'x':[3,2,1,1],'y':[1,2,3,5]})
    func = Functional(df)
    func.plot()