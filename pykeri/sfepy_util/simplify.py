# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 09:42:34 2018

Simplify rectangular elements(=cells);
possible types are '1_2', '2_4', '3_8'.

@author: Jaywan Chung
"""

import numpy as np

from sfepy.discrete.fem.mesh import Mesh

from pykeri.sfepy_util.blockmesh_util import discard_unnecessary_coords
from pykeri.sfepy_util.merge import merge_parallelepiped_mesh
from pykeri.sfepy_util.merge import merge_rect_mesh


class MeshSimplifyError(Exception):
    pass


def simplify_parallelepiped_mesh(mesh):
    """Simplify a block mesh.
    
    Eliminate all the redundant cells in the given block mesh,
    assuming there is only ONE element group.
    
    You may use "simplify_line_mesh()", "simplify_rect_mesh()" and "simplify_parallelepiped_mesh()" functions
        when the cell type (line in 1D, rectangular in 2D, parallelepiped in 3D) is known.
    
    Warning: 'mat_id' will be considered; even though two cells are adjacent, if they
        have different 'mat_id's, cells will be intact.
    
    Args:
        mesh: (sfepy's) Mesh with descs=['1_2'] or =['2_4'] or =['3_8'] (block mesh with only one group).
    
    Returns:
        the Mesh simplified.

    """
    desc = mesh.descs[0]
    if desc == '1_2':
        return simplify_line_mesh(mesh)
    elif desc == '2_4':
        return simplify_rect_mesh(mesh)
    elif desc == '3_8':
        return simplify_parallelepiped_mesh(mesh)
    else:
        raise MeshSimplifyError("Cannot simplify a non-block mesh!")



def simplify_parallelepiped_mesh(mesh):
    """Simplify a parallelepiped mesh.
    
    Eliminate all the redundant parallelepiped cells in the given parallelepiped mesh,
    assuming there is only ONE element group.
    
    Warning: 'mat_id' will be considered; even though two cells are adjacent, if they
        have different 'mat_id's, cells will be intact.
    
    Args:
        mesh: (sfepy's) Mesh with descs=['3_8'] (parallelepiped mesh with only one group).
    
    Returns:
        the Mesh simplified.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [0.0,0.0,0.0], name='para_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.,2.], [2,2,2], [0.0,0.0,0.0], name='para_mesh2', verbose=False)
    >>> from pykeri.sfepy_util.merge import merge_parallelepiped_mesh
    >>> merged_mesh = merge_parallelepiped_mesh(mesh1, mesh2)
    >>> merged_mesh._get_io_data()
    (array([[-1. , -1. , -1. ],
           [-1. , -1. , -0.5],
           [-1. , -1. ,  0.5],
           ...,
           [ 1. ,  1. , -0.5],
           [ 1. ,  1. ,  0.5],
           [ 1. ,  1. ,  1. ]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[ 0, 16, 20, ..., 17, 21,  5],
           [ 1, 17, 21, ..., 18, 22,  6],
           [ 2, 18, 22, ..., 19, 23,  7],
           ...,
           [40, 56, 60, ..., 57, 61, 45],
           [41, 57, 61, ..., 58, 62, 46],
           [42, 58, 62, ..., 59, 63, 47]])], [array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0])], ['3_8'])
    >>> simplify_parallelepiped_mesh(merged_mesh)._get_io_data()
    (array([[-1., -1., -1.],
           [-1., -1.,  1.],
           [-1.,  1., -1.],
           [-1.,  1.,  1.],
           [ 1., -1., -1.],
           [ 1., -1.,  1.],
           [ 1.,  1., -1.],
           [ 1.,  1.,  1.]]), array([0, 0, 0, 0, 0, 0, 0, 0]), [array([[0, 4, 6, 2, 1, 5, 7, 3]])], [array([0])], ['3_8'])
    """

    coords, ngroups, conns, mat_ids, descs = mesh._get_io_data()
    # assume there is only ONE group
    if not(len(descs)==1):
        raise MeshSimplifyError("Cannot simplify a mesh having more than two groups!")
    # assume the element type is a parallelepiped: '3_8'
    if not(descs[0]=='3_8'):
        raise MeshSimplifyError("Cannot simplify a non-parallelepiped mesh!")
    # copy items to be altered
    conns_in_first_group = conns[0].copy()
    mat_ids_in_first_group = mat_ids[0].copy()
    
    simplifiable = True
    while simplifiable:
        traveling_conns = conns_in_first_group.copy()
        for idx, conn in enumerate(traveling_conns):
            simplified = False
            # check connectivity
            for other_idx, other_conn in enumerate(traveling_conns):
                if idx == other_idx:  # ignore myself
                    continue
                if (mat_ids_in_first_group[idx] == mat_ids_in_first_group[other_idx]):  # 'mat_id' is also considered
                    if (conn[0] == other_conn[1]) and (conn[3] == other_conn[2]) \
                        and (conn[7] == other_conn[6]) and (conn[4] == other_conn[5]):  # check x_left connectivity
                        conns_in_first_group[idx][0] = other_conn[0]  # stick two meshes
                        conns_in_first_group[idx][3] = other_conn[3]
                        conns_in_first_group[idx][7] = other_conn[7]
                        conns_in_first_group[idx][4] = other_conn[4]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
                    elif (conn[1] == other_conn[0]) and (conn[2] == other_conn[3]) \
                        and (conn[6] == other_conn[7]) and (conn[5] == other_conn[4]):  # check x_right connectivity
                        conns_in_first_group[idx][1] = other_conn[1]  # stick two meshes
                        conns_in_first_group[idx][2] = other_conn[2]
                        conns_in_first_group[idx][6] = other_conn[6]
                        conns_in_first_group[idx][5] = other_conn[5]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
                    elif (conn[0] == other_conn[3]) and (conn[1] == other_conn[2]) \
                        and (conn[5] == other_conn[6]) and (conn[4] == other_conn[7]):  # check y_left connectivity
                        conns_in_first_group[idx][0] = other_conn[0]  # stick two meshes
                        conns_in_first_group[idx][1] = other_conn[1]
                        conns_in_first_group[idx][5] = other_conn[5]
                        conns_in_first_group[idx][4] = other_conn[4]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
                    elif (conn[3] == other_conn[0]) and (conn[2] == other_conn[1]) \
                        and (conn[6] == other_conn[5]) and (conn[7] == other_conn[4]):  # check y_right connectivity
                        conns_in_first_group[idx][3] = other_conn[3]  # stick two meshes
                        conns_in_first_group[idx][2] = other_conn[2]
                        conns_in_first_group[idx][6] = other_conn[6]
                        conns_in_first_group[idx][7] = other_conn[7]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
                    elif (conn[0] == other_conn[4]) and (conn[1] == other_conn[5]) \
                        and (conn[2] == other_conn[6]) and (conn[3] == other_conn[7]):  # check z_left connectivity
                        conns_in_first_group[idx][0] = other_conn[0]  # stick two meshes
                        conns_in_first_group[idx][1] = other_conn[1]
                        conns_in_first_group[idx][2] = other_conn[2]
                        conns_in_first_group[idx][3] = other_conn[3]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
                    elif (conn[4] == other_conn[0]) and (conn[5] == other_conn[1]) \
                        and (conn[6] == other_conn[2]) and (conn[7] == other_conn[3]):  # check z_right connectivity
                        conns_in_first_group[idx][4] = other_conn[4]  # stick two meshes
                        conns_in_first_group[idx][5] = other_conn[5]
                        conns_in_first_group[idx][6] = other_conn[6]
                        conns_in_first_group[idx][7] = other_conn[7]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
            if simplified:
                break
        if not simplified:
            simplifiable = False

    # since the 3D geometry is quite complex, we need additional "merge" process to refine.
    simple_mesh = None
    for conn, mat_id in zip(conns_in_first_group, mat_ids_in_first_group):
        # create a mesh with a single cell
        single_conns = [np.array([conn], dtype=np.int)]
        single_mat_ids = [np.array([mat_id], dtype=np.int)]
        single_mesh = Mesh.from_data('', coords, ngroups, single_conns, single_mat_ids, descs)
        if simple_mesh is not None:
            simple_mesh = merge_parallelepiped_mesh(single_mesh, simple_mesh)
        else:
            simple_mesh = single_mesh

    simple_mesh = discard_unnecessary_coords(simple_mesh)
    simple_mesh.name = '(simplified:' + mesh.name +')'
    
    return simple_mesh


def simplify_rect_mesh(mesh):
    """Simplify a rectangular mesh.
    
    Eliminate all the redundant rectangular cells in the given rectangular mesh,
    assuming there is only ONE element group.
    
    Warning: 'mat_id' will be considered; even though two cells are adjacent, if they
        have different 'mat_id's, cells will be intact.
    
    Args:
        mesh: (sfepy's) Mesh with descs=['2_4'] (rectangular mesh with only one group).
    
    Returns:
        the Mesh simplified.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.], [3,3], [1.0,0.0], name='rect_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([1.,2.], [3,3], [0.0,0.0], name='rect_mesh2', verbose=False)
    >>> from pykeri.sfepy_util.merge import merge_rect_mesh
    >>> merged_mesh = merge_rect_mesh(mesh1, mesh2)
    >>> merged_mesh._get_io_data()
    (array([[-0.5, -1. ],
           [-0.5, -0.5],
           [-0.5,  0. ],
           [-0.5,  0.5],
           [-0.5,  1. ],
           [ 0. , -1. ],
           [ 0. , -0.5],
           [ 0. ,  0. ],
           [ 0. ,  0.5],
           [ 0. ,  1. ],
           [ 0.5, -1. ],
           [ 0.5, -0.5],
           [ 0.5,  0. ],
           [ 0.5,  0.5],
           [ 0.5,  1. ],
           [ 1. , -0.5],
           [ 1. ,  0. ],
           [ 1. ,  0.5],
           [ 1.5, -0.5],
           [ 1.5,  0. ],
           [ 1.5,  0.5]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[ 0,  5,  6,  1],
           [ 1,  6,  7,  2],
           [ 2,  7,  8,  3],
           [ 3,  8,  9,  4],
           [ 5, 10, 11,  6],
           [ 6, 11, 12,  7],
           [ 7, 12, 13,  8],
           [ 8, 13, 14,  9],
           [11, 15, 16, 12],
           [12, 16, 17, 13],
           [15, 18, 19, 16],
           [16, 19, 20, 17]])], [array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])], ['2_4'])
    >>> simplify_rect_mesh(merged_mesh)._get_io_data()
    (array([[-0.5, -1. ],
           [-0.5, -0.5],
           [-0.5,  0.5],
           [-0.5,  1. ],
           [ 0.5, -1. ],
           [ 0.5, -0.5],
           [ 0.5,  0.5],
           [ 0.5,  1. ],
           [ 1.5, -0.5],
           [ 1.5,  0.5]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[0, 4, 5, 1],
           [1, 5, 6, 2],
           [2, 6, 7, 3],
           [5, 8, 9, 6]])], [array([0, 0, 0, 0])], ['2_4'])
    """

    coords, ngroups, conns, mat_ids, descs = mesh._get_io_data()
    # assume there is only ONE group
    if not(len(descs)==1):
        raise MeshSimplifyError("Cannot simplify a mesh having more than two groups!")
    # assume the element type is a rectangular: '2_4'
    if not(descs[0]=='2_4'):
        raise MeshSimplifyError("Cannot simplify a non-rectangular mesh!")
    # copy items to be altered
    conns_in_first_group = conns[0].copy()
    mat_ids_in_first_group = mat_ids[0].copy()
    
    simplifiable = True
    while simplifiable:
        traveling_conns = conns_in_first_group.copy()
        for idx, conn in enumerate(traveling_conns):
            simplified = False
            # check connectivity
            for other_idx, other_conn in enumerate(traveling_conns):
                if idx == other_idx:  # ignore myself
                    continue
                if (mat_ids_in_first_group[idx] == mat_ids_in_first_group[other_idx]):  # 'mat_id' is also considered
                    if (conn[0] == other_conn[1]) and (conn[3] == other_conn[2]):  # check left connectivity
                        conns_in_first_group[idx][0] = other_conn[0]  # stick two meshes
                        conns_in_first_group[idx][3] = other_conn[3]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
                    elif (conn[1] == other_conn[0]) and (conn[2] == other_conn[3]):  # check right connectivity
                        conns_in_first_group[idx][1] = other_conn[1]  # stick two meshes
                        conns_in_first_group[idx][2] = other_conn[2]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
                    elif (conn[3] == other_conn[0]) and (conn[2] == other_conn[1]):  # check up connectivity
                        conns_in_first_group[idx][3] = other_conn[3]  # stick two meshes
                        conns_in_first_group[idx][2] = other_conn[2]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
                    elif (conn[0] == other_conn[3]) and (conn[1] == other_conn[2]):  # check down connectivity
                        conns_in_first_group[idx][0] = other_conn[0]  # stick two meshes
                        conns_in_first_group[idx][1] = other_conn[1]
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
            if simplified:
                break
        if not simplified:
            simplifiable = False

    # since the 2D geometry is quite complex, we need additional "merge" process to refine.
    simple_mesh = None
    for conn, mat_id in zip(conns_in_first_group, mat_ids_in_first_group):
        # create a mesh with a single cell
        single_conns = [np.array([conn], dtype=np.int)]
        single_mat_ids = [np.array([mat_id], dtype=np.int)]
        single_mesh = Mesh.from_data('', coords, ngroups, single_conns, single_mat_ids, descs)
        if simple_mesh is not None:
            simple_mesh = merge_rect_mesh(single_mesh, simple_mesh)
        else:
            simple_mesh = single_mesh

    simple_mesh = discard_unnecessary_coords(simple_mesh)
    simple_mesh.name = '(simplified:' + mesh.name +')'
    
    return simple_mesh
    




def simplify_line_mesh(mesh):
    """Simplify a line mesh.
    
    Eliminate all the redundant lines in the given line mesh,
    assuming there is only ONE element group.
    
    Warning: 'mat_id' will be considered; even though two cells are adjacent, if they
        have different 'mat_id's, cells will be intact.
    
    Args:
        mesh: (sfepy's) Mesh with descs=['1_2'] (line mesh with only one group).
    
    Returns:
        the Mesh simplified.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh = gen_block_mesh([1.], [5], [0.5], name='line_mesh', verbose=False)
    >>> simple_mesh = simplify_line_mesh(mesh)
    >>> simple_mesh._get_io_data()
    (array([[0.],
           [1.]]), array([0, 0]), [array([[0, 1]])], [array([0])], ['1_2'])
    """

    coords, ngroups, conns, mat_ids, descs = mesh._get_io_data()
    # assume there is only ONE group
    if not(len(descs)==1):
        raise MeshSimplifyError("Cannot simplify a mesh having more than two groups!")
    # assume the element type is a line: '1_2'
    if not(descs[0]=='1_2'):
        raise MeshSimplifyError("Cannot simplify a non-line mesh!")
    # copy items to be altered
    conns_in_first_group = conns[0].copy()
    mat_ids_in_first_group = mat_ids[0].copy()
    
    simplifiable = True
    while simplifiable:
        traveling_conns = conns_in_first_group.copy()
        for idx, conn in enumerate(traveling_conns):
            simplified = False
            # check connectivity
            for other_idx, other_conn in enumerate(traveling_conns):
                if idx == other_idx:  # ignore myself
                    continue
                if (mat_ids_in_first_group[idx] == mat_ids_in_first_group[other_idx]):  # 'mat_id' is also considered
                    if (conn[1] == other_conn[0]):  # check right connectivity
                        conns_in_first_group[idx][1] = other_conn[1]  # stick two meshes
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
                    elif (conn[0] == other_conn[1]):  # check left connectivity
                        conns_in_first_group[idx][0] = other_conn[0]  # stick two meshes
                        conns_in_first_group = np.delete(conns_in_first_group, other_idx, 0)  # delete the neighbor
                        mat_ids_in_first_group = np.delete(mat_ids_in_first_group, other_idx)
                        simplified = True
                        break
            if simplified:
                break
        if not simplified:
            simplifiable = False

    simple_conns = [np.array(conns_in_first_group, dtype=np.int)]
    simple_mat_ids = [np.array(mat_ids_in_first_group, dtype=np.int)]
    mesh_name = '(simplified:' + mesh.name +')'
    
    simple_mesh = Mesh.from_data(mesh_name, coords, ngroups, simple_conns, simple_mat_ids, descs)
    simple_mesh = discard_unnecessary_coords(simple_mesh)
    
    return simple_mesh
    


    
if __name__ == '__main__':
    import doctest
    doctest.testmod()