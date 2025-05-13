# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 17:13:09 2018

Provides functions to merge rectangular elements(=cells);
possible types are '1_2', '2_4', '3_8'.


updated on Mon Mar 19 2018: renewed the function itself; better than before.
updated on Mon Mar 19 2018: start to develop a fast version: failed; not fast
updated on Thu Mar 15 2018: bug fix: merge does not create unnecessary coordinate points; see 'discard_unnecessary_coords()' function.

@author: Jaywan Chung
"""

import numpy as np
from sfepy.discrete.fem.mesh import Mesh


class MeshMergeError(Exception):
    pass


def merge_block_mesh(mesh1, mesh2):
    """
    Merge two block meshes and create one block mesh,
    assuming there is only ONE element group.
    A block mesh can be a line, a rectangular or a parallelepiped.

    Warning: If two meshes have different 'mat_id's in the same region,
        the 'mat_id' of 'mesh2' is imposed.

    Args:
        mesh1: (sfepy's) Mesh object. A block type (desc='1_2','2_4', or '3_8') having only one element group.
        mesh2: (sfepy's) Mesh object. A block type (desc='1_2','2_4', or '3_8') having only one element group.
        
    Returns:
        merged_mesh: (sfepy's) Mesh object. Merged block mesh (desc='1_2','2_4', or '3_8').
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.], [3], [0.5], mat_id=0, name='line_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.], [3], [0.2], mat_id=1, name='line_mesh2', verbose=False)
    >>> merged_mesh = merge_block_mesh(mesh1, mesh2)
    >>> merged_mesh._get_io_data()
    (array([[-0.8],
           [ 0. ],
           [ 0.2],
           [ 0.5],
           [ 1. ],
           [ 1.2]]), array([0, 0, 0, 0, 0, 0]), [array([[0, 1],
           [1, 2],
           [2, 3],
           [3, 4],
           [4, 5]])], [array([1, 1, 1, 1, 1])], ['1_2'])
    """
    desc = mesh1.descs[0]
    if desc == '1_2':
        return merge_line_mesh(mesh1, mesh2)
    elif desc == '2_4':
        return merge_rect_mesh(mesh1, mesh2)
    elif desc == '3_8':
        return merge_parallelepiped_mesh(mesh1, mesh2)
    else:
        raise MeshMergeError("Cannot merge non-block meshes!")


def merge_parallelepiped_mesh(mesh1, mesh2):
    """
    Merge two parallelepiped meshes and create one mesh,
    assuming there is only ONE element group.

    Warning: If two meshes have different 'mat_id's in the same region,
        the 'mat_id' of 'mesh2' is imposed.

    Args:
        mesh1: (sfepy's) Mesh object. A parallelepiped type (desc='3_8') having only one element group.
        mesh2: (sfepy's) Mesh object. A parallelepiped type (desc='3_8') having only one element group.
        
    Returns:
        merged_mesh: (sfepy's) Mesh object. Merged parallelepiped mesh (desc='3_8').

    Examples:
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [0.5,0.5,0.5], mat_id=0, name='para_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.,2.], [2,2,2], [0.2,0.2,0.2], mat_id=1, name='para_mesh2', verbose=False)
    >>> merged_mesh = merge_parallelepiped_mesh(mesh1, mesh2)
    >>> merged_mesh._get_io_data()
    (array([[-0.8, -0.8, -0.8],
           [-0.8, -0.8,  0. ],
           [-0.8, -0.8,  1. ],
           ...,
           [ 1.2,  1.2,  0. ],
           [ 1.2,  1.2,  1. ],
           [ 1.2,  1.2,  1.2]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[ 0, 16, 20, ..., 17, 21,  5],
           [ 1, 17, 21, ..., 18, 22,  6],
           [ 2, 18, 22, ..., 19, 23,  7],
           ...,
           [40, 56, 60, ..., 57, 61, 45],
           [41, 57, 61, ..., 58, 62, 46],
           [42, 58, 62, ..., 59, 63, 47]])], [array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           1, 1, 1, 1, 1])], ['3_8'])
    """
    coords1, ngroups1, conns1, mat_ids1, descs1 = mesh1._get_io_data()
    coords2, ngroups2, conns2, mat_ids2, descs2 = mesh2._get_io_data()
    # assume there is only ONE group
    if not(len(descs1)==1 and len(descs2)==1):
        raise MeshMergeError("Cannot merge more than two groups!")
    # assume the element type is a cube: '3_8'
    if not(descs1[0]=='3_8' and descs2[0]=='3_8'):
        raise MeshMergeError("Cannot merge non-parallelepiped meshes!")
    descs = ['3_8']
    
    blocks1 = conns_to_blocks(conns1[0], coords1)
    blocks2 = conns_to_blocks(conns2[0], coords2)
    
    # check overlapping blocks
    id_pairs = where_overlapping_blocks(blocks1, blocks2, touch_is_overlapping=True)
    
    blocks1_with_mat_ids = np.hstack( (blocks1, mat_ids1[0].reshape(-1,1)) )
    blocks2_with_mat_ids = np.hstack( (blocks2, mat_ids2[0].reshape(-1,1)) )

    # cut the plane along which overlapping occurs
    for id1, id2 in id_pairs:
        x_left_block1, x_right_block1, y_left_block1, y_right_block1, z_left_block1, z_right_block1 = blocks1[id1]
        x_left_block2, x_right_block2, y_left_block2, y_right_block2, z_left_block2, z_right_block2 = blocks2[id2]
        
        ordering1 = [[x_left_block1, x_left_block2,  x_right_block1, 'x'],  # depends on dimension
                     [x_left_block1, x_right_block2, x_right_block1, 'x'],
                     [y_left_block1, y_left_block2,  y_right_block1, 'y'],
                     [y_left_block1, y_right_block2, y_right_block1, 'y'],
                     [z_left_block1, z_left_block2,  z_right_block1, 'z'],
                     [z_left_block1, z_right_block2, z_right_block1, 'z']]
        ordering2 = [[x_left_block2, x_left_block1,  x_right_block2, 'x'],
                     [x_left_block2, x_right_block1, x_right_block2, 'x'],
                     [y_left_block2, y_left_block1,  y_right_block2, 'y'],
                     [y_left_block2, y_right_block1, y_right_block2, 'y'],
                     [z_left_block2, z_left_block1,  z_right_block2, 'z'],
                     [z_left_block2, z_right_block1, z_right_block2, 'z']]
        
        for left_coord, middle_coord, right_coord, normal_direction in ordering1:
            if left_coord < middle_coord < right_coord:
                blocks1_with_mat_ids = cut_plane_blocks(blocks1_with_mat_ids, normal_direction, middle_coord)

        for left_coord, middle_coord, right_coord, normal_direction in ordering2:
            if left_coord < middle_coord < right_coord:
                blocks2_with_mat_ids = cut_plane_blocks(blocks2_with_mat_ids, normal_direction, middle_coord)
    
    # discard the same regions in 'blocks1'   # Tue Mar 20 2018
    only_in_blocks1 = is_in_setdiff2d( blocks1_with_mat_ids[:,:-1], blocks2_with_mat_ids[:,:-1] )
    if only_in_blocks1.any():
        all_blocks_with_mat_ids = np.concatenate( (blocks1_with_mat_ids[only_in_blocks1], blocks2_with_mat_ids) )
    else:
        all_blocks_with_mat_ids = blocks2_with_mat_ids.copy()
    # sort the blocks
    k = all_blocks_with_mat_ids
    all_blocks_with_mat_ids = k[np.lexsort((k[:,5],k[:,4], k[:,3],k[:,2],k[:,1],k[:,0]))]

    ## depends on dimension
    node1_coords = all_blocks_with_mat_ids[:,[0,2,4]]   # [x_left, y_left, z_left]
    node2_coords = all_blocks_with_mat_ids[:,[1,2,4]]   # [x_right,y_left, z_left]
    node3_coords = all_blocks_with_mat_ids[:,[1,3,4]]   # [x_right,y_right,z_left]
    node4_coords = all_blocks_with_mat_ids[:,[0,3,4]]   # [x_left, y_right,z_left]
    node5_coords = all_blocks_with_mat_ids[:,[0,2,5]]   # [x_left, y_left, z_right]
    node6_coords = all_blocks_with_mat_ids[:,[1,2,5]]   # [x_right,y_left, z_right]
    node7_coords = all_blocks_with_mat_ids[:,[1,3,5]]   # [x_right,y_right,z_right]
    node8_coords = all_blocks_with_mat_ids[:,[0,3,5]]   # [x_left, y_right,z_right]
    
    merged_coords = np.unique( np.concatenate((node1_coords, node2_coords, node3_coords, node4_coords, \
                                               node5_coords, node6_coords, node7_coords, node8_coords)), axis=0 )  # sorted automatically
    merged_ngroups = [ngroups1[0]] * len(merged_coords)  # assuming there is only one element group
    # evaluate merged conns
    merged_conns = np.array([], dtype=np.int32).reshape(-1,8)   # [node1,...,node8]
    for block in all_blocks_with_mat_ids:
        node1 = [block[0], block[2], block[4]]
        node2 = [block[1], block[2], block[4]]
        node3 = [block[1], block[3], block[4]]
        node4 = [block[0], block[3], block[4]]
        node5 = [block[0], block[2], block[5]]
        node6 = [block[1], block[2], block[5]]
        node7 = [block[1], block[3], block[5]]
        node8 = [block[0], block[3], block[5]]
        
        node1_idx = np.argmax( (merged_coords == node1).all(axis=1) )
        node2_idx = np.argmax( (merged_coords == node2).all(axis=1) )
        node3_idx = np.argmax( (merged_coords == node3).all(axis=1) )
        node4_idx = np.argmax( (merged_coords == node4).all(axis=1) )
        node5_idx = np.argmax( (merged_coords == node5).all(axis=1) )
        node6_idx = np.argmax( (merged_coords == node6).all(axis=1) )
        node7_idx = np.argmax( (merged_coords == node7).all(axis=1) )
        node8_idx = np.argmax( (merged_coords == node8).all(axis=1) )

        merged_conns = np.append( merged_conns, [[node1_idx, node2_idx, node3_idx, node4_idx, \
                                                  node5_idx, node6_idx, node7_idx, node8_idx, ]], axis=0 )
    merged_conns = [merged_conns]  # first group
    merged_mat_ids = [all_blocks_with_mat_ids[:,-1].astype(np.int32)]
    merged_name = '(merge:' + mesh1.name + '_and_' + mesh2.name +')'

    return Mesh.from_data(merged_name, merged_coords, merged_ngroups, merged_conns, merged_mat_ids, descs)
    

def merge_rect_mesh(mesh1, mesh2):
    """
    Merge two rectangular meshes and create one rectangular mesh,
    assuming there is only ONE element group.

    Warning: If two meshes have different 'mat_id's in the same region,
        the 'mat_id' of 'mesh2' is imposed.

    Args:
        mesh1: (sfepy's) Mesh object. A rectangular type (desc='2_4') having only one element group.
        mesh2: (sfepy's) Mesh object. A rectangular type (desc='2_4') having only one element group.
        
    Returns:
        merged_mesh: (sfepy's) Mesh object. Merged rectangular mesh (desc='2_4').

    Examples:    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.], [2,2], [0.5,0.5], mat_id=0, name='rect_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.], [2,2], [0.2,0.2], mat_id=1, name='rect_mesh2', verbose=False)
    >>> merged_mesh = merge_rect_mesh(mesh1, mesh2)
    >>> merged_mesh._get_io_data()
    (array([[-0.8, -0.8],
           [-0.8,  0. ],
           [-0.8,  1. ],
           [-0.8,  1.2],
           [ 0. , -0.8],
           [ 0. ,  0. ],
           [ 0. ,  1. ],
           [ 0. ,  1.2],
           [ 1. , -0.8],
           [ 1. ,  0. ],
           [ 1. ,  1. ],
           [ 1. ,  1.2],
           [ 1.2, -0.8],
           [ 1.2,  0. ],
           [ 1.2,  1. ],
           [ 1.2,  1.2]]), array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), [array([[ 0,  4,  5,  1],
           [ 1,  5,  6,  2],
           [ 2,  6,  7,  3],
           [ 4,  8,  9,  5],
           [ 5,  9, 10,  6],
           [ 6, 10, 11,  7],
           [ 8, 12, 13,  9],
           [ 9, 13, 14, 10],
           [10, 14, 15, 11]])], [array([1, 1, 1, 1, 1, 1, 1, 1, 1])], ['2_4'])
    """
    coords1, ngroups1, conns1, mat_ids1, descs1 = mesh1._get_io_data()
    coords2, ngroups2, conns2, mat_ids2, descs2 = mesh2._get_io_data()
    # assume there is only ONE group
    if not(len(descs1)==1 and len(descs2)==1):
        raise MeshMergeError("Cannot merge more than two groups!")
    # assume the element type is a rectangle: '2_4'
    if not(descs1[0]=='2_4' and descs2[0]=='2_4'):
        raise MeshMergeError("Cannot merge non-rectangular meshes!")
    descs = ['2_4']
    
    blocks1 = conns_to_blocks(conns1[0], coords1)
    blocks2 = conns_to_blocks(conns2[0], coords2)
    
    # check overlapping blocks
    id_pairs = where_overlapping_blocks(blocks1, blocks2, touch_is_overlapping=True)
    
    blocks1_with_mat_ids = np.hstack( (blocks1, mat_ids1[0].reshape(-1,1)) )
    blocks2_with_mat_ids = np.hstack( (blocks2, mat_ids2[0].reshape(-1,1)) )

    # cut the plane along which overlapping occurs
    for id1, id2 in id_pairs:
        x_left_block1, x_right_block1, y_left_block1, y_right_block1 = blocks1[id1]
        x_left_block2, x_right_block2, y_left_block2, y_right_block2 = blocks2[id2]
        
        ordering1 = [[x_left_block1, x_left_block2,  x_right_block1, 'x'],
                     [x_left_block1, x_right_block2, x_right_block1, 'x'],
                     [y_left_block1, y_left_block2,  y_right_block1, 'y'],
                     [y_left_block1, y_right_block2, y_right_block1, 'y']]
        ordering2 = [[x_left_block2, x_left_block1,  x_right_block2, 'x'],
                     [x_left_block2, x_right_block1, x_right_block2, 'x'],
                     [y_left_block2, y_left_block1,  y_right_block2, 'y'],
                     [y_left_block2, y_right_block1, y_right_block2, 'y']]                     
        
        for left_coord, middle_coord, right_coord, normal_direction in ordering1:
            if left_coord < middle_coord < right_coord:
                blocks1_with_mat_ids = cut_plane_blocks(blocks1_with_mat_ids, normal_direction, middle_coord)

        for left_coord, middle_coord, right_coord, normal_direction in ordering2:
            if left_coord < middle_coord < right_coord:
                blocks2_with_mat_ids = cut_plane_blocks(blocks2_with_mat_ids, normal_direction, middle_coord)

    # discard the same regions in 'blocks1'   # Tue Mar 20 2018
    only_in_blocks1 = is_in_setdiff2d( blocks1_with_mat_ids[:,:-1], blocks2_with_mat_ids[:,:-1] )
    if only_in_blocks1.any():
        all_blocks_with_mat_ids = np.concatenate( (blocks1_with_mat_ids[only_in_blocks1,:], blocks2_with_mat_ids) )
    else:
        all_blocks_with_mat_ids = blocks2_with_mat_ids.copy()
    # sort the blocks
    k = all_blocks_with_mat_ids
    all_blocks_with_mat_ids = k[np.lexsort((k[:,3],k[:,2],k[:,1],k[:,0]))]

    ## depends on dimension
    node1_coords = all_blocks_with_mat_ids[:,[0,2]]   # [x_left,y_left]
    node2_coords = all_blocks_with_mat_ids[:,[1,2]]   # [x_right,y_left]
    node3_coords = all_blocks_with_mat_ids[:,[1,3]]   # [x_right,y_right]
    node4_coords = all_blocks_with_mat_ids[:,[0,3]]   # [x_left,y_right]
    
    merged_coords = np.unique( np.concatenate((node1_coords, node2_coords, node3_coords, node4_coords)), axis=0 )  # sorted automatically
    merged_ngroups = [ngroups1[0]] * len(merged_coords)  # assuming there is only one element group
    # evaluate merged conns
    merged_conns = np.array([], dtype=np.int32).reshape(-1,4)   # [node1,node2,node3,node4]
    for block in all_blocks_with_mat_ids:
        node1 = [block[0], block[2]]
        node2 = [block[1], block[2]]
        node3 = [block[1], block[3]]
        node4 = [block[0], block[3]]
        node1_idx = np.argmax( (merged_coords == node1).all(axis=1) )
        node2_idx = np.argmax( (merged_coords == node2).all(axis=1) )
        node3_idx = np.argmax( (merged_coords == node3).all(axis=1) )
        node4_idx = np.argmax( (merged_coords == node4).all(axis=1) )
        merged_conns = np.append( merged_conns, [[node1_idx, node2_idx, node3_idx, node4_idx]], axis=0 )
    merged_conns = [merged_conns]  # first group
    merged_mat_ids = [all_blocks_with_mat_ids[:,-1].astype(np.int32)]
    merged_name = '(merge:' + mesh1.name + '_and_' + mesh2.name +')'

    return Mesh.from_data(merged_name, merged_coords, merged_ngroups, merged_conns, merged_mat_ids, descs)
    

def merge_line_mesh(mesh1, mesh2):
    """
    Merge two line meshes and create one line mesh,
    assuming there is only ONE element group.
    
    Warning: If two meshes have different 'mat_id's in the same region,
        the 'mat_id' of 'mesh2' is imposed.
    
    Args:
        mesh1: (sfepy's) Mesh object. A line type (desc='1_2') having only one element group.
        mesh2: (sfepy's) Mesh object. A line type (desc='1_2') having only one element group.
        
    Returns:
        merged_mesh: (sfepy's) Mesh object. Merged line mesh (desc='1_2').
    
    Examples:
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.], [3], [0.5], mat_id=0, name='line_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.], [3], [0.2], mat_id=1, name='line_mesh2', verbose=False)
    >>> merged_mesh = merge_line_mesh(mesh1, mesh2)
    >>> merged_mesh._get_io_data()
    (array([[-0.8],
           [ 0. ],
           [ 0.2],
           [ 0.5],
           [ 1. ],
           [ 1.2]]), array([0, 0, 0, 0, 0, 0]), [array([[0, 1],
           [1, 2],
           [2, 3],
           [3, 4],
           [4, 5]])], [array([1, 1, 1, 1, 1])], ['1_2'])
    """
    
    coords1, ngroups1, conns1, mat_ids1, descs1 = mesh1._get_io_data()
    coords2, ngroups2, conns2, mat_ids2, descs2 = mesh2._get_io_data()    
    # assume there is only ONE group
    if not(len(descs1)==1 and len(descs2)==1):
        raise MeshMergeError("Cannot merge more than two groups!")
    # assume the element type is a line: '1_2'
    if not(descs1[0]=='1_2' and descs2[0]=='1_2'):
        raise MeshMergeError("Cannot merge non-line meshes!")
    descs = ['1_2']
    
    blocks1 = conns_to_blocks(conns1[0], coords1)
    blocks2 = conns_to_blocks(conns2[0], coords2)
    
    # check overlapping blocks
    id_pairs = where_overlapping_blocks(blocks1, blocks2, touch_is_overlapping=True)
    
    blocks1_with_mat_ids = np.hstack( (blocks1, mat_ids1[0].reshape(-1,1)) )
    blocks2_with_mat_ids = np.hstack( (blocks2, mat_ids2[0].reshape(-1,1)) )

    # cut the plane along which overlapping occurs
    for id1, id2 in id_pairs:
        x_left_block1, x_right_block1 = blocks1[id1,[0,1]]
        x_left_block2, x_right_block2 = blocks2[id2,[0,1]]
        
        if x_left_block1 < x_left_block2 < x_right_block1:
            blocks1_with_mat_ids = cut_plane_blocks(blocks1_with_mat_ids, 'x', x_left_block2)
        if x_left_block1 < x_right_block2 < x_right_block1:
            blocks1_with_mat_ids = cut_plane_blocks(blocks1_with_mat_ids, 'x', x_right_block2)

        if x_left_block2 < x_left_block1 < x_right_block2:
            blocks2_with_mat_ids = cut_plane_blocks(blocks2_with_mat_ids, 'x', x_left_block1)
        if x_left_block2 < x_right_block1 < x_right_block2:
            blocks2_with_mat_ids = cut_plane_blocks(blocks2_with_mat_ids, 'x', x_right_block1)
    
    # discard the same regions in 'blocks1'   # Tue Mar 20 2018
    only_in_blocks1 = is_in_setdiff2d( blocks1_with_mat_ids[:,:-1], blocks2_with_mat_ids[:,:-1] )
    if only_in_blocks1.any():
        all_blocks_with_mat_ids = np.concatenate( (blocks1_with_mat_ids[only_in_blocks1], blocks2_with_mat_ids) )
    else:
        all_blocks_with_mat_ids = blocks2_with_mat_ids.copy()
    # sort the blocks
    k = all_blocks_with_mat_ids
    all_blocks_with_mat_ids = k[np.lexsort((k[:,1],k[:,0]))]
    
    # blocks.sort(axis=0)
    node1_coords = all_blocks_with_mat_ids[:,[0]]   # x_left
    node2_coords = all_blocks_with_mat_ids[:,[1]]   # x_right
    
    merged_coords = np.unique( np.concatenate((node1_coords, node2_coords)), axis=0 )  # sorted automatically
    merged_ngroups = [ngroups1[0]] * len(merged_coords)  # assuming there is only one element group
    # evaluate merged conns
    merged_conns = np.array([], dtype=np.int32).reshape(-1,2)   # [x_left,x_right]
    for block in all_blocks_with_mat_ids:
        x_left  = block[0]
        x_right = block[1]
        x_left_idx = np.argmax( (merged_coords == [x_left]).all(axis=1) )
        x_right_idx = np.argmax( (merged_coords == [x_right]).all(axis=1) )
        merged_conns = np.append( merged_conns, [[x_left_idx,x_right_idx]], axis=0 )
    merged_conns = [merged_conns]  # first group
    merged_mat_ids = [all_blocks_with_mat_ids[:,-1].astype(np.int32)]
    merged_name = '(merge:' + mesh1.name + '_and_' + mesh2.name +')'

    return Mesh.from_data(merged_name, merged_coords, merged_ngroups, merged_conns, merged_mat_ids, descs)


def is_in_setdiff2d(ar1, ar2):
    """
    Return the boolean values answering whether each item 'ar1' is NOT contained in 'ar2'.
    
    Args:
        ar1: numpy 2D array.
        ar2: numpy 2D array.
        
    Returns:
        is_in: numpy 1D array.
            Boolean values answering whether the item in 'ar1' of the row index is NOT contained in 'ar2'.
        
    Examples:
    >>> import numpy as np
    >>> a = np.array([[1,0],[2,0],[3,0],[4,0]])
    >>> b = np.array([[1,0],[2,1],[3,0],[4,1]])
    >>> is_in_setdiff2d(a,b)
    array([False,  True, False,  True])
    >>> a[is_in_setdiff2d(a,b)]
    array([[2, 0],
           [4, 0]])
    >>> a = np.array([[0.5,1.],[0.,0.2],[0.2,0.5]])
    >>> b = np.array([[-0.8,0.],[0.,0.2],[0.2,0.5],[0.5,1.],[1.,1.2]])
    >>> is_in_setdiff2d(a,b)
    array([False, False, False])
    """
    is_in = []
    for idx, item in enumerate(ar1):
        if ((ar2 == item).all(axis=1)).any():  # the item is in ar2
        #if np.isclose(item, ar2).all(axis=1).any():  # the item is in ar2
            is_in.append(False)
        else:
            is_in.append(True)
    return np.array(is_in)


def conns_to_blocks(conns_in_a_group, coords):
    """
    Transform the 'conns' of (sfepy's) Mesh object (in a group) to 'blocks';
    a 'block' consists of 2,4, or 6 points: [x_left,x_right,y_left,y_right,z_left,z_right].

    Args:
        conns_in_a_group: 'conns' of (sfepy's) Mesh object in a group.
        coords: 'coords' of (sfepy's) Mesh object.
            
    Returns:
        blocks: a numpy array of blocks.
    
    >>> import numpy as np
    >>> conns_in_group = np.array([[0,2,3,1]])
    >>> coords = np.array([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
    >>> conns_to_blocks(conns_in_group,coords)
    array([[0., 1., 0., 1.]])
    """
    dim = coords.shape[1]
    if dim == 3:
        left_coords = coords[conns_in_a_group[:,0]]
        right_coords = coords[conns_in_a_group[:,6]]
        blocks = np.stack([left_coords[:,0],right_coords[:,0], left_coords[:,1],right_coords[:,1], left_coords[:,2],right_coords[:,2]], axis=-1)
    elif dim == 2:
        left_coords = coords[conns_in_a_group[:,0]]
        right_coords = coords[conns_in_a_group[:,2]]
        blocks = np.stack([left_coords[:,0],right_coords[:,0], left_coords[:,1],right_coords[:,1]], axis=-1)
    elif dim == 1:
        left_coords = coords[conns_in_a_group[:,0]]
        right_coords = coords[conns_in_a_group[:,1]]
        blocks = np.stack([left_coords[:,0],right_coords[:,0]], axis=-1)
    else:
        raise ValueError("Cannot identify the dimension of 'coords': 1,2, or 3 dimensions are possible.")
    
    return blocks


def where_overlapping_blocks(blocks1, blocks2, touch_is_overlapping=False):
    """
    Check whether the given blocks are overlapped or not;
    a 'block' consists of 2,4, or 6 points: [x_left,x_right,y_left,y_right,z_left,z_right].

    Args:
        blocks1: numpy array of 'blocks'. A 'block' consists of 2,4, or 6 points: [x_left,x_right,y_left,y_right,z_left,z_right].
        blocks2: numpy array of 'blocks'. A 'block' consists of 2,4, or 6 points: [x_left,x_right,y_left,y_right,z_left,z_right].
        touch_is_overlapping: bool, optional (default=False). If this is True,
            a mesh touching another mesh is judged as overlapping.
            
    Returns:
        result: a list of tuples: an element (id1,id2) means the index 'id1' of 'blocks1' and the index 'id2' of 'blocks2' are overlapping.
    
    >>> import numpy as np
    >>> blocks1 = np.array([[0.,1.,0.,1.,0.,1.]])
    >>> blocks2 = np.array([[-1.,1.,-1.,1.,-1.,1.]])
    >>> where_overlapping_blocks(blocks1, blocks2)
    [(0, 0)]
    >>> blocks3 = np.array([[-1.,-0.5,-1.,-0.5,-1.,-0.5], [-1.,-0.5,-1.,-0.5,-0.5,0.],\
                            [-1.,-0.5,-0.5,0.,-1.,-0.5], [-1.,-0.5,-0.5,0.,-0.5,0.],\
                            [-0.5,0.,-1.,-0.5,-1.,-0.5],  [-0.5,0.,-1.,-0.5,-0.5,0.],\
                            [-0.5,0.,-0.5,0.,-1.,-0.5],   [-0.5,0.,-0.5,0.,-0.5,0.]])
    >>> where_overlapping_blocks(blocks1, blocks3)
    []
    >>> where_overlapping_blocks(blocks1, blocks3, touch_is_overlapping=True)
    [(0, 7)]
    >>> where_overlapping_blocks(blocks3, blocks1, touch_is_overlapping=True)
    [(7, 0)]
    """
    dim = max(blocks1.shape[1], blocks2.shape[1])/2
    if dim == 3:
        left_coords_of_blocks1  = blocks1[:,[0,2,4]]
        right_coords_of_blocks1 = blocks1[:,[1,3,5]]
        left_coords_of_blocks2  = blocks2[:,[0,2,4]]
        right_coords_of_blocks2 = blocks2[:,[1,3,5]]
    elif dim == 2:
        left_coords_of_blocks1  = blocks1[:,[0,2]]
        right_coords_of_blocks1 = blocks1[:,[1,3]]
        left_coords_of_blocks2  = blocks2[:,[0,2]]
        right_coords_of_blocks2 = blocks2[:,[1,3]]
    elif dim == 1:
        left_coords_of_blocks1  = blocks1[:,[0]]
        right_coords_of_blocks1 = blocks1[:,[1]]
        left_coords_of_blocks2  = blocks2[:,[0]]
        right_coords_of_blocks2 = blocks2[:,[1]]
    else:
        raise ValueError("Cannot identify the dimension of blocks: try elements of length 2,4, or 6.")

    result = []
    
    # the idea is to check non-overlapping, instead of overlapping
    if touch_is_overlapping:
        for idx, block1 in enumerate(blocks1):
            left_coord_of_block1  = left_coords_of_blocks1[idx]
            right_coord_of_block1 = right_coords_of_blocks1[idx]

            test1 = np.less(right_coord_of_block1, left_coords_of_blocks2)            
            test2 = np.less(right_coords_of_blocks2, left_coord_of_block1)
            not_overlap  = np.logical_or(test1, test2).any(axis=1)
            overlap_indices = np.where(not_overlap == False)[0]
            for overlap_index in overlap_indices:
                result.append( (idx,overlap_index) )
    else:
        for idx, block1 in enumerate(blocks1):
            left_coord_of_block1  = left_coords_of_blocks1[idx]
            right_coord_of_block1 = right_coords_of_blocks1[idx]

            test1 = np.less_equal(right_coord_of_block1, left_coords_of_blocks2)            
            test2 = np.less_equal(right_coords_of_blocks2, left_coord_of_block1)
            not_overlap  = np.logical_or(test1, test2).any(axis=1)
            overlap_indices = np.where(not_overlap == False)[0]
            for overlap_index in overlap_indices:
                result.append( (idx,overlap_index) )
    return result


def cut_plane_blocks(blocks, normal_direction, coord):
    """
    Cut the given blocks through a plane with the given normal direction and coordinate.
    
    Args:
        blocks: numpy array of 'blocks'. A 'block' consists of 2,4, or 6 points: [x_left,x_right,y_left,y_right,z_left,z_right].
        normal_direction: 'x', 'y' or 'z'. The normal direction of the cut plane.
        coord: float. The coordinate on the normal direction where a cut plane passes through.
        
    Returns:
        new_blocks: a numpy array of blocks, cutted through the plane.
        
    >>> import numpy as np
    >>> blocks = np.array( [[0.,1.,0.,1.],[1.,2.,0.,1.]] )
    >>> cut_plane_blocks(blocks, 'y', 0.5)
    array([[0. , 1. , 0. , 0.5],
           [0. , 1. , 0.5, 1. ],
           [1. , 2. , 0. , 0.5],
           [1. , 2. , 0.5, 1. ]])
    """
    if normal_direction == 'x':
        normal_idx = 0
    elif normal_direction == 'y':
        normal_idx = 2
    elif normal_direction == 'z':
        normal_idx = 4
    else:
        raise ValueError("Unknown option for 'normal_direction': use 'x','y' or 'z'.")
    
    left_of_coord  = blocks[:,normal_idx] < coord
    right_of_coord = coord < blocks[:,normal_idx+1]
    is_block_to_cut = np.logical_and(left_of_coord,right_of_coord)
    blocks_to_cut = blocks[ is_block_to_cut ]
    
    new_blocks = blocks[ np.logical_not(is_block_to_cut) ]   # non-cutted blocks remains intact.
    
    for block in blocks_to_cut:
        left_block = block.copy()
        right_block = block.copy()
        left_block[normal_idx+1] = coord
        right_block[normal_idx] = coord
        
        new_blocks = np.append(new_blocks, [left_block,right_block], axis=0)
    
    return new_blocks
    

def mesh_info_to_str(mesh):
    """
    Returns a string containing the infomation of a mesh.
    """
    
    result = ""
    coords, ngroups, conns, mat_ids, descs = mesh._get_io_data()
    result += "Information of Mesh:%s:\n" % mesh.name
    result += '\tcoords = %s\n' % str(coords)
    result += '\tngroups = %s\n' % str(ngroups)
    result += '\tconns = %s\n' % str(conns)
    result += '\tmat_ids = %s\n' % str(mat_ids)
    result += '\tdescs = %s\n' % str(descs)
    return result


def print_mesh(mesh):
    """
    Print the info of a mesh.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh = gen_block_mesh([1.], [3], [0.5], name='test_mesh', verbose=False)
    >>> mesh._get_io_data()
    (array([[0. ],
           [0.5],
           [1. ]]), array([0, 0, 0]), [array([[0, 1],
           [1, 2]])], [array([0, 0])], ['1_2'])
    """
    print(mesh_info_to_str(mesh))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
    from sfepy.mesh.mesh_generators import gen_block_mesh
    mesh1 = gen_block_mesh([1.,1.], [2,2], [0.5,0.5], mat_id=0, name='rect_mesh1', verbose=False)
    mesh2 = gen_block_mesh([2.,2.], [2,2], [0.2,0.2], mat_id=1, name='rect_mesh2', verbose=False)
    merged_mesh = merge_rect_mesh(mesh1, mesh2)
    merged_mesh._get_io_data()