# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 11:22:51 2018

@author: 정재환
"""

from sfepy.mesh.mesh_generators import gen_block_mesh
from sfepy.postprocess.viewer import Viewer

from pykeri.sfepy_util.merge import merge_block_mesh
from pykeri.sfepy_util.merge import merge_parallelepiped_mesh
from pykeri.sfepy_util.simplify import simplify_parallelepiped_mesh
from pykeri.sfepy_util.stack import stack_block_mesh


fileheader = 'test_simplify_3d_'


mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [0.5,0.5,0], mat_id=1, name='para_mesh1', verbose=False)
mesh2 = gen_block_mesh([2.,2.,2.], [4,4,4], [0,0,0], name='para_mesh2', verbose=False)
#merged_mesh = merge_parallelepiped_mesh(mesh1, mesh2)

mesh = stack_block_mesh(mesh1, 'above', mesh2)




#mesh1 = gen_block_mesh([1.,1.], [3,3], [1.0,0.0], name='rect_mesh1', verbose=False)
#mesh1 = gen_block_mesh([1.,1.], [3,3], [1.0,0.0], name='rect_mesh1', verbose=False)
#mesh2 = gen_block_mesh([1.,2.], [3,3], [0.0,0.0], name='rect_mesh2', verbose=False)
#mesh3 = gen_block_mesh([0.5,0.5], [3,3], [0.25,0.25], mat_id=1, name='diff_mat')

#mesh = mesh2
#mesh = merge_parallelepiped_mesh(mesh3, mesh)

mesh.write(fileheader + 'before.vtk')
print('before:', mesh._get_io_data())

view = Viewer(fileheader + 'before.vtk')
view(is_wireframe=True, is_scalar_bar=True, opacity=0.5)


### after

simple_mesh = simplify_parallelepiped_mesh(mesh)
print('after:', simple_mesh._get_io_data())
simple_mesh.write(fileheader + 'after.vtk')

#domain = FEDomain('test_stack', mesh)
#omega = domain.create_region('Omega', 'all')
#
#domain.save_regions(filename)

view = Viewer(fileheader + 'after.vtk')
view(is_wireframe=True, is_scalar_bar=True, opacity=0.5)