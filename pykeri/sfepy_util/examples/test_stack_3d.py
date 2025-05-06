# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 2018

@author: Jaywan Chung
"""

from sfepy.mesh.mesh_generators import gen_block_mesh

#from pykeri.sfepy_util.merge import merge_block_mesh
from pykeri.sfepy_util.stack import stack_block_mesh
from pykeri.util.timer import Timer

num_grids = 3

t = Timer()

plate = gen_block_mesh([4.,4.,2.], [num_grids]*3, [0.0,0.0, 0.0], name='rect_mesh2', verbose=False)
leg = gen_block_mesh([1.,1.,2.], [num_grids]*3, [0.0,0.0, 0.0], name='rect_mesh2', verbose=False)

leg1 = gen_block_mesh([1.,1.,1.], [num_grids]*3, [+1.0,+1.0, 0.0], name='rect_mesh2', verbose=False)
leg2 = gen_block_mesh([1.,1.,1.], [num_grids]*3, [+1.0,-1.0, 0.0], name='rect_mesh2', verbose=False)
leg3 = gen_block_mesh([1.,1.,1.], [num_grids]*3, [-1.0,+1.0, 0.0], name='rect_mesh2', verbose=False)
leg4 = gen_block_mesh([1.,1.,1.], [num_grids]*3, [-1.0,-1.0, 0.0], name='rect_mesh2', verbose=False)


print(t.passed(), 'sec passed for initialization')

mesh = stack_block_mesh(leg1, 'above', plate)
t.print_passed()
#mesh = stack_block_mesh(leg2, 'above', plate)
mesh = stack_block_mesh(leg2, 'above', mesh)
t.print_passed()
mesh = stack_block_mesh(leg3, 'above', mesh)
t.print_passed()
mesh = stack_block_mesh(leg4, 'above', mesh)
t.print_passed()
#
# try again
mesh = stack_block_mesh(leg2, 'above', mesh)
t.print_passed()
mesh = stack_block_mesh(leg3, 'above', mesh)
t.print_passed()


filename = 'test_stack_3d.vtk'
mesh.write(filename)

from sfepy.postprocess.viewer import Viewer
#view = Viewer('test_stack_Omega.vtk')
view = Viewer(filename)
view(is_wireframe=True, is_scalar_bar=True, opacity=0.5)