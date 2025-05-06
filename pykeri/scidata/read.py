# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 16:14:30 2017

@author: Jaywan Chung

modified on Tue Mar 06 2018: add "read_sheet_from_excel_scidata" function.
modified on Mon May 08 2017
"""

import pandas as pd
import numpy as np
from pykeri.util.indexrect import IndexRect
from pykeri.scidata.settings import Settings
#from settings import Settings

def parse_assigns(dataframe):
    """
    Pull out assignment statements from a DataFrame in pandas;
    also returns the altered DataFrame by pulling out the statements.
    Assignment statements are: (i) "A=B", (ii) "A" "=B" or (iii) "A=" "B".
    In these cases, the result list adds a tuple (A,B).
    Returns a Settings object.
    """
    df = dataframe.copy()
    na = np.nan     # null symbol
    result = []    
    if df.isnull().all().all():
        return result, df
    
    rows, cols = np.where( df.notnull() )
    elem_pos = list(zip(rows,cols))
    total_elems = len(elem_pos)
    for i in range(total_elems):
        elem = str(df.iloc[elem_pos[i]]).strip()
        if i+1<total_elems:
            next_elem = str(df.iloc[elem_pos[i+1]]).strip()
        else:
            next_elem = ''
        # fix the insufficient forms of "A=" or "=B"
        if (elem.endswith('=') or next_elem.startswith('=')) and i+1<total_elems: 
            df.iloc[elem_pos[i+1]] = elem + next_elem
            df.iloc[elem_pos[i]] = na
        elif '=' in elem: # extract the assignment statements of the form "A=B=C=..."
            variables = [x.strip() for x in elem.split('=')]
            df.iloc[elem_pos[i]] = na
            rhs = variables.pop()
            if rhs == '': rhs = na
            result += [(lhs,rhs) for lhs in variables]
    return Settings(result), df

def min_bounding_box_containing(dataframe, row, col):
    """
    Return a minimum bounding box containing the given point.
    The bounding box is enclosed by a rectangle of NaN (np.nan)'s.
    Returns for integers describing a rectangle:
        upper left row and column, lower right row and column.
    """
    df = dataframe  # for brevity
    total_rows, total_cols = df.shape
    rect = IndexRect(row,col, row,col)
    rect.set_border(0,0,total_rows-1,total_cols-1)
    while( not rect.is_bounding_box_of(df) ):
        for direction in IndexRect.expand_directions:
            while( not rect.has_bounding_edge(df,direction) ):
                rect.expand(direction)
    return rect

def parse_tables(dataframe):
    """
    Pull out tables from a DataFrame in pandas.
    A table is surrounded by a bounding box;
    a bounding box is a rectangle with edge values are all NaN(np.nan)'s.
    """
    df = dataframe.copy()
    # fix the insufficient forms of "A="
    result = []
    while( df.notnull().any().any() ):
        rows, cols = np.where( df.notnull() )
        rect = min_bounding_box_containing(df, rows[0], cols[0])
        table = rect.mask(df).dropna(how='all',axis=0).dropna(how='all',axis=1)
        result.append(table)
        # erase the extracted table
        rect.fillna(df)
    return result

def read_excel_scidata(filename, ignore_settings=False, ignore_tables=False):
    """
    Read settings (assignment statements) and tables from the given Excel file.
    Returns settings and tables in each sheets and the sheet names;
    'return settings_in_sheets, tables_in_sheets, sheet_names'
    """
    xls_file = pd.ExcelFile(filename) #100 loops, best of 3: 18.8 ms per loop
    sheet_names = xls_file.sheet_names
    settings_in_sheets = []
    tables_in_sheets = []
    for sheet_name in sheet_names:
        df = xls_file.parse(sheet_name,header=None)  #1000 loops, best of 3: 725 µs per loop
        if not ignore_settings:
            settings, altered_df = parse_assigns(df)   #100 loops, best of 3: 8.63 ms per loop
            settings_in_sheets.append(settings)
        else:
            altered_df = df
        if not ignore_tables:
            tables = parse_tables(altered_df)          #1000 loops, best of 3: 469 µs per loop
            tables_in_sheets.append(tables)            
    # process the result
    result = []
    if not ignore_settings:
        result.append(settings_in_sheets)
    if not ignore_tables:
        result.append(tables_in_sheets)
    result.append(sheet_names)
    return result

class SheetNotFoundError(Exception):
    pass

def read_sheet_from_excel_scidata(filename, sheetname, ignore_settings=False, ignore_tables=False):
    """
    Read settings (assignment statements) and tables from the given Excel file and the given sheet name.
    Returns settings and tables in the sheet name;
    'return settings_in_sheet, tables_in_sheet'
    Raise "SheetNotFoundError" if there is no such sheetname.
    """
    xls_file = pd.ExcelFile(filename) #100 loops, best of 3: 18.8 ms per loop
    sheet_names = xls_file.sheet_names
    sheet_found = False
    for sheet_name in sheet_names:
        if sheetname == sheet_name:
            sheet_found = True
            df = xls_file.parse(sheet_name,header=None)  #1000 loops, best of 3: 725 µs per loop
            if not ignore_settings:
                settings, altered_df = parse_assigns(df)   #100 loops, best of 3: 8.63 ms per loop
                settings_in_sheet = settings
            else:
                altered_df = df
            if not ignore_tables:
                tables = parse_tables(altered_df)          #1000 loops, best of 3: 469 µs per loop
                tables_in_sheet = tables
    # process the result
    if not sheet_found:
        raise SheetNotFoundError("No such sheet in the excel file.")
    if not ignore_tables:
        if ignore_settings:
            return tables_in_sheet
        else:
            return settings_in_sheet, tables_in_sheet
    elif not ignore_settings:
        return settings_in_sheet
    else:
        return None

def read_text(filename, sep=None, na=np.nan):
    """
    Read a text file.
    Returns a DataFrame.
    """
    df_dict = {}
    last_col = -1
    cur_line = 0
    with open(filename) as fp:
        for line in fp:
            cur_line += 1
            items = line.rstrip('\r\n').split(sep) # ignore carriage return and split
            num_items = len(items)
            for col in range(last_col+1,num_items):  # add new column with NaN's.
                df_dict[col] = [na] * (cur_line-1)
            for col in range(num_items):   # add the items
                if(items[col] == ''): items[col] = na   # ignore empty string
                df_dict[col].append(items[col])
            for col in range(num_items,last_col+1):
                df_dict[col].append(na)
            if num_items-1 > last_col:
                last_col = num_items-1
    return pd.DataFrame(df_dict)

def read_text_scidata(filename, sep=None, na=np.nan, ignore_settings=False, ignore_tables=False):
    """
    Read settings (assignment statements) and tables from the given text file.
    Returns settings and tables.
    """
    df = read_text(filename, sep=sep, na=na)
    result = []
    if not ignore_settings:
        settings, altered_df = parse_assigns(df)
        result.append(settings)
    else:
        altered_df = df
    if not ignore_tables:
        tables = parse_tables(altered_df)
        result.append(tables)
    return result

def sci_table(dataframe, col_irow, unit_irow=np.nan, discard_irows=[]):
    """
    Organize a scientific table (DataFrame) imposing column labels with
    metric units.
    """
    (num_rows, num_cols) = dataframe.shape
    row_list = list(range(num_rows))
    if np.isscalar(discard_irows):
        discard_irows = list([discard_irows])
    else:
        discard_irows = list(discard_irows)
    for discard_irow in discard_irows:
        row_list.remove(discard_irow)
    if np.isfinite(col_irow):
        col_index = list(dataframe.iloc[col_irow])
        row_list.remove(col_irow)
    else:
        col_index = list(dataframe.columns)
    if np.isfinite(unit_irow):
        row_list.remove(unit_irow)
        unit_index = list(dataframe.iloc[unit_irow])
        for i in range(num_cols):
            unit = '['+str(unit_index[i]).lstrip('(').lstrip('[')\
                              .rstrip(')').rstrip(']')+']'
            col_index[i] = col_index[i] + ' ' + unit
    df = dataframe.iloc[row_list].copy()
    df.columns = col_index
    df.reset_index(drop=True, inplace=True)
    return df