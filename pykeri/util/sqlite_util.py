# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 10:07:39 2017

Custom utilities for SQLite3

@author: Jaywan Chung

Updated on Mon Oct 16 2017: add 'DB_file_fetch_top' function
Updated on Wed Oct 11 2017: add 'DB_table_to_csv' function
"""

import sqlite3

def DB_file_fetch_top(rank, db_filename, table_name, sort_index=-1):
    con = sqlite3.connect(db_filename)
    cur = con.cursor()
    col_names = DB_get_col_names(cur,table_name)
    sort_col = col_names[sort_index]

    cur.execute("SELECT * FROM "+table_name+" ORDER BY "+sort_col+" DESC LIMIT "+str(rank)+";")
    return cur.fetchall()    

def DB_table_to_csv(db_filename,table_name,csv_filename):
    con = sqlite3.connect(db_filename)
    cur = con.cursor()
    col_names = DB_get_col_names(cur,table_name)

    cur.execute("SELECT * FROM "+table_name+";")
    import csv
    with open(csv_filename,'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(col_names)
        for row in cur:
            writer.writerow(row)
    con.close()
    

def DB_check_table(filename,table_name):
    con = sqlite3.connect(filename)
    cur = con.cursor()
    col_names = DB_get_col_names(cur,table_name)

    print("TABLE '"+table_name+"' in "+filename+"=")
    print("   name :", col_names)
    cur.execute("SELECT * FROM "+table_name)
    for idx,row in enumerate(cur):
        print("   row",idx+1,":", row)
#    rows = DB_read_table(cur,table_name)
#    for idx,row in enumerate(rows):
#        print("   row",idx,":", row)
    con.close()
    
def DB_read_table(cur,tbl):
    cur.execute("SELECT * FROM "+tbl)
    return cur.fetchall()

def DB_get_col_names(cur,tbl):
    cur.execute("PRAGMA table_info({});".format(tbl))
    cols = [col_name for rowid,col_name,data_type,can_be_null,default_value,pk in cur.fetchall()]
    return tuple(cols)

def DB_create_a_table_if_not_exists(cur,columns,tbl,col_types):
    columns_and_types_str = ''.join([col+' '+col_type+',' for col,col_type in zip(columns[:-1],col_types[:-1])]) + columns[-1]+' '+col_types[-1]
    cur.execute("CREATE TABLE IF NOT EXISTS "+tbl+"("+columns_and_types_str+")")

def DB_create_columns_if_not_exists(cur,columns,tbl,col_types=[]):
    if not col_types:
        col_types = ["REAL"]*len(columns)
    for column,col_type in zip(columns,col_types):
        DB_create_a_column_if_not_exists(cur,column,tbl,col_type=col_type)    

def DB_create_a_column_if_not_exists(cur,column,tbl,col_type="REAL"):
    if not DB_has_a_column(cur,column,tbl):
        sql = "ALTER TABLE "+tbl+" ADD "+column+" "+col_type
        cur.execute(sql)

def DB_has_a_column(cur,column,tbl):
    cols = DB_get_col_names(cur,tbl)
    if column in cols:
        return True
    else:
        return False