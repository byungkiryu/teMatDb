# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 18:27:25 2018

updated on Mon Mar 19 2018
@author: Jaywan Chung
"""

from sfepy.mesh.mesh_generators import gen_block_mesh
from sfepy.postprocess.viewer import Viewer

from pykeri.sfepy_util.stack import stack_block_mesh
from pykeri.util.timer import Timer


filename = 'test_stack_2d.vtk'

t = Timer()

num_grids = 10

mesh1 = gen_block_mesh([1.,1.], [num_grids,num_grids], [1.0,0.0], mat_id=0, name='rect_mesh1', verbose=False)
mesh2 = gen_block_mesh([1.,2.], [num_grids,num_grids], [0.0,0.0], mat_id=1, name='rect_mesh2', verbose=False)
mesh3 = gen_block_mesh([1.,1.], [num_grids,num_grids], [1.0,0.0], mat_id=2, name='rect_mesh3', verbose=False)

print(t.passed(), 'sec passed for initialization')

# original
mesh = mesh2
t.print_passed()

mesh.write(filename)
view = Viewer(filename)
view(is_wireframe=True, is_scalar_bar=False, filter_names=['node_groups'], ranges={'mat_id': (0,2)})
#view(is_wireframe=True, is_scalar_bar=True, ranges={'mat_id': (0,2)})

# x-axis: left and right
mesh = stack_block_mesh(mesh1, 'x_left_of', mesh2)
t.print_passed()
mesh = stack_block_mesh(mesh1, 'x_right_of', mesh)
t.print_passed()

mesh.write(filename)
view = Viewer(filename)
view(is_wireframe=True, is_scalar_bar=False, filter_names=['node_groups'], ranges={'mat_id': (0,2)})
#view(is_wireframe=True, is_scalar_bar=True, ranges={'mat_id': (0,2)})

# y-axis: left and right
mesh = stack_block_mesh(mesh3, 'y_left_of', mesh)
t.print_passed()
mesh = stack_block_mesh(mesh3, 'y_right_of', mesh)
t.print_passed()

mesh.write(filename)
view = Viewer(filename)
view(is_wireframe=True, is_scalar_bar=False, filter_names=['node_groups'], ranges={'mat_id': (0,2)})
#view(is_wireframe=True, is_scalar_bar=True, ranges={'mat_id': (0,2)})