# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 14:39:49 2018

Provides functions to stack rectangular elements(=cells);
possible types are '1_2', '2_4', '3_8'.

@author: Jaywan Chung

updated on Sat Mar 17 2018: init "stack_fast_rect_mesh()" and "stack_fast_parallelepiped_mesh()" functions.
updated on Sat Mar 17 2018: complete "stack_rect_mesh()" and "stack_parallelepiped_mesh()" functions.
"""

import numpy as np
from sfepy.discrete.fem.mesh import Mesh

from pykeri.sfepy_util.merge import MeshMergeError
from pykeri.sfepy_util.merge import merge_line_mesh, merge_rect_mesh, merge_parallelepiped_mesh
from pykeri.sfepy_util.blockmesh_util import translate, is_overlapping, get_exterior_vertex_ids


def stack_fast_block_mesh(mesh_to_stack, direction, ground_mesh):
    """Stick two block meshes together.

    Stack the 'mesh_to_stack' on the 'ground_mesh' with along 'direction',
    assuming there is only ONE element group.
    
    Warning: this "fast" method uses a heuristic method; it considers "only the bounding box",
        not precise shape (as it suffices in line mesh case). So be careful.

    Args:
        mesh_to_stack: (sfepy's) Mesh to stack.
        direction: String.
            Use 'left_of'/'x_left_of' or 'right_of'/'x_right_of' for 1D;
                'x_left_of', 'x_right_of', 'y_left_of' or 'y_right_of' for 2D;
                'x_left_of', 'x_right_of', 'y_left_of', 'y_right_of', 'z_left_of'/'below' or 'z_right_of'/'above' for 3D.
        ground_mesh: (sfepy's) Mesh where 'mesh_to_stack' will be added along the direction.
    
    Returns:
        the Mesh constructed by stacking the 'mesh_to_stack' on the 'direction' of 'ground_mesh'.
        
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [0.0,0.0,0.0], name='para_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.,2.], [2,2,2], [0.0,0.0,0.0], name='para_mesh2', verbose=False)
    >>> stack_fast_block_mesh(mesh1, 'below', mesh2)._get_io_data()
    (array([[-1. , -1. , -1. ],
           [-1. , -1. ,  1. ],
           [-1. , -0.5, -1. ],
           ...,
           [ 1. ,  0.5,  1. ],
           [ 1. ,  1. , -1. ],
           [ 1. ,  1. ,  1. ]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[ 0,  8, 11,  2,  1,  9, 12,  3],
           [ 2, 11, 14,  4,  3, 12, 15,  5],
           [ 4, 14, 16,  6,  5, 15, 17,  7],
           [ 8, 18, 21, 11,  9, 19, 22, 12],
           [10, 20, 23, 13, 11, 21, 24, 14],
           [11, 21, 24, 14, 12, 22, 25, 15],
           [14, 24, 26, 16, 15, 25, 27, 17],
           [18, 28, 30, 21, 19, 29, 31, 22],
           [21, 30, 32, 24, 22, 31, 33, 25],
           [24, 32, 34, 26, 25, 33, 35, 27]])], [array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])], ['3_8'])
    """
    desc = mesh_to_stack.descs[0]
    if desc == '1_2':
        return stack_line_mesh(mesh_to_stack, direction, ground_mesh)  # there is no fast method for line mesh
    elif desc == '2_4':
        return stack_fast_rect_mesh(mesh_to_stack, direction, ground_mesh)
    elif desc == '3_8':
        return stack_fast_parallelepiped_mesh(mesh_to_stack, direction, ground_mesh)
    else:
        raise MeshMergeError("Cannot stack a non-block mesh!")


def stack_block_mesh(mesh_to_stack, direction, ground_mesh):
    """Stick two block meshes together.

    Stack the 'mesh_to_stack' on the 'ground_mesh' with along 'direction',
    assuming there is only ONE element group.
    
    Args:
        mesh_to_stack: (sfepy's) Mesh to stack.
        direction: String.
            Use 'left_of'/'x_left_of' or 'right_of'/'x_right_of' for 1D;
                'x_left_of', 'x_right_of', 'y_left_of' or 'y_right_of' for 2D;
                'x_left_of', 'x_right_of', 'y_left_of', 'y_right_of', 'z_left_of'/'below' or 'z_right_of'/'above' for 3D.
        ground_mesh: (sfepy's) Mesh where 'mesh_to_stack' will be added along the direction.
    
    Returns:
        the Mesh constructed by stacking the 'mesh_to_stack' on the 'direction' of 'ground_mesh'.
        
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [0.0,0.0,0.0], name='para_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.,2.], [2,2,2], [0.0,0.0,0.0], name='para_mesh2', verbose=False)
    >>> stack_block_mesh(mesh1, 'below', mesh2)._get_io_data()
    (array([[-1. , -1. , -1. ],
           [-1. , -1. ,  1. ],
           [-1. , -0.5, -1. ],
           ...,
           [ 1. ,  0.5,  1. ],
           [ 1. ,  1. , -1. ],
           [ 1. ,  1. ,  1. ]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[ 0,  8, 11,  2,  1,  9, 12,  3],
           [ 2, 11, 14,  4,  3, 12, 15,  5],
           [ 4, 14, 16,  6,  5, 15, 17,  7],
           [ 8, 18, 21, 11,  9, 19, 22, 12],
           [10, 20, 23, 13, 11, 21, 24, 14],
           [11, 21, 24, 14, 12, 22, 25, 15],
           [14, 24, 26, 16, 15, 25, 27, 17],
           [18, 28, 30, 21, 19, 29, 31, 22],
           [21, 30, 32, 24, 22, 31, 33, 25],
           [24, 32, 34, 26, 25, 33, 35, 27]])], [array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])], ['3_8'])
    """
    desc = mesh_to_stack.descs[0]
    if desc == '1_2':
        return stack_line_mesh(mesh_to_stack, direction, ground_mesh)
    elif desc == '2_4':
        return stack_rect_mesh(mesh_to_stack, direction, ground_mesh)
    elif desc == '3_8':
        return stack_parallelepiped_mesh(mesh_to_stack, direction, ground_mesh)
    else:
        raise MeshMergeError("Cannot stack a non-block mesh!")


def stack_fast_parallelepiped_mesh(mesh_to_stack, direction, ground_mesh):
    """Stick two parallelepiped meshes together.
    
    Stack the 'mesh_to_stack' on the 'ground_mesh' with along 'direction',
    assuming there is only ONE element group.
    
    Warning: this "fast" method uses a heuristic method; it considers "only the bounding box",
        not precise shape (as it suffices in line mesh case). So be careful.

    Performance: slightly faster (0.289 sec --> 0.273 sec)
    
    Args:
        mesh_to_stack: (sfepy's) Mesh to stack.
        direction: String. Use 'x_left_of', 'x_right_of', 'y_left_of', 'y_right_of', 'z_left_of'/'below' or 'z_right_of'/'above'.
        ground_mesh: (sfepy's) Mesh where 'mesh_to_stack' will be added along the direction.
    
    Returns:
        the Mesh constructed by stacking the 'mesh_to_stack' on the 'direction' of 'ground_mesh'.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [0.5,0.5,0.5], name='para_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.,2.], [2,2,2], [0.0,0.0,0.0], name='para_mesh2', verbose=False)
    >>> stack_fast_parallelepiped_mesh(mesh1, 'above', mesh2)._get_io_data()
    (array([[-1., -1., -1.],
           [-1., -1.,  1.],
           [-1.,  0., -1.],
           [-1.,  0.,  1.],
           [-1.,  1., -1.],
           [-1.,  1.,  1.],
           [ 0., -1., -1.],
           [ 0., -1.,  1.],
           [ 0.,  0., -1.],
           [ 0.,  0.,  1.],
           [ 0.,  0.,  2.],
           [ 0.,  1., -1.],
           [ 0.,  1.,  1.],
           [ 0.,  1.,  2.],
           [ 1., -1., -1.],
           [ 1., -1.,  1.],
           [ 1.,  0., -1.],
           [ 1.,  0.,  1.],
           [ 1.,  0.,  2.],
           [ 1.,  1., -1.],
           [ 1.,  1.,  1.],
           [ 1.,  1.,  2.]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[ 0,  6,  8,  2,  1,  7,  9,  3],
           [ 2,  8, 11,  4,  3,  9, 12,  5],
           [ 6, 14, 16,  8,  7, 15, 17,  9],
           [ 8, 16, 19, 11,  9, 17, 20, 12],
           [ 9, 17, 20, 12, 10, 18, 21, 13]])], [array([0, 0, 0, 0, 0])], ['3_8'])
    """
    coords1, ngroups1, conns1, mat_ids1, descs1 = mesh_to_stack._get_io_data()
    coords1 = coords1.copy()
    descs2 = ground_mesh.descs
    # assume there is only ONE group
    if not(len(descs1)==1 and len(descs2)==1):
        raise MeshMergeError("Cannot stack meshes having more than two groups!")
    # assume the element type is a cube: '3_8'
    if not(descs1[0]=='3_8' and descs2[0]=='3_8'):
        raise MeshMergeError("Cannot stack non-parallelepiped meshes!")


    # find the possible shifting positions of 'mesh_to_stack'
    mesh_x_left   = np.min(mesh_to_stack.coors[:,0])
    mesh_x_right  = np.max(mesh_to_stack.coors[:,0])
    mesh_y_left   = np.min(mesh_to_stack.coors[:,1])
    mesh_y_right  = np.max(mesh_to_stack.coors[:,1])
    mesh_z_left   = np.min(mesh_to_stack.coors[:,2])
    mesh_z_right  = np.max(mesh_to_stack.coors[:,2])

    ground_x_coors = ground_mesh.coors[:,0]
    ground_y_coors = ground_mesh.coors[:,1]
    ground_z_coors = ground_mesh.coors[:,2]

    between_x_coors = np.logical_and( mesh_x_left <= ground_x_coors, ground_x_coors <= mesh_x_right )
    between_y_coors = np.logical_and( mesh_y_left <= ground_y_coors, ground_y_coors <= mesh_y_right )
    between_z_coors = np.logical_and( mesh_z_left <= ground_z_coors, ground_z_coors <= mesh_z_right )

    if direction == 'x_left_of':
        need_to_check_coors = ground_mesh.coors[np.logical_and(between_y_coors,between_z_coors), 0]
        if need_to_check_coors.size > 0:
            ground_x_left = np.min(need_to_check_coors)  # fast way
        else:
            ground_x_left = np.min(ground_mesh.coors[:,0])
        mesh_ready = translate(mesh_to_stack, axis='x', start=mesh_x_right, end=ground_x_left)  # make ready the mesh to move
    elif direction == 'x_right_of':
        need_to_check_coors = ground_mesh.coors[np.logical_and(between_y_coors,between_z_coors), 0]
        if need_to_check_coors.size > 0:
            ground_x_right = np.max(need_to_check_coors)  # fast way
        else:
            ground_x_right = np.max(ground_mesh.coors[:,0])
        mesh_ready = translate(mesh_to_stack, axis='x', start=mesh_x_left, end=ground_x_right)  # make ready the mesh to move
    elif direction == 'y_left_of':
        need_to_check_coors = ground_mesh.coors[np.logical_and(between_x_coors,between_z_coors), 1]
        if need_to_check_coors.size > 0:
            ground_y_left = np.min(need_to_check_coors)  # fast way
        else:
            ground_y_left = np.min(ground_mesh.coors[:,1])
        mesh_ready = translate(mesh_to_stack, axis='y', start=mesh_y_right, end=ground_y_left)  # make ready the mesh to move
    elif direction == 'y_right_of':
        need_to_check_coors = ground_mesh.coors[np.logical_and(between_x_coors,between_z_coors), 1]
        if need_to_check_coors.size > 0:
            ground_y_right = np.max(need_to_check_coors)  # fast way
        else:
            ground_y_right = np.max(ground_mesh.coors[:,1])
        mesh_ready = translate(mesh_to_stack, axis='y', start=mesh_y_left, end=ground_y_right)  # make ready the mesh to move
    elif direction == 'z_left_of' or direction == 'below':
        need_to_check_coors = ground_mesh.coors[np.logical_and(between_x_coors,between_y_coors), 2]
        if need_to_check_coors.size > 0:
            ground_z_left = np.min(need_to_check_coors)  # fast way
        else:
            ground_z_left = np.min(ground_mesh.coors[:,2])
        mesh_ready = translate(mesh_to_stack, axis='z', start=mesh_z_right, end=ground_z_left)  # make ready the mesh to move
    elif direction == 'z_right_of' or direction == 'above':
        need_to_check_coors = ground_mesh.coors[np.logical_and(between_x_coors,between_y_coors), 2]
        if need_to_check_coors.size > 0:
            ground_z_right = np.max(need_to_check_coors)  # fast way
        else:
            ground_z_right = np.max(ground_mesh.coors[:,2])
        mesh_ready = translate(mesh_to_stack, axis='z', start=mesh_z_left, end=ground_z_right)  # make ready the mesh to move
    else:
        raise ValueError("Unknown 'direction': use 'x_left_of', 'x_right_of', 'y_left_of', 'y_right_of', 'z_left_of'/'below', or 'z_right_of'/'above' for 3D.")

    stacked_mesh = merge_parallelepiped_mesh(ground_mesh, mesh_ready)
    stacked_mesh.name = '(stack:' + mesh_to_stack.name + '_on_' + ground_mesh.name + ')'

    return stacked_mesh


def stack_parallelepiped_mesh(mesh_to_stack, direction, ground_mesh):
    """Stick two parallelepiped meshes together.
    
    Stack the 'mesh_to_stack' on the 'ground_mesh' with along 'direction',
    assuming there is only ONE element group.
    
    Args:
        mesh_to_stack: (sfepy's) Mesh to stack.
        direction: String. Use 'x_left_of', 'x_right_of', 'y_left_of', 'y_right_of', 'z_left_of'/'below' or 'z_right_of'/'above'.
        ground_mesh: (sfepy's) Mesh where 'mesh_to_stack' will be added along the direction.
    
    Returns:
        the Mesh constructed by stacking the 'mesh_to_stack' on the 'direction' of 'ground_mesh'.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [0.5,0.5,0.5], name='para_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.,2.], [2,2,2], [0.0,0.0,0.0], name='para_mesh2', verbose=False)
    >>> stack_parallelepiped_mesh(mesh1, 'above', mesh2)._get_io_data()
    (array([[-1., -1., -1.],
           [-1., -1.,  1.],
           [-1.,  0., -1.],
           [-1.,  0.,  1.],
           [-1.,  1., -1.],
           [-1.,  1.,  1.],
           [ 0., -1., -1.],
           [ 0., -1.,  1.],
           [ 0.,  0., -1.],
           [ 0.,  0.,  1.],
           [ 0.,  0.,  2.],
           [ 0.,  1., -1.],
           [ 0.,  1.,  1.],
           [ 0.,  1.,  2.],
           [ 1., -1., -1.],
           [ 1., -1.,  1.],
           [ 1.,  0., -1.],
           [ 1.,  0.,  1.],
           [ 1.,  0.,  2.],
           [ 1.,  1., -1.],
           [ 1.,  1.,  1.],
           [ 1.,  1.,  2.]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[ 0,  6,  8,  2,  1,  7,  9,  3],
           [ 2,  8, 11,  4,  3,  9, 12,  5],
           [ 6, 14, 16,  8,  7, 15, 17,  9],
           [ 8, 16, 19, 11,  9, 17, 20, 12],
           [ 9, 17, 20, 12, 10, 18, 21, 13]])], [array([0, 0, 0, 0, 0])], ['3_8'])
    """
    coords1, ngroups1, conns1, mat_ids1, descs1 = mesh_to_stack._get_io_data()
    coords1 = coords1.copy()
    descs2 = ground_mesh.descs
    # assume there is only ONE group
    if not(len(descs1)==1 and len(descs2)==1):
        raise MeshMergeError("Cannot stack meshes having more than two groups!")
    # assume the element type is a cube: '3_8'
    if not(descs1[0]=='3_8' and descs2[0]=='3_8'):
        raise MeshMergeError("Cannot stack non-parallelepiped meshes!")

    # find the possible shifting positions of 'mesh_to_stack'
    ground_exterior_vertex_ids = get_exterior_vertex_ids(ground_mesh)
    if direction == 'x_left_of':
        ground_left = np.min(ground_mesh.coors[:,0])
        mesh_right  = np.max(mesh_to_stack.coors[:,0])
        mesh_ready = translate(mesh_to_stack, axis='x', start=mesh_right, end=ground_left)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,0]
        end_vals2 = ground_left - mesh_ready.coors[mesh_ready_exterior_vertex_ids,0]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )
        start_val = ground_left
        axis = 'x'
    elif direction == 'x_right_of':
        ground_right = np.max(ground_mesh.coors[:,0])
        mesh_left = np.min(mesh_to_stack.coors[:,0])
        mesh_ready = translate(mesh_to_stack, axis='x', start=mesh_left, end=ground_right)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,0]
        end_vals2 = ground_right - mesh_ready.coors[mesh_ready_exterior_vertex_ids,0]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )[::-1]  # in descending order
        start_val = ground_right
        axis = 'x'
    elif direction == 'y_left_of':
        ground_left = np.min(ground_mesh.coors[:,1])
        mesh_right  = np.max(mesh_to_stack.coors[:,1])
        mesh_ready = translate(mesh_to_stack, axis='y', start=mesh_right, end=ground_left)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,1]
        end_vals2 = ground_left - mesh_ready.coors[mesh_ready_exterior_vertex_ids,1]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )
        start_val = ground_left
        axis = 'y'
    elif direction == 'y_right_of':
        ground_right = np.max(ground_mesh.coors[:,1])
        mesh_left = np.min(mesh_to_stack.coors[:,1])
        mesh_ready = translate(mesh_to_stack, axis='y', start=mesh_left, end=ground_right)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,1]
        end_vals2 = ground_right - mesh_ready.coors[mesh_ready_exterior_vertex_ids,1]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )[::-1]  # in descending order
        start_val = ground_right
        axis = 'y'
    elif direction == 'z_left_of' or direction == 'below':
        ground_left = np.min(ground_mesh.coors[:,2])
        mesh_right  = np.max(mesh_to_stack.coors[:,2])
        mesh_ready = translate(mesh_to_stack, axis='z', start=mesh_right, end=ground_left)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,2]
        end_vals2 = ground_left - mesh_ready.coors[mesh_ready_exterior_vertex_ids,2]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )
        start_val = ground_left
        axis = 'z'
    elif direction == 'z_right_of' or direction == 'above':
        ground_right = np.max(ground_mesh.coors[:,2])
        mesh_left = np.min(mesh_to_stack.coors[:,2])
        mesh_ready = translate(mesh_to_stack, axis='z', start=mesh_left, end=ground_right)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,2]
        end_vals2 = ground_right - mesh_ready.coors[mesh_ready_exterior_vertex_ids,2]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )[::-1]  # in descending order
        start_val = ground_right
        axis = 'z'
    else:
        raise ValueError("Unknown 'direction': use 'x_left_of', 'x_right_of', 'y_left_of', 'y_right_of', 'z_left_of'/'below', or 'z_right_of'/'above' for 3D.")

    ok_mesh = mesh_ready
    end_vals = end_vals[1:]  # starting position is always ok
    for end_val in end_vals:
        # move the mesh and test it is ok or not
        moved_mesh = translate(mesh_ready, axis, start_val, end_val)
        if is_overlapping(moved_mesh, ground_mesh, touch_is_overlapping=False):
            break
        else:
            ok_mesh = moved_mesh

    stacked_mesh = merge_parallelepiped_mesh(ground_mesh, ok_mesh)
    stacked_mesh.name = '(stack:' + mesh_to_stack.name + '_on_' + ground_mesh.name + ')'

    return stacked_mesh


def stack_fast_rect_mesh(mesh_to_stack, direction, ground_mesh):
    """Stick two rectnagular meshes together.
    
    Stack the 'mesh_to_stack' on the 'ground_mesh' with along 'direction',
    assuming there is only ONE element group.
    
    Warning: this "fast" method uses a heuristic method; it considers "only the bounding box",
        not precise shape (as it suffices in line mesh case). So be careful.
        
    Performance: slightly faster (0.069 sec --> 0.053 sec)

    Args:
        mesh_to_stack: (sfepy's) Mesh to stack.
        direction: String. Use 'x_left_of', 'x_right_of', 'y_left_of' or 'y_right_of'.
        ground_mesh: (sfepy's) Mesh where 'mesh_to_stack' will be added along the direction.
    
    Returns:
        the Mesh constructed by stacking the 'mesh_to_stack' on the 'direction' of 'ground_mesh'.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.], [2,2], [0.5,0.5], name='rect_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([1.,2.], [2,2], [0.0,0.0], name='rect_mesh2', verbose=False)
    >>> stack_fast_rect_mesh(mesh1, 'x_left_of', mesh2)._get_io_data()
    (array([[-1.5,  0. ],
           [-1.5,  1. ],
           [-0.5, -1. ],
           [-0.5,  0. ],
           [-0.5,  1. ],
           [ 0.5, -1. ],
           [ 0.5,  0. ],
           [ 0.5,  1. ]]), array([0, 0, 0, 0, 0, 0, 0, 0]), [array([[0, 3, 4, 1],
           [2, 5, 6, 3],
           [3, 6, 7, 4]])], [array([0, 0, 0])], ['2_4'])
    >>> stack_fast_rect_mesh(mesh1, 'y_right_of', mesh2)._get_io_data()
    (array([[-0.5, -1. ],
           [-0.5,  1. ],
           [ 0. , -1. ],
           [ 0. ,  1. ],
           [ 0. ,  2. ],
           [ 0.5, -1. ],
           [ 0.5,  1. ],
           [ 0.5,  2. ],
           [ 1. ,  1. ],
           [ 1. ,  2. ]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[0, 2, 3, 1],
           [2, 5, 6, 3],
           [3, 6, 7, 4],
           [6, 8, 9, 7]])], [array([0, 0, 0, 0])], ['2_4'])
    """
    coords1, ngroups1, conns1, mat_ids1, descs1 = mesh_to_stack._get_io_data()
    coords1 = coords1.copy()
    descs2 = ground_mesh.descs
    # assume there is only ONE group
    if not(len(descs1)==1 and len(descs2)==1):
        raise MeshMergeError("Cannot stack meshes having more than two groups!")
    # assume the element type is a rectangle: '2_4'
    if not(descs1[0]=='2_4' and descs2[0]=='2_4'):
        raise MeshMergeError("Cannot stack non-rectangular meshes!")
        
    # find the possible shifting positions of 'mesh_to_stack'
    if direction == 'x_left_of':
        mesh_y_left   = np.min(mesh_to_stack.coors[:,1])
        mesh_y_right  = np.max(mesh_to_stack.coors[:,1])
        mesh_x_right  = np.max(mesh_to_stack.coors[:,0])
        ground_y_coors = ground_mesh.coors[:,1]
        need_to_check_indices = np.logical_and( mesh_y_left <= ground_y_coors, ground_y_coors <= mesh_y_right )
        need_to_check_coors = ground_mesh.coors[need_to_check_indices,0]
        if need_to_check_coors.size > 0:
            ground_x_left = np.min(need_to_check_coors)  # fast way
        else:
            ground_x_left = np.min(ground_mesh.coors[:,0])
        mesh_ready = translate(mesh_to_stack, axis='x', start=mesh_x_right, end=ground_x_left)  # make ready the mesh to move
    elif direction == 'x_right_of':
        mesh_y_left   = np.min(mesh_to_stack.coors[:,1])
        mesh_y_right  = np.max(mesh_to_stack.coors[:,1])
        mesh_x_left  = np.min(mesh_to_stack.coors[:,0])
        ground_y_coors = ground_mesh.coors[:,1]
        need_to_check_indices = np.logical_and( mesh_y_left <= ground_y_coors, ground_y_coors <= mesh_y_right )
        need_to_check_coors = ground_mesh.coors[need_to_check_indices,0]
        if need_to_check_coors.size > 0:
            ground_x_right = np.max(need_to_check_coors)  # fast way
        else:
            ground_x_right = np.max(ground_mesh.coors[:,0])
        mesh_ready = translate(mesh_to_stack, axis='x', start=mesh_x_left, end=ground_x_right)  # make ready the mesh to move
    elif direction == 'y_left_of':
        mesh_x_left   = np.min(mesh_to_stack.coors[:,0])
        mesh_x_right  = np.max(mesh_to_stack.coors[:,0])
        mesh_y_right  = np.max(mesh_to_stack.coors[:,1])
        ground_x_coors = ground_mesh.coors[:,0]
        need_to_check_indices = np.logical_and( mesh_x_left <= ground_x_coors, ground_x_coors <= mesh_x_right )
        need_to_check_coors = ground_mesh.coors[need_to_check_indices,1]
        if need_to_check_coors.size > 0:
            ground_y_left = np.min(need_to_check_coors)  # fast way
        else:
            ground_y_left = np.min(ground_mesh.coors[:,1])
        mesh_ready = translate(mesh_to_stack, axis='y', start=mesh_y_right, end=ground_y_left)  # make ready the mesh to move
    elif direction == 'y_right_of':
        mesh_x_left   = np.min(mesh_to_stack.coors[:,0])
        mesh_x_right  = np.max(mesh_to_stack.coors[:,0])
        mesh_y_left  = np.min(mesh_to_stack.coors[:,1])
        ground_x_coors = ground_mesh.coors[:,0]
        need_to_check_indices = np.logical_and( mesh_x_left <= ground_x_coors, ground_x_coors <= mesh_x_right )
        need_to_check_coors = ground_mesh.coors[need_to_check_indices,1]
        if need_to_check_coors.size > 0:
            ground_y_right = np.max(need_to_check_coors)  # fast way
        else:
            ground_y_right = np.max(ground_mesh.coors[:,1])
        mesh_ready = translate(mesh_to_stack, axis='y', start=mesh_y_left, end=ground_y_right)  # make ready the mesh to move
    else:
        raise ValueError("Unknown 'direction': use 'x_left_of', 'x_right_of', 'y_left_of' or 'y_right_of' for 2D.")

    stacked_mesh = merge_rect_mesh(ground_mesh, mesh_ready)
    stacked_mesh.name = '(stack:' + mesh_to_stack.name + '_on_' + ground_mesh.name + ')'

    return stacked_mesh


def stack_rect_mesh(mesh_to_stack, direction, ground_mesh):
    """Stick two rectnagular meshes together.
    
    Stack the 'mesh_to_stack' on the 'ground_mesh' with along 'direction',
    assuming there is only ONE element group.
        
    Args:
        mesh_to_stack: (sfepy's) Mesh to stack.
        direction: String. Use 'x_left_of', 'x_right_of', 'y_left_of' or 'y_right_of'.
        ground_mesh: (sfepy's) Mesh where 'mesh_to_stack' will be added along the direction.
    
    Returns:
        the Mesh constructed by stacking the 'mesh_to_stack' on the 'direction' of 'ground_mesh'.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.], [2,2], [0.5,0.5], name='rect_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([1.,2.], [2,2], [0.0,0.0], name='rect_mesh2', verbose=False)
    >>> stack_rect_mesh(mesh1, 'x_left_of', mesh2)._get_io_data()
    (array([[-1.5,  0. ],
           [-1.5,  1. ],
           [-0.5, -1. ],
           [-0.5,  0. ],
           [-0.5,  1. ],
           [ 0.5, -1. ],
           [ 0.5,  0. ],
           [ 0.5,  1. ]]), array([0, 0, 0, 0, 0, 0, 0, 0]), [array([[0, 3, 4, 1],
           [2, 5, 6, 3],
           [3, 6, 7, 4]])], [array([0, 0, 0])], ['2_4'])
    >>> stack_rect_mesh(mesh1, 'y_right_of', mesh2)._get_io_data()
    (array([[-0.5, -1. ],
           [-0.5,  1. ],
           [ 0. , -1. ],
           [ 0. ,  1. ],
           [ 0. ,  2. ],
           [ 0.5, -1. ],
           [ 0.5,  1. ],
           [ 0.5,  2. ],
           [ 1. ,  1. ],
           [ 1. ,  2. ]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[0, 2, 3, 1],
           [2, 5, 6, 3],
           [3, 6, 7, 4],
           [6, 8, 9, 7]])], [array([0, 0, 0, 0])], ['2_4'])
    """
    coords1, ngroups1, conns1, mat_ids1, descs1 = mesh_to_stack._get_io_data()
    coords1 = coords1.copy()
    descs2 = ground_mesh.descs
    # assume there is only ONE group
    if not(len(descs1)==1 and len(descs2)==1):
        raise MeshMergeError("Cannot stack meshes having more than two groups!")
    # assume the element type is a rectangle: '2_4'
    if not(descs1[0]=='2_4' and descs2[0]=='2_4'):
        raise MeshMergeError("Cannot stack non-rectangular meshes!")
        
    # find the possible shifting positions of 'mesh_to_stack'
    ground_exterior_vertex_ids = get_exterior_vertex_ids(ground_mesh)
    if direction == 'x_left_of':
        ground_left = np.min(ground_mesh.coors[:,0])
        mesh_right  = np.max(mesh_to_stack.coors[:,0])
        mesh_ready = translate(mesh_to_stack, axis='x', start=mesh_right, end=ground_left)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,0]
        end_vals2 = ground_left - mesh_ready.coors[mesh_ready_exterior_vertex_ids,0]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )
        start_val = ground_left
        axis = 'x'
    elif direction == 'x_right_of':
        ground_right = np.max(ground_mesh.coors[:,0])
        mesh_left = np.min(mesh_to_stack.coors[:,0])
        mesh_ready = translate(mesh_to_stack, axis='x', start=mesh_left, end=ground_right)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,0]
        end_vals2 = ground_right - mesh_ready.coors[mesh_ready_exterior_vertex_ids,0]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )[::-1]  # in descending order
        start_val = ground_right
        axis = 'x'
    elif direction == 'y_left_of':
        ground_left = np.min(ground_mesh.coors[:,1])
        mesh_right  = np.max(mesh_to_stack.coors[:,1])
        mesh_ready = translate(mesh_to_stack, axis='y', start=mesh_right, end=ground_left)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,1]
        end_vals2 = ground_left - mesh_ready.coors[mesh_ready_exterior_vertex_ids,1]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )
        start_val = ground_left
        axis = 'y'
    elif direction == 'y_right_of':
        ground_right = np.max(ground_mesh.coors[:,1])
        mesh_left = np.min(mesh_to_stack.coors[:,1])
        mesh_ready = translate(mesh_to_stack, axis='y', start=mesh_left, end=ground_right)  # make ready the mesh to move
        mesh_ready_exterior_vertex_ids = get_exterior_vertex_ids(mesh_ready)
        end_vals1 = ground_mesh.coors[ground_exterior_vertex_ids,1]
        end_vals2 = ground_right - mesh_ready.coors[mesh_ready_exterior_vertex_ids,1]
        end_vals = np.sort( np.unique( np.concatenate((end_vals1,end_vals2)) ) )[::-1]  # in descending order
        start_val = ground_right
        axis = 'y'
    else:
        raise ValueError("Unknown 'direction': use 'x_left_of', 'x_right_of', 'y_left_of' or 'y_right_of' for 2D.")

    ok_mesh = mesh_ready
    end_vals = end_vals[1:]  # starting position is always ok
    for end_val in end_vals:
        # move the mesh and test it is ok or not
        moved_mesh = translate(mesh_ready, axis, start_val, end_val)
        if is_overlapping(moved_mesh, ground_mesh, touch_is_overlapping=False):
            break
        else:
            ok_mesh = moved_mesh

    stacked_mesh = merge_rect_mesh(ground_mesh, ok_mesh)
    stacked_mesh.name = '(stack:' + mesh_to_stack.name + '_on_' + ground_mesh.name + ')'
    
    return stacked_mesh


def stack_line_mesh(mesh_to_stack, direction, ground_mesh):
    """Stick two line meshes together.
    
    Stack the 'mesh_to_stack' on the 'ground_mesh' with along 'direction',
    assuming there is only ONE element group.
    
    Args:
        mesh_to_stack: (sfepy's) Mesh to stack.
        direction: String. Use 'left_of'/'x_left_of' or 'right_of'/'x_right_of'.
        ground_mesh: (sfepy's) Mesh where 'mesh_to_stack' will be added along the direction.
    
    Returns:
        the Mesh constructed by stacking the 'mesh_to_stack' on the 'direction' of 'ground_mesh'.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh_to_stack = gen_block_mesh([1.], [3], [0.5], name='line_mesh1', verbose=False)
    >>> ground_mesh = gen_block_mesh([2.], [3], [0.2], name='line_mesh2', verbose=False)
    >>> stacked_mesh = stack_line_mesh(mesh_to_stack, 'x_left_of', ground_mesh)
    >>> stacked_mesh._get_io_data()
    (array([[-1.8],
           [-1.3],
           [-0.8],
           [ 0.2],
           [ 1.2]]), array([0, 0, 0, 0, 0]), [array([[0, 1],
           [1, 2],
           [2, 3],
           [3, 4]])], [array([0, 0, 0, 0])], ['1_2'])
    >>> stacked_mesh = stack_line_mesh(mesh_to_stack, 'right_of', ground_mesh)
    >>> stacked_mesh._get_io_data()
    (array([[-0.8],
           [ 0.2],
           [ 1.2],
           [ 1.7],
           [ 2.2]]), array([0, 0, 0, 0, 0]), [array([[0, 1],
           [1, 2],
           [2, 3],
           [3, 4]])], [array([0, 0, 0, 0])], ['1_2'])
    """
    coords1, ngroups1, conns1, mat_ids1, descs1 = mesh_to_stack._get_io_data()
    descs2 = ground_mesh.descs
    # assume there is only ONE group
    if not(len(descs1)==1 and len(descs2)==1):
        raise MeshMergeError("Cannot stack meshes having more than two groups!")
    # assume the element type is a line: '1_2'
    if not(descs1[0]=='1_2' and descs2[0]=='1_2'):
        raise MeshMergeError("Cannot stack non-line meshes!")
    
    # find the right position of the ground mesh
    if direction == 'left_of' or direction == 'x_left_of':
        ground_boundary = np.min(ground_mesh.coors)  # left side
        mesh_boundary  = np.max(mesh_to_stack.coors)  # right side
    elif direction == 'right_of' or direction == 'x_right_of':
        ground_boundary = np.max(ground_mesh.coors)   # right side
        mesh_boundary = np.min(mesh_to_stack.coors)   # left side
    else:
        raise ValueError("Unknown 'direction': use 'left_of'/'x_left_of' or 'right_of'/'x_right_of' for 1D.")
    
    # move the mesh to stack.
    dx = ground_boundary - mesh_boundary
    coords1 = coords1 + dx
    # make sure there is no floating point error
    idx = np.isclose(coords1, ground_boundary)
    coords1[idx] = ground_boundary   # eliminate virtual gap due to floating point error
    
    shifted_mesh = Mesh.from_data(mesh_to_stack.name, coords1, ngroups1, conns1, mat_ids1, descs1)
    stacked_mesh = merge_line_mesh(ground_mesh, shifted_mesh)
    stacked_mesh.name = '(stack:' + mesh_to_stack.name + '_on_' + ground_mesh.name + ')'
    
    return stacked_mesh


if __name__ == '__main__':
    import doctest
    doctest.testmod()