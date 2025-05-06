# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 2018

@author: Jaywan Chung

Draws a Thermoelectric Device for test
"""

import numpy as np

from sfepy.mesh.mesh_generators import gen_block_mesh

from pykeri.sfepy_util.stack import stack_block_mesh
from pykeri.util.timer import Timer

t = Timer()

lower_plate = gen_block_mesh([4.,4.,0.2], [3,3,3], [0.0,0.0, 0.0], mat_id=1, name='rect_mesh2', verbose=False)
#lower_plate = gen_block_mesh([4.,4.,0.2], [10,10,3], [0.0,0.0, 0.0], mat_id=1, name='rect_mesh2', verbose=False)
upper_plate = gen_block_mesh([4.,4.,0.2], [3,3,3], [0.0,0.0, 0.0], mat_id=1, name='rect_mesh2', verbose=False)

p_leg_width = 0.8
p_leg_depth = 0.8
p_leg_grid  = 3
n_leg_width = 0.5
n_leg_depth = 0.8
n_leg_grid  = 3
leg_height = 1.0

center_x_vals = [-1.5, -0.5, +0.5, +1.5]
center_y_vals = [-1.5, -0.5, +0.5, +1.5]
nx = len(center_x_vals)
ny = len(center_y_vals)

mesh = lower_plate

total_time = 0.
count = 0

xv, yv = np.meshgrid(center_x_vals, center_y_vals)
is_p_leg = True
for i in range(nx):
    for j in range(ny):
        # treat xv[j,i], yv[j,i]
        leg_center = [xv[j,i], yv[j,i], 0.]
        if is_p_leg:
            leg_mesh = gen_block_mesh([p_leg_width,p_leg_depth,leg_height], [p_leg_grid]*3, \
                                      leg_center, mat_id=0, name='p_leg', verbose=False)
        else:
            leg_mesh = gen_block_mesh([n_leg_width,n_leg_depth,leg_height], [n_leg_grid]*3, \
                                      leg_center, mat_id=2, name='n_leg', verbose=False)
        mesh = stack_block_mesh(leg_mesh, 'above', mesh)
        #mesh = stack_fast_block_mesh(leg_mesh, 'above', mesh)
        passed_time = t.passed()
        count += 1
        print(passed_time, 'sec passed for ', count, 'th leg addition.')
        total_time += passed_time
        is_p_leg = not(is_p_leg)  # toggle leg type
    is_p_leg = not(is_p_leg)  # toggle leg type

mesh = stack_block_mesh(upper_plate, 'above', mesh)
passed_time = t.passed()
total_time += passed_time
print(passed_time, 'sec passed for upper envelope addition')
print(total_time, 'sec passed for mesh generation.')

filename = 'test_TE_device.vtk'
mesh.write(filename)


from sfepy.postprocess.viewer import Viewer
#view = Viewer('test_stack_Omega.vtk')
view = Viewer(filename)
view(is_wireframe=True, is_scalar_bar=True, opacity=0.5)