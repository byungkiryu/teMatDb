# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 17:13:09 2018

Provides functions to merge rectangular elements(=cells);
possible types are '1_2', '2_4', '3_8'.


updated on Thu Mar 15 2018: bug fix: merge does not create unnecessary coordinate points; see 'discard_unnecessary_coords()' function.

@author: Jaywan Chung
"""

import numpy as np
#from sfepy.mesh.mesh_generators import gen_block_mesh
from sfepy.discrete.fem.mesh import Mesh

from pykeri.sfepy_util.block_mesh import discard_unnecessary_coords


class MeshMergeError(Exception):
    pass


def merge_block_mesh(mesh1, mesh2):
    """
    Merge two block meshes and create one block mesh,
    assuming there is only ONE element group.
    A block mesh can be a line, a rectangular or a parallelepiped.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.], [3], [0.5], name='line_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.], [3], [0.2], name='line_mesh2', verbose=False)
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
           [4, 5]])], [array([0, 0, 0, 0, 0])], ['1_2'])
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
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.,1.], [2,2,2], [0.5,0.5,0.5], name='para_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.,2.], [2,2,2], [0.2,0.2,0.2], name='para_mesh2', verbose=False)
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
           [16, 32, 36, ..., 33, 37, 21],
           [32, 48, 52, ..., 49, 53, 37],
           ...,
           [10, 26, 30, ..., 27, 31, 15],
           [26, 42, 46, ..., 43, 47, 31],
           [42, 58, 62, ..., 59, 63, 47]])], [array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0])], ['3_8'])
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
    
    conns1_in_first_group = conns1[0]  # array of [x,y,z] coordinates
    conns2_in_first_group = conns2[0]
    xs = []
    ys = []
    zs = []
    parals_and_mat_ids = []
    for conn_idx, conn in enumerate(conns1_in_first_group):
        x_min = coords1[conn[0]][0]; x_max = coords1[conn[6]][0]
        y_min = coords1[conn[0]][1]; y_max = coords1[conn[6]][1]
        z_min = coords1[conn[0]][2]; z_max = coords1[conn[6]][2]
        xs.append(x_min); xs.append(x_max)
        ys.append(y_min); ys.append(y_max)
        zs.append(z_min); zs.append(z_max)
        mat_id = mat_ids1[0][conn_idx]
        parals_and_mat_ids.append(( (x_min,x_max,y_min,y_max,z_min,z_max), mat_id) )
    for conn_idx, conn in enumerate(conns2_in_first_group):
        x_min = coords2[conn[0]][0]; x_max = coords2[conn[6]][0]
        y_min = coords2[conn[0]][1]; y_max = coords2[conn[6]][1]
        z_min = coords2[conn[0]][2]; z_max = coords2[conn[6]][2]
        xs.append(x_min); xs.append(x_max)
        ys.append(y_min); ys.append(y_max)
        zs.append(z_min); zs.append(z_max)
        mat_id = mat_ids2[0][conn_idx]
        parals_and_mat_ids.append(( (x_min,x_max,y_min,y_max,z_min,z_max), mat_id) )
    xs = sorted(list(set(xs)))
    ys = sorted(list(set(ys)))
    zs = sorted(list(set(zs)))
    xyzs = [(xp, yp, zp) for xp in xs for yp in ys for zp in zs]
    merged_coords = np.array( xyzs, dtype=np.float64 )
    merged_conns_in_first_group = []
    merged_mat_ids_in_first_group = []
    for z_min, z_max in zip(zs[:-1],zs[1:]):
        for y_min, y_max in zip(ys[:-1],ys[1:]):
            for x_min, x_max in zip(xs[:-1],xs[1:]):
                for big_paral, mat_id in parals_and_mat_ids:
                    small_paral = (x_min,x_max,y_min,y_max,z_min,z_max)
                    if contained_in_parallelepiped(small_paral, big_paral):
                        bottom_plane_leftbottom_idx  = xyzs.index((x_min,y_min,z_min))
                        bottom_plane_rightbottom_idx = xyzs.index((x_max,y_min,z_min))
                        bottom_plane_righttop_idx    = xyzs.index((x_max,y_max,z_min))
                        bottom_plane_lefttop_idx     = xyzs.index((x_min,y_max,z_min))
                        merged_conns_in_first_group.append( [bottom_plane_leftbottom_idx,
                                                             bottom_plane_rightbottom_idx,
                                                             bottom_plane_righttop_idx,
                                                             bottom_plane_lefttop_idx,
                                                             bottom_plane_leftbottom_idx+1,
                                                             bottom_plane_rightbottom_idx+1,
                                                             bottom_plane_righttop_idx+1,
                                                             bottom_plane_lefttop_idx+1] )
                        merged_mat_ids_in_first_group.append(mat_id)
                        break
    merged_conns = [np.array(merged_conns_in_first_group, dtype=np.int)]
    merged_mat_ids = [np.array(merged_mat_ids_in_first_group, dtype=np.int)]
    merged_ngroups = [ngroups1[0]] * len(merged_coords)
    merged_name = '(merge:' + mesh1.name + '_and_' + mesh2.name +')'
    
    merged_mesh = Mesh.from_data(merged_name, merged_coords, merged_ngroups, merged_conns, merged_mat_ids, descs)
    merged_mesh = discard_unnecessary_coords(merged_mesh)  # Thu Mar 15 2018
    return merged_mesh
    

def contained_in_parallelepiped(small_paral, big_paral):
    """
    Determine whether the small parallelepiped is contained in the big parallelepiped or not;
    a parallelepiped is a list of six floating numbers: [x_min, x_max, y_min, y_max, z_min, z_max].

    >>> contained_in_parallelepiped([0.,1., 0.,1., 0.,1.], [0.,1., 0.,2., 0.,1.])
    True
    >>> contained_in_parallelepiped([0.,2., 0.,1., 0.,2.], [0.,1., 0.,1., 0.,1.])
    False
    """
    small_xy_rect = small_paral[0:4]
    small_yz_rect = small_paral[2:6]
    small_zx_rect = small_paral[4:6] + small_paral[0:2]
    big_xy_rect   = big_paral[0:4]
    big_yz_rect   = big_paral[2:6]
    big_zx_rect   = big_paral[4:6] + big_paral[0:2]
        
    if not contained_in_rect(small_xy_rect, big_xy_rect):
        return False
    if not contained_in_rect(small_yz_rect, big_yz_rect):
        return False
    if not contained_in_rect(small_zx_rect, big_zx_rect):
        return False
    return True


def merge_rect_mesh(mesh1, mesh2):
    """
    Merge two rectangular meshes and create one rectangular mesh,
    assuming there is only ONE element group.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.,1.], [2,2], [0.5,0.5], name='rect_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.,2.], [2,2], [0.2,0.2], name='rect_mesh2', verbose=False)
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
           [ 4,  8,  9,  5],
           [ 8, 12, 13,  9],
           [ 1,  5,  6,  2],
           [ 5,  9, 10,  6],
           [ 9, 13, 14, 10],
           [ 2,  6,  7,  3],
           [ 6, 10, 11,  7],
           [10, 14, 15, 11]])], [array([0, 0, 0, 0, 0, 0, 0, 0, 0])], ['2_4'])
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
    
    conns1_in_first_group = conns1[0]  # array of [x,y] coordinates
    conns2_in_first_group = conns2[0]
    xs = []
    ys = []
    rects_and_mat_ids = []
    for conn_idx, conn in enumerate(conns1_in_first_group):
        left   = coords1[conn[0]][0]
        right  = coords1[conn[2]][0]
        bottom = coords1[conn[0]][1]
        top    = coords1[conn[2]][1]
        xs.append(left)
        xs.append(right)
        ys.append(top)
        ys.append(bottom)
        mat_id = mat_ids1[0][conn_idx]
        rects_and_mat_ids.append(( (left, right, bottom, top), mat_id) )
    for conn_idx, conn in enumerate(conns2_in_first_group):
        left   = coords2[conn[0]][0]
        right  = coords2[conn[2]][0]
        bottom = coords2[conn[0]][1]
        top    = coords2[conn[2]][1]
        xs.append(left)
        xs.append(right)
        ys.append(top)
        ys.append(bottom)
        mat_id = mat_ids2[0][conn_idx]
        rects_and_mat_ids.append(( (left, right, bottom, top), mat_id) )
    xs = sorted(list(set(xs)))
    ys = sorted(list(set(ys)))
    xys = [(xp, yp) for xp in xs for yp in ys]
    merged_coords = np.array( xys, dtype=np.float64 )
    merged_conns_in_first_group = []
    merged_mat_ids_in_first_group = []
    for bottom, top in zip(ys[:-1],ys[1:]):
        for left, right in zip(xs[:-1],xs[1:]):
            for big_rect, mat_id in rects_and_mat_ids:
                small_rect = (left, right, bottom, top)
                if contained_in_rect(small_rect, big_rect):
                    leftbottom_idx  = xys.index((left,bottom))
                    rightbottom_idx = xys.index((right,bottom))
                    merged_conns_in_first_group.append([leftbottom_idx, rightbottom_idx, rightbottom_idx+1, leftbottom_idx+1])
                    merged_mat_ids_in_first_group.append(mat_id)
                    break
    merged_conns = [np.array(merged_conns_in_first_group, dtype=np.int)]
    merged_mat_ids = [np.array(merged_mat_ids_in_first_group, dtype=np.int)]
    merged_ngroups = [ngroups1[0]] * len(merged_coords)
    merged_name = '(merge:' + mesh1.name + '_and_' + mesh2.name +')'
    
    merged_mesh = Mesh.from_data(merged_name, merged_coords, merged_ngroups, merged_conns, merged_mat_ids, descs)
    merged_mesh = discard_unnecessary_coords(merged_mesh)   # Thu Mar 15 2018
    return merged_mesh
    

def contained_in_rect(small_rect, big_rect):
    """
    Determine whether the small rectangular is contained in the big rectangular or not;
    a rectangular is a list of four floating numbers: [left, right, bottom, top].

    >>> contained_in_rect([0., 1., 0., 1.], [0., 1., 0., 2.])
    True
    >>> contained_in_rect([0., 2., 0., 1.], [0., 1., 0., 1.])
    False
    """
    small_x_line = small_rect[0:2]
    small_y_line = small_rect[2:4]
    big_x_line   = big_rect[0:2]
    big_y_line   = big_rect[2:4]
    
    if not contained_in_line(small_x_line, big_x_line):
        return False
    if not contained_in_line(small_y_line, big_y_line):
        return False
    return True


def merge_line_mesh(mesh1, mesh2):
    """
    Merge two line meshes and create one line mesh,
    assuming there is only ONE element group.
    
    >>> from sfepy.mesh.mesh_generators import gen_block_mesh
    >>> mesh1 = gen_block_mesh([1.], [3], [0.5], name='line_mesh1', verbose=False)
    >>> mesh2 = gen_block_mesh([2.], [3], [0.2], name='line_mesh2', verbose=False)
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
           [4, 5]])], [array([0, 0, 0, 0, 0])], ['1_2'])
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
    
    conns1_in_first_group = conns1[0]
    conns2_in_first_group = conns2[0]
    xs = []
    lines_and_mat_ids = []
    for conn_idx, conn in enumerate(conns1_in_first_group):
        start_x = coords1[conn[0]][0]
        end_x = coords1[conn[1]][0]
        xs.append(start_x)
        xs.append(end_x)
        mat_id = mat_ids1[0][conn_idx]
        lines_and_mat_ids.append(([start_x, end_x], mat_id))
    for conn_idx, conn in enumerate(conns2_in_first_group):
        start_x = coords2[conn[0]][0]
        end_x = coords2[conn[1]][0]
        xs.append(start_x)
        xs.append(end_x)
        mat_id = mat_ids2[0][conn_idx]
        lines_and_mat_ids.append(([start_x, end_x], mat_id))
    xs = sorted(list(set(xs)))
    merged_coords = np.array( list([xp] for xp in xs), dtype=np.float64 )
    merged_conns_in_first_group = []
    merged_mat_ids_in_first_group = []
    for idx, short_line in enumerate(zip(xs[:-1],xs[1:])):
        #short_line = [start_x, end_x]
        for long_line, mat_id in lines_and_mat_ids:
            if contained_in_line(short_line, long_line):
                merged_conns_in_first_group.append([idx, idx+1])
                merged_mat_ids_in_first_group.append(mat_id)
                break
    merged_conns = [np.array(merged_conns_in_first_group, dtype=np.int)]
    merged_mat_ids = [np.array(merged_mat_ids_in_first_group, dtype=np.int)]
    merged_ngroups = [ngroups1[0]] * len(merged_coords)
    merged_name = '(merge:' + mesh1.name + '_and_' + mesh2.name +')'
    
    merged_mesh = Mesh.from_data(merged_name, merged_coords, merged_ngroups, merged_conns, merged_mat_ids, descs)
    return merged_mesh


def contained_in_line(short_line, long_line):
    """
    Determine whether the short line is contained in the long line or not;
    a line is a list of two floating numbers: [starting point, end point].
    
    >>> contained_in_line([0., 1.], [0., 1.])
    True
    >>> contained_in_line([0., 1.], [0., 2.])
    True
    >>> contained_in_line([0., 1.], [1., 2.])
    False
    >>> contained_in_line([0., 2.], [0., 1.])
    False
    >>> contained_in_line([0., 2.], [0., 2.])
    True
    >>> contained_in_line([0., 2.], [1., 2.])
    False
    >>> contained_in_line([1., 2.], [0., 1.])
    False
    >>> contained_in_line([1., 2.], [0., 2.])
    True
    >>> contained_in_line([1., 2.], [1., 2.])
    True
    """
    if short_line[0] < long_line[0]:
        return False
    if short_line[1] > long_line[1]:
        return False
    return True


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