# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 16:58:07 2017

Shows an example to do the parametric sweep using the distributed DBs

@author: Jaywan Chung

Modified on Wed Oct 11 2017: completed.
"""

## options: modify here
resolution = 3       # how many evenly spaced?
max_num_of_grid_per_interval = 100

# interpolation option
EXTEND_LEFT_TO = 0   # constant extension to the given [K]
EXTEND_RIGHT_BY = 50  # constant extenstion by the given [K] (+[K])

Th = 700 # [K]
Tc = 300 # [K]

L = 3e-3    # 1mm
A = 9e-6    # 1mm x 1mm
min_grid_length = L/100

TEP_DB_FILENAME = 'tep.db'  # do not modify



## ----------------- DO NOT MODIFY BELOW ---------------------

# read the filename
import sys
try:
    filename = str(sys.argv[1])  # first argument is the filename
except:
    raise ValueError("No filename is found; type a DB file to sweep.")
#filename = "stg3_2.db"

# define the solver
from pykeri.thermoelectrics.TEProp import TEProp
from pykeri.scidata.matprop import MatProp
from segment import Segment
from device import Device
from steadystate import SteadyState, NUMERICAL_EFFICIENCY, FORMULA_EFFICIENCY
from environment import Environment
def solver(input_dict):
    mats = []
    for idx in range(resolution):
        param_strg = 'mat{:d}'.format(idx+1)
        mat_id = input_dict.get( param_strg )
        a_mat = TEProp(TEP_DB_FILENAME,mat_id)
        # set interpolation options
        interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
                  MatProp.OPT_EXTEND_LEFT_TO:EXTEND_LEFT_TO,          # ok to 0 Kelvin
                  MatProp.OPT_EXTEND_RIGHT_BY:EXTEND_RIGHT_BY}        # ok to +50 Kelvin from the raw data
        a_mat.set_interp_opt(interp_opt)
        mats.append(a_mat)
    lengths = [L/resolution]*resolution   # evenly spaced

    seg = Segment(lengths, mats, min_grid_length, max_num_of_grid_per_interval=max_num_of_grid_per_interval)
    dev = Device(seg, A)
    env = Environment(Th, Tc)
    
    # solve the PDE
    result = {}
    ss = SteadyState(dev, env, debugging=False)
    # exact maximum efficiency
    try:
        numerical_convergent = ss.solve(given_gamma=SteadyState.GAMMA_MODE_EFF_MAX, quiet=True)
    except ValueError:
        numerical_convergent = False  # Th and Tc are not adequate
    result[NUMERICAL_EFFICIENCY] = ss.get(NUMERICAL_EFFICIENCY) if numerical_convergent else -1
    # formula efficiency
    try:
        formula_convergent = ss.solve(given_I=0, quiet=True)  # for formula efficiency
    except ValueError:
        formula_convergent = False  # Th and Tc are not adequate
    result[FORMULA_EFFICIENCY] = ss.get(FORMULA_EFFICIENCY) if formula_convergent else -1
    
    return result

# run stage
from pykeri.util.paramsweeper import ParamSweeper
swp = ParamSweeper(filename)
swp.solver = solver
swp.sweep(quiet=True)

# show the result
from pykeri.util.sqlite_util import DB_check_table
DB_check_table(filename,swp.TBL_RESULT)
DB_check_table(filename,swp.TBL_PROGRESS)