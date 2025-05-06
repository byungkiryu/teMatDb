# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 2018

@author: Jaywan Chung
"""

from sfepy.mesh.mesh_generators import gen_block_mesh

from pykeri.sfepy_util.stack import stack_block_mesh
from pykeri.util.timer import Timer

t = Timer()

plate1 = gen_block_mesh([3.5,3.5,0.1], [3,3,3], [0.0,0.0, 0.0], mat_id=0, name='rect_mesh2', verbose=False)
leg1 = gen_block_mesh([1.,1.,1.], [3,3,3], [+1.0,+1.0, 0.0], mat_id=0, name='rect_mesh2', verbose=False)
leg2 = gen_block_mesh([1.,1.,1.], [3,3,3], [-1.0,-1.0, 0.0], mat_id=0, name='rect_mesh2', verbose=False)
plate2 = gen_block_mesh([3.5,3.5,0.1], [3,3,3], [0.0,0.0, 0.0], mat_id=1, name='rect_mesh2', verbose=False)
leg3 = gen_block_mesh([1.,1.,1.], [3,3,3], [+1.0,-1.0, 0.0], mat_id=1, name='rect_mesh2', verbose=False)
leg4 = gen_block_mesh([1.,1.,1.], [3,3,3], [-1.0,+1.0, 0.0], mat_id=1, name='rect_mesh2', verbose=False)


print(t.passed(), 'sec passed for initialization')

mesh1 = stack_block_mesh(leg1, 'above', plate1)
t.print_passed()

mesh1 = stack_block_mesh(leg2, 'above', mesh1)
t.print_passed()

mesh2 = stack_block_mesh(leg3, 'below', plate2)
t.print_passed()

mesh2 = stack_block_mesh(leg4, 'below', mesh2)
t.print_passed()

# stack two meshes
mesh = stack_block_mesh(mesh2, 'above', mesh1)
t.print_passed()


filename = 'test_stack_3d_ex2.vtk'
mesh.write(filename)

#domain = FEDomain('test_stack', mesh)
#omega = domain.create_region('Omega', 'all')
#
#domain.save_regions(filename)

from sfepy.postprocess.viewer import Viewer
#view = Viewer('test_stack_Omega.vtk')
view = Viewer(filename)
view(is_wireframe=True, is_scalar_bar=True, opacity=0.5)