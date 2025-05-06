# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 22:27:01 2017

@author: Jaywan Chung
"""

from pykeri.scidata.matdb import MatDB
from pykeri.scidata.matprop import MatProp
#from pykeri.util.sqlite_util import DB_check_table

property_name = 'Seebeck_coefficient'   # should NOT have white spaces
names = ('temperature',property_name)
units = ('K','uV/K')
raw_data = ((100,50),(200,100),(300,30),(400,50),(500,90))
Seebeck = MatProp(names,units,raw_data)

print("Before save:")
print(Seebeck)

db_filename = 'MatDB_ex.db'

db = MatDB(db_filename)
id_num = 1
if db.save(Seebeck,id_num):
    print("DB Saved.")
else:
    print("Did not save.")

#DB_check_table(db_filename,'Seebeck_unit')

mat = db.load(property_name,id_num)
print("After load:")
print(mat)