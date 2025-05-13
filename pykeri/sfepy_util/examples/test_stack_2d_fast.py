# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 2018

@author: Jaywan Chung

Warning: "stack_fast_block_mesh()" function is a heuristic method using only the bounding boxes;
    to be precise calculation, use "stack_block_mesh()" function.
"""

from sfepy.mesh.mesh_generators import gen_block_mesh

from pykeri.sfepy_util.stack import stack_fast_block_mesh
from pykeri.util.timer import Timer

t = Timer()

num_grids = 10

mesh1 = gen_block_mesh([1.,1.], [num_grids,num_grids], [1.0,0.0], mat_id=0, name='rect_mesh1', verbose=False)
mesh2 = gen_block_mesh([1.,2.], [num_grids,num_grids], [0.0,0.0], mat_id=1, name='rect_mesh2', verbose=False)
mesh3 = gen_block_mesh([1.,1.], [num_grids,num_grids], [1.0,0.0], mat_id=2, name='rect_mesh3', verbose=False)

print(t.passed(), 'sec passed for initialization')

mesh = stack_fast_block_mesh(mesh1, 'x_left_of', mesh2)
t.print_passed()

mesh = stack_fast_block_mesh(mesh1, 'x_right_of', mesh)
t.print_passed()

mesh = stack_fast_block_mesh(mesh3, 'y_left_of', mesh)
t.print_passed()

mesh = stack_fast_block_mesh(mesh3, 'y_right_of', mesh)
t.print_passed()

filename = 'test_stack_2d_fast.vtk'
mesh.write(filename)


from sfepy.postprocess.viewer import Viewer
#view = Viewer('test_stack_Omega.vtk')
view = Viewer(filename)
view(is_wireframe=True, is_scalar_bar=True)