# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 16:18:29 2017

@author: Jaywan Chung

Last modified on Oct 10 2017:  use the option "overwrite" instead of "override"
"""

import sqlite3
from pykeri.util.sqlite_util import DB_create_a_table_if_not_exists, \
    DB_create_columns_if_not_exists, DB_read_table, DB_get_col_names
from pykeri.scidata.matprop import MatProp

class MatDB:
    ID = 'id'
    UNIT_POSTFIX = '_unit'
    
    def __init__(self,db_filename):
        self._db_filename = db_filename
    
    def __repr__(self):
        return self.__name__ + "(db_filename="+self._db_filename+")"
    
    def load(self,property_name,id_num):
        tbl_props = property_name
        tbl_units = tbl_props + self.UNIT_POSTFIX

        con = sqlite3.connect(self._db_filename)
        cur = con.cursor()
        
        # load the material properties
        names = DB_get_col_names(cur,tbl_props)[1:]     # skip the ID
        selection = (''.join([name+',' for name in names]))[:-1]
        cur.execute("SELECT "+selection+" FROM "+tbl_props+" WHERE "+self.ID+"="+str(id_num)+";")
        raw_data = cur.fetchall()
        # load the units
        units = self._load_units(cur,tbl_units)
        
        return MatProp(names,units,raw_data)
    
    def save(self,matprop,id_num,overwrite=False):
        names = matprop.names()
        units = matprop.units()
        tbl_props = names[-1]    # the output property is the table name
        tbl_units = tbl_props + self.UNIT_POSTFIX

        con = sqlite3.connect(self._db_filename)
        cur = con.cursor()
        
        self._init_DB(cur,[self.ID]+list(names),tbl_props,['INTEGER']+['REAL']*len(names))
        self._init_DB(cur,names,tbl_units,['TEXT']*len(names))
        
        # check the previous unit
        try:
            prev_units = self._load_units(cur,tbl_units)
        except IndexError:
            self._save_units(cur,units,tbl_units)
            con.commit()
        else:
            # convert the units for the DB form
            units = prev_units
            matprop = matprop.to_units(units)
        # flag for override
        if not overwrite:
            if self._has_item(cur,tbl_props,id_num):  # item already exists, and you do not want to override
                con.close()
                return False   # did NOT save
        else:
            self._delete_item(cur,tbl_props,id_num)   # delete the previous item for override
        # record the data
        question_strg = (''.join(['?,']*(len(names)+1)))[:-1]   # one more for ID
        data = [[id_num]+list(row) for row in matprop.raw_data()]
        cur.executemany("INSERT INTO "+tbl_props+" VALUES ("+question_strg+")", data)
        
        con.commit()
        con.close()
        return True    # DID save
    
    def _init_DB(self,cur,columns,tbl,col_types):
        # create a data table
        DB_create_a_table_if_not_exists(cur,columns,tbl,col_types=col_types)
        DB_create_columns_if_not_exists(cur,columns,tbl,col_types=col_types)
        
    def _save_units(self,cur,units,tbl):
        # update the unit
        unit_strg = (''.join(["'"+unit+"'," for unit in units]))[:-1]
        cur.execute("INSERT INTO "+tbl+" VALUES("+unit_strg+");")
        
    def _load_units(self,cur,tbl):
        rows = DB_read_table(cur,tbl)
        return rows[0]
    
    def _has_item(self,cur,tbl,id_num):
        cur.execute("SELECT * FROM "+tbl+" WHERE "+self.ID+'='+str(id_num)+';')
        rows = cur.fetchall()
        if len(rows)>0:
            return True
        else:
            return False
    
    def _delete_item(self,cur,tbl,id_num):
        # delete the previous item
        cur.execute("DELETE FROM "+tbl+" WHERE "+self.ID+'='+str(id_num)+';')