# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 18:00:00 2017

Setup a Parametric Sweeper for TE leg

@author: Jaywan Chung
"""

HEADER = "stg3_"
NUM_DB = 2
# define materials by ids
id_list = [1,2,4]

# setup stage
from pykeri.util.paramsweeper import ParamSweeper
swp = ParamSweeper()
swp.param_by_list("mat1", id_list)
swp.param_by_list("mat2", id_list)
swp.const("mat3", 1)
#swp.param("A", 1, 3)
swp.commit_interval(100)  # sec
swp.info()

swp.generate(filename_header=HEADER,num_DB=NUM_DB)


#from pykeri.util.sqlite_util import DB_check_table
#DB_check_table("stg3_1.db",swp.TBL_PROGRESS)
#DB_check_table("stg3_2.db",swp.TBL_PROGRESS)