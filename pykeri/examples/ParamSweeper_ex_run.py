# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 16:58:07 2017

Shows an example to do the parametric sweep using the distributed DBs

@author: Jaywan Chung
"""

# run the parametric sweeper and test

from pykeri.util.paramsweeper import ParamSweeper
from pykeri.util.sqlite_util import DB_check_table

def solver(input_dict):
    A = input_dict.get("A")
    B = input_dict.get("B")
    C = input_dict.get("C")
    return {"sum":A+B+C, "prod":A*B*C}

# run stage
swp = ParamSweeper("test1.db")   # same as swp2.load("test.db")
# swp.info()
swp.solver = solver
swp.sweep(quiet=False)
DB_check_table("test1.db",swp.TBL_RESULT)
DB_check_table("test1.db",swp.TBL_PROGRESS)

swp = ParamSweeper("test2.db")   # same as swp2.load("test.db")
# swp.info()
swp.solver = solver
swp.sweep(quiet=False)
DB_check_table("test2.db",swp.TBL_RESULT)
DB_check_table("test2.db",swp.TBL_PROGRESS)