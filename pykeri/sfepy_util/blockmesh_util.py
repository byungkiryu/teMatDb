# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 14:35:52 2018

Gathered several basic functions to treat block meshes.

@author: Jaywan Chung


updated on Sun Mar 18 2018: added "get_exterior_vertex_ids()" function.
updated on Sat Mar 17 2018: (maybe) completed "is_inside()" function.
"""

import numpy as np

from sfepy.discrete.fem.mesh import Mesh


def get_exterior_vertex_ids(block_mesh):
    """
    Returns the coordinate ('coords' of 'block_mesh') indices of exterior vertices,
    assuming the mesh is a block type (desc='1_2', '2_4' or '3_8')
    
    Args:
        block_mesh: (sfepy's) Mesh object. A block type (desc='1_2', '2_4' or '3_8')
    
    Returns:
        a numpy integer array of coordinate indices.

    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> from pykeri.sfepy_util.merge import merge_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.], [2,2], [+0.5,-0.5], name='rect_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([1.,2.], [2,2], [-0.5,+0.0], name='rect_mesh2', verbose=False)
    >>> mesh = merge_block_mesh(mesh1, mesh2)
    >>> mesh._get_io_data()
    (array([[-1., -1.],
           [-1.,  0.],
           [-1.,  1.],
           [ 0., -1.],
           [ 0.,  0.],
           [ 0.,  1.],
           [ 1., -1.],
           [ 1.,  0.]]), array([0, 0, 0, 0, 0, 0, 0, 0]), [array([[0, 3, 4, 1],
           [1, 4, 5, 2],
           [3, 6, 7, 4]])], [array([0, 0, 0])], ['2_4'])
    >>> get_exterior_vertex_ids(mesh)
    array([0, 2, 4, 5, 6, 7])
    >>> mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [+0.5,-0.5,+0.0], name='rect_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([1.,2.,1.], [2,2,2], [-0.5,+0.0,+0.0], name='rect_mesh2', verbose=False)
    >>> mesh = merge_block_mesh(mesh1, mesh2)
    >>> mesh._get_io_data()
    (array([[-1. , -1. , -0.5],
           [-1. , -1. ,  0.5],
           [-1. ,  0. , -0.5],
           [-1. ,  0. ,  0.5],
           [-1. ,  1. , -0.5],
           [-1. ,  1. ,  0.5],
           [ 0. , -1. , -0.5],
           [ 0. , -1. ,  0.5],
           [ 0. ,  0. , -0.5],
           [ 0. ,  0. ,  0.5],
           [ 0. ,  1. , -0.5],
           [ 0. ,  1. ,  0.5],
           [ 1. , -1. , -0.5],
           [ 1. , -1. ,  0.5],
           [ 1. ,  0. , -0.5],
           [ 1. ,  0. ,  0.5]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[ 0,  6,  8,  2,  1,  7,  9,  3],
           [ 2,  8, 10,  4,  3,  9, 11,  5],
           [ 6, 12, 14,  8,  7, 13, 15,  9]])], [array([0, 0, 0])], ['3_8'])
    >>> get_exterior_vertex_ids(mesh)
    array([ 0,  1,  4,  5,  8,  9, 10, 11, 12, 13, 14, 15])
    """
    coords, ngroups, conns, mat_ids, descs = block_mesh._get_io_data()
    desc = descs[0]
    
    if desc == '1_2':
        all_conns = np.reshape(conns, (-1,2))  # ignore node groups
        return np.setxor1d(all_conns[:,0], all_conns[:,1])   # exterior point appears only once in each cell position (left end or right end)
    elif desc == '2_4':
        all_conns = np.reshape(conns, (-1,4))  # ignore node groups
        all_vertex_ids = np.unique(all_conns.reshape(-1))
        exists_at_pos = []
        not_exists_at_pos = []
        for pos in range(4):  # remeber the existence and non-existence of coordinate points in each cell position.
            exists_at_pos.append(all_conns[:,pos])
            not_exists_at_pos.append( np.setdiff1d(all_vertex_ids, all_conns[:,pos]) )
        interior_should_exists_condition = ((0,1),(1,2),(2,3),(3,0),(0,1,2,3))
        interior_vertex_ids = np.array([], dtype=np.int32)
        for condition in interior_should_exists_condition:
            ids_satisfying_condition = all_vertex_ids
            for pos in range(4):
                if pos in condition:
                    ids_satisfying_condition = np.intersect1d(ids_satisfying_condition, exists_at_pos[pos])
                else:
                    ids_satisfying_condition = np.intersect1d(ids_satisfying_condition, not_exists_at_pos[pos])
            interior_vertex_ids = np.union1d(interior_vertex_ids, ids_satisfying_condition)
        return np.setdiff1d(all_vertex_ids, interior_vertex_ids)
    elif desc == '3_8':
        all_conns = np.reshape(conns, (-1,8))  # ignore node groups
        all_vertex_ids = np.unique(all_conns.reshape(-1))
        exists_at_pos = []
        not_exists_at_pos = []
        for pos in range(8):  # remeber the existence and non-existence of coordinate points in each cell position.
            exists_at_pos.append(all_conns[:,pos])
            not_exists_at_pos.append( np.setdiff1d(all_vertex_ids, all_conns[:,pos]) )
        interior_should_exists_condition = ((0,1),(1,2),(2,3),(3,0),
                                            (4,5),(5,6),(6,7),(7,4),
                                            (0,4),(1,5),(2,6),(3,7),
                                            (0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),
                                            (0,1,2,3,4,5,6,7))
        interior_vertex_ids = np.array([])
        for condition in interior_should_exists_condition:
            ids_satisfying_condition = all_vertex_ids
            for pos in range(8):
                if pos in condition:
                    ids_satisfying_condition = np.intersect1d(ids_satisfying_condition, exists_at_pos[pos])
                else:
                    ids_satisfying_condition = np.intersect1d(ids_satisfying_condition, not_exists_at_pos[pos])
            interior_vertex_ids = np.union1d(interior_vertex_ids, ids_satisfying_condition)
        return np.setdiff1d(all_vertex_ids, interior_vertex_ids)
    else:
        raise TypeError("Cannot handle a non-block mesh!")


def translate(mesh, axis, start, end):
    """
    Translate a mesh from the 'start' point to the 'end' point along the 'axis'-direction.

    Args:
        mesh: (sfepy's) Mesh object.
        axis: string. 'x', 'y' or 'z'.
        start: a reference point representing a starting point.
            Can choose freely, independent of the 'mesh'.
        end: the point where the 'start' point arrives.
    
    Returns:
        a translated Mesh object.

    Warning:
        This function handles floating point error.
        So if a coordinate point of 'mesh' is close to 'end' point,
        the coordinate point is replaced by the 'end' point. So the coordinate
        point does not become messy near the edges.
        This is why we use 'start' and 'end' instead of 'end-start' as an input argument.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh = gen_block_mesh([1.,1.,1.], [4,4,4], [0.5,0.5,0.5], name='para_mesh1', verbose=False)
    >>> mesh.coors
    array([[0.        , 0.        , 0.        ],
           [0.        , 0.        , 0.33333333],
           [0.        , 0.        , 0.66666667],
           ...,
           [1.        , 1.        , 0.33333333],
           [1.        , 1.        , 0.66666667],
           [1.        , 1.        , 1.        ]])
    >>> translate(mesh, 'x', 0., 1.).coors
    array([[1.        , 0.        , 0.        ],
           [1.        , 0.        , 0.33333333],
           [1.        , 0.        , 0.66666667],
           ...,
           [2.        , 1.        , 0.33333333],
           [2.        , 1.        , 0.66666667],
           [2.        , 1.        , 1.        ]])
    """
    coords, ngroups, conns, mat_ids, descs = mesh._get_io_data()
    new_coords = coords.copy()

    ds = end-start
    if axis=='x':
        axis_idx = 0
    elif axis=='y':
        axis_idx = 1
    elif axis=='z':
        axis_idx = 2
    
    new_coords[:,axis_idx] += ds
    idx = np.isclose(new_coords[:,axis_idx], end)
    new_coords[idx,axis_idx] = end   # eliminate virtual gap due to floating point error
    
    return Mesh.from_data('translated_mesh', new_coords, ngroups, conns, mat_ids, descs)
    

def is_overlapping(mesh1, mesh2, touch_is_overlapping=False):
    """
    Check whether the given meshes are overlapped or not,
    assuming 'mesh1' and 'mesh2' are block meshes having only one group.

    Args:
        mesh1: (sfepy's) Mesh object. Supposed to be a block mesh and having only one group.
        mesh2: (sfepy's) Mesh object. Supposed to be a block mesh and having only one group.
        touch_is_overlapping: bool, optional (default=False). If this is True,
            a mesh touching another mesh is judged as overlapping.
            
    Returns:
        bool. if 'mesh1' and 'mesh2' are overlapped, returns True.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [0.5,0.5,0.5], name='test_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.,2.], [2,2,2], [0.0,0.0,0.0], name='test_mesh2', verbose=False)
    >>> is_overlapping(mesh1, mesh2)
    True
    >>> mesh3 = gen_block_mesh([1.,1.,1.], [3,3,3], [-0.5,-0.5,-0.5], name='test_mesh3', verbose=False)
    >>> is_overlapping(mesh1, mesh3)
    False
    >>> is_overlapping(mesh1, mesh3, touch_is_overlapping=True)
    True
    """
    coords1, ngroups1, conns1, mat_ids1, descs1 = mesh1._get_io_data()
    coords2, ngroups2, conns2, mat_ids2, descs2 = mesh2._get_io_data()
    if len(descs1)>1 or len(descs2)>1:
        raise TypeError("Cannot handle a mesh having more than one connectivity groups.")
        
    conns1_in_first_group = conns1[0]
    conns2_in_first_group = conns2[0]

    desc2 = descs2[0]
    if desc2 == '3_8':  # 3d case
        conn_pos_left  = 0
        conn_pos_right = 6
    elif desc2 == '2_4':  # 2d case
        conn_pos_left  = 0
        conn_pos_right = 2
    elif desc2 == '1_2':  # 1d case
        conn_pos_left  = 0
        conn_pos_right = 1
    else:
        raise TypeError("Cannot handle the mesh: mesh shape should be '1_2', '2_4' or '3_8'.")

    left_coords_of_mesh2   = coords2[ conns2_in_first_group[:, conn_pos_left] ]
    right_coords_of_mesh2  = coords2[ conns2_in_first_group[:, conn_pos_right] ]
    
    # the idea is to check non-overlapping, instead of overlapping
    if touch_is_overlapping:
        for conn1 in conns1_in_first_group:
            left_coord_of_mesh1  = coords1[ conn1[conn_pos_left] ]
            right_coord_of_mesh1 = coords1[ conn1[conn_pos_right] ]

            test1 = np.less(right_coord_of_mesh1, left_coords_of_mesh2)            
            test2 = np.less(right_coords_of_mesh2, left_coord_of_mesh1)
            not_overlap  = np.logical_or(test1, test2).any(axis=1).all()
            if not not_overlap:
                return True
    else:
        for conn1 in conns1_in_first_group:
            left_coord_of_mesh1  = coords1[ conn1[conn_pos_left] ]
            right_coord_of_mesh1 = coords1[ conn1[conn_pos_right] ]

            test1 = np.less_equal(right_coord_of_mesh1, left_coords_of_mesh2)  # this is different when touch=overlapping            
            test2 = np.less_equal(right_coords_of_mesh2, left_coord_of_mesh1)
            not_overlap  = np.logical_or(test1, test2).any(axis=1).all()
            if not not_overlap:
                return True
    return False


def is_inside(coord, block_mesh, edge_is_inside=False):
    """
    Check whether the given point ('coord') is inside the Mesh object ('mesh'),
    assuming 'mesh' is a block mesh.

    Args:
        coord: a list of floating numbers; the length of the list is equal to the dimension.
            eg: [x] in 1D, [x,y] in 2D, [x,y,z] in 3D.
        block_mesh: (sfepy's) Mesh object. Supposed to be a block mesh.
        edge_is_inside: bool, optional (default=False). if this is True, a point touching
            an edge of the mesh is said to be inside.
    
    Returns:
        bool. if the 'coord' is inside the 'block_mesh', this is True.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh = gen_block_mesh([1.,1.,1.], [4,4,4], [0.0,0.0,0.0], name='test_mesh', verbose=False)
    >>> is_inside([0.0,0.0,0.0], mesh)   # test inside vertex
    True
    >>> is_inside([0.5,0.5,0.5], mesh)   # test outside edge
    False
    >>> is_inside([0.5,0.5,0.5], mesh, edge_is_inside=True)  # test outside edge
    True
    >>> is_inside([0.0,0.0,0.1], mesh)  # test inside edge
    True
    >>> is_inside([0.0,0.0,0.1], mesh, edge_is_inside=True)  # test inside edge
    True
    """
    coords, ngroups, conns, mat_ids, descs = block_mesh._get_io_data()
    dim = len(coord)

    if dim == 3:  # 3d case
        conn_pos_left  = 0
        conn_pos_right = 6
    elif dim == 2:  # 2d case
        conn_pos_left  = 0
        conn_pos_right = 2
    elif dim == 1:  # 1d case
        conn_pos_left  = 0
        conn_pos_right = 1
    else:
        raise TypeError("Cannot handle the given dimension: can handle 1D, 2D, and 3D.")

    num_touch = 0
    for conns_in_a_group in conns:
        indices_left  = conns_in_a_group[:, conn_pos_left]  # different for each dim
        indices_right = conns_in_a_group[:, conn_pos_right]
        left_coords  = coords[indices_left]
        right_coords = coords[indices_right]
        
        strictly_less  = np.less(left_coords, coord).all(axis=1)
        strictly_greater = np.less(coord, right_coords).all(axis=1)
        strictly_inside = np.logical_and(strictly_less, strictly_greater).any()

        if strictly_inside:  # the point is inside of a cell
            return True
        # now the point is on edge or outside
        nonstrictly_less  = np.less_equal(left_coords, coord).all(axis=1)
        nonstrictly_greater = np.less_equal(coord, right_coords).all(axis=1)
        nonstrictly_inside_bool = np.logical_and(nonstrictly_less, nonstrictly_greater)
        
        num_touch += nonstrictly_inside_bool.sum()
        
    # even tough a point is not inside a cell, it can be a vertex inside.
    is_vertex = ((coords == coord).all(axis=1)).any()
    if dim == 3:
        if is_vertex:
            if num_touch == 8:  # inside vertex
                return True
            elif edge_is_inside:
                return True
        else:
            if num_touch == 4:  # inside edge
                return True
        if num_touch > 8:
            raise TypeError("A vertex touches more than 8 cells: not possible. Check the structure of the block mesh.")
    elif dim == 2:
        if is_vertex:
            if num_touch == 4:  # inside vertex
                return True
            elif edge_is_inside:
                return True
        else:
            if num_touch == 2:  # inside edge
                return True
        if num_touch > 4:
            raise TypeError("A vertex touches more than 4 rectangulars: not possible. Check the structure of the block mesh.")
    elif dim == 1:
        if is_vertex:
            if num_touch == 2:  # inside vertex
                return True
            elif edge_is_inside:
                return True
        else:
            if num_touch == 1:  # inside edge
                return True
        if num_touch > 2:
            raise TypeError("A vertex touches more than 2 lines: not possible. Check the structure of the block mesh.")

    return False


def discard_unnecessary_coords(mesh):
    """
    Delete all the unused coordinate points from Mesh (sfepy) object.
    """
    coords, ngroups, conns, mat_ids, descs = mesh._get_io_data()

    if not(len(descs)==1):
        raise ValueError("Cannot handle a mesh having more than two groups!")

    conns_in_first_group = conns[0]  # array of coordinate indices
    
    new_coords = coords.copy()
    new_ngroups = ngroups.copy()
    new_conns_in_first_group = conns_in_first_group.copy()
    
    idx = 0
    for _ in range(len(coords)):
        used_in_conn = False
        for conn in new_conns_in_first_group:
            if idx in conn:
                used_in_conn = True
                break
        if not used_in_conn:   # unnecessary point
            new_coords = np.delete(new_coords, idx, 0)
            new_ngroups = np.delete(new_ngroups, idx)
            new_conns_in_first_group[ new_conns_in_first_group>idx ] -= 1
            idx -= 1
        idx += 1
    
    new_conns = [new_conns_in_first_group]
    new_mesh = Mesh.from_data(mesh.name, new_coords, new_ngroups, new_conns, mat_ids, descs)
    
    return new_mesh


if __name__ == '__main__':
    import doctest
    doctest.testmod()