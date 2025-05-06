# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 16:58:07 2017

Shows an example to generate DBs for parallel computing

@author: Jaywan Chung
"""

# create a parametric sweeper and test

from pykeri.util.paramsweeper import ParamSweeper
from pykeri.util.sqlite_util import DB_check_table

# setup stage
swp = ParamSweeper()
swp.param("A", 1, 3)
#swp.const("A", 1)
#swp.param_by_list("A", [1])
#swp.param_by_list("B", [400,500,600])
swp.const("B", 400)
#swp.param_by_list("B", [500])
swp.const("C", 300)
swp.commit_interval(100)  # sec
swp.info()

swp.generate(filename_header="test",num_DB=1)

DB_check_table("test1.db",swp.TBL_PROGRESS)
DB_check_table("test2.db",swp.TBL_PROGRESS)