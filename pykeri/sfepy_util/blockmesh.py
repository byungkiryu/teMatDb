# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 09:32:01 2018

@author: 정재환
"""

import numpy as np
from fractions import Fraction

from sfepy.discrete.fem.mesh import Mesh
from sfepy.mesh.mesh_generators import gen_block_mesh
from pykeri.sfepy_util.merge import merge_block_mesh
from pykeri.sfepy_util.stack import stack_block_mesh


class BlockMesh(Mesh):
    """
    The BlockMesh class extends the SfePy's Mesh class;
    the main purpose is to provide 'simple_mesh' attribute which contains
    the simplest block mesh topologically identical to the given mesh.
    """
    def __init__(self, name='blockmesh', cmesh=None):
        """
        Create a BlockMesh.
        By default, the mesh is empty.
        
        Args:
            name : String. Blockmesh name.
            cmesh : CMesh, optional. If given, use this as the cmesh.
        """
        super().__init__(name, cmesh)
        self._simple_mesh = None
    
    def cell_selection(self, mat_ids=[0]):
        """
        Create a topological entity selection string to select cells with the given 'mat_ids'.
        Refer to SfePy's document: "http://sfepy.org/doc-devel/users_guide.html#regions"
        to see how to use the created string.
        
        Args:
            mat_ids: array of ints
                All the cells having one of these 'mat_ids' are selected.
        
        Warning:
            assumes there is only ONE node group in the mesh.
        
        Returns:
            selection: string
                A selection string which can be used for creating a region in SfePy;
                check "sfepy.discrete.fem.FEDomain.create_region()" function.
                
        Examples:
        >>> mesh1 = BlockMesh.block_by_border([0.], [2.], [2], mat_id=0, name='mesh1')
        >>> mesh2 = BlockMesh.block_by_border([1.], [3.], [2], mat_id=1, name='mesh2')
        >>> mesh1.add(mesh2)
        >>> mesh1.cell_selection(mat_ids=[0])
        '(cells of group 0)'
        >>> mesh1.cell_selection(mat_ids=[1])
        '(cells of group 1)'
        >>> mesh1.cell_selection(mat_ids=[0,1])
        '(cells of group 0 +c cells of group 1)'
        """
        selection = '(cells of group ' + str(mat_ids[0])
        for mat_id in mat_ids[1:]:
            selection += ' +c cells of group ' + str(mat_id)
        selection += ')'

        return selection                
    
    @staticmethod
    def block_by_border(leftbottom, righttop, shape, mat_id=0, name='block', coors=None, verbose=False):
        """
        Generate a block having border enclosed by 'leftbottom' point and 'righttop' point.
    
        Args:
            leftbottom: array of 1, 2 or 3 floats
                The left bottom point of the block.
            righttop: array of 1, 2 or 3 floats
                The right top point of the block.
            shape : array of 2 or 3 ints
                Shape (counts of nodes in x, y, z) of the block mesh.
            mat_id : int, optional.
                The material id of all elements.
            name : string.
                Mesh name.
            verbose : bool.
                If True, show progress of the mesh generation.
    
        Returns:
            blockmesh : BlockMesh instance
            
        Examples:
        >>> mesh = BlockMesh.block_by_border([0.], [1.5], [3], mat_id=1, name='test_mesh')
        >>> mesh._get_io_data()
        (array([[0.  ],
               [0.75],
               [1.5 ]]), array([0, 0, 0]), [array([[0, 1],
               [1, 2]])], [array([1, 1])], ['1_2'])
        >>> mesh.simple_mesh._get_io_data()
        (array([[0. ],
               [1.5]]), array([0, 0]), [array([[0, 1]])], [array([1])], ['1_2'])
        """
        dims = []
        center = []
        for lp, rp in zip(leftbottom, righttop):
            left = Fraction(lp)  # to avoid floating point error
            right = Fraction(rp)
            dim = right-left
            middle = left + dim/2
            dims.append( float(dim) )
            center.append( float(middle) )
        
        return BlockMesh.block_by_center(dims, shape, center, mat_id=mat_id, name=name, coors=coors, verbose=verbose)
        
        
    @staticmethod
    def block_by_center(dims, shape, center, mat_id=0, name='block', coors=None, verbose=False):
        """
        Generate a block centered at 'center'. The dimension is determined by the lenght of the shape argument.
        A wrapper for SfePy's "gen_block_mesh" function.
    
        Args:
            dims : array of 2 or 3 floats.
                Dimensions of the block.
            shape : array of 2 or 3 ints.
                Shape (counts of nodes in x, y, z) of the block mesh.
            center : array of 2 or 3 floats.
                Centre of the block.
            mat_id : int, optional.
                The material id of all elements.
            name : string.
                Mesh name.
            verbose : bool.
                If True, show progress of the mesh generation.
    
        Returns:
            blockmesh : BlockMesh instance
            
        Examples:
        >>> mesh = BlockMesh.block_by_center([1.], [3], [0.5], name='test_mesh')
        >>> mesh._get_io_data()
        (array([[0. ],
               [0.5],
               [1. ]]), array([0, 0, 0]), [array([[0, 1],
               [1, 2]])], [array([0, 0])], ['1_2'])
        >>> mesh.simple_mesh._get_io_data()
        (array([[0.],
               [1.]]), array([0, 0]), [array([[0, 1]])], [array([0])], ['1_2'])
        """
        new_mesh = gen_block_mesh(dims, shape, center, mat_id, name, coors, verbose)
        simple_shape = np.asarray(shape, dtype=np.int32)
        simple_shape.fill(2)  # simplest block has 2 nodes in each direction.
        simple_mesh = gen_block_mesh(dims, simple_shape, center, mat_id, name, coors, verbose)
        blockmesh = BlockMesh.from_Mesh(new_mesh)
        blockmesh._simple_mesh = BlockMesh.from_Mesh(simple_mesh)
        
        return blockmesh

    def add(self, blockmesh):
        """
        Add a BlockMesh to self.
        
        Warning: If two meshes have different 'mat_id's in the same region,
            the 'mat_id' of 'blockmesh' (not self) is imposed.
        
        Args:
            blockmesh: a BlockMesh object to be added to self.
            
        Examples:
        >>> mesh1 = BlockMesh.block_by_center([1.,1.,1.], [2,2,2], [0.5,0.5,0.5], mat_id=0, name='mesh1')
        >>> mesh2 = BlockMesh.block_by_center([2.,2.,2.], [2,2,2], [0.2,0.2,0.2], mat_id=1, name='mesh2')
        >>> mesh1.add(mesh2)
        >>> mesh1._get_io_data()
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
        >>> mesh1.simple_mesh._get_io_data()
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
        new_mesh = merge_block_mesh(self, blockmesh)
        super().__init__(name=self.name, cmesh=new_mesh.cmesh)   # change self
        new_simple_mesh = merge_block_mesh(self.simple_mesh, blockmesh.simple_mesh)
        self._simple_mesh = BlockMesh.from_Mesh(new_simple_mesh)
    
    def stack(self, blockmesh_to_stack, direction):
        """
        Stack the 'blockmesh_to_stack' on 'self' with along 'direction',
        assuming there is only ONE element group.
        
        Args:
            blockmesh_to_stack: (sfepy's) Mesh to stack.
            direction: String.
                Use 'left_of'/'x_left_of' or 'right_of'/'x_right_of' for 1D;
                    'x_left_of', 'x_right_of', 'y_left_of' or 'y_right_of' for 2D;
                    'x_left_of', 'x_right_of', 'y_left_of', 'y_right_of', 'z_left_of'/'below' or 'z_right_of'/'above' for 3D.
        
        Returns:
            the BlockMesh constructed by stacking the 'blockmesh_to_stack' on the 'direction' of 'self'.
        
        Examples:
        >>> mesh1 = BlockMesh.block_by_center([1.,1.,1.], [2,2,2], [0.5,0.5,0.5], name='mesh1')
        >>> mesh2 = BlockMesh.block_by_center([2.,2.,2.], [2,2,2], [0.0,0.0,0.0], name='mesh2')
        >>> mesh2.stack(mesh1, 'above')
        >>> mesh2._get_io_data()
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
        >>> mesh2.simple_mesh._get_io_data()
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
        new_mesh = stack_block_mesh(blockmesh_to_stack, direction, self)
        super().__init__(name=self.name, cmesh=new_mesh.cmesh)   # change self
        new_simple_mesh = stack_block_mesh(blockmesh_to_stack.simple_mesh, direction, self.simple_mesh)
        self._simple_mesh = BlockMesh.from_Mesh(new_simple_mesh)
        
    @staticmethod
    def from_Mesh(mesh):
        """
        Create a BlockMesh from the SfePy's Mesh object.
        
        Args:
            mesh: SfePy's Mesh object.
        Returns:
            blockmesh: a BlockMesh object.
        """
        cmesh = mesh.cmesh.create_new()
        return BlockMesh(name=mesh.name, cmesh=cmesh)
    
    def to_Mesh(self, name=None):
        """
        Convert the blockmesh object to a SfePy's Mesh object.
        
        Returns:
            mesh: SfePy's Mesh object.
        """
        if name is None:
            name = self.name
            
        cmesh = self.cmesh.create_new()
        return Mesh(name=name, cmesh=cmesh)
        
    @property
    def simple_mesh(self):
        """
        Return the simplest block mesh topologically identical to the block mesh.
        """
        if self._simple_mesh is None:
            from pykeri.sfepy_util.simplify import simplify_parallelepiped_mesh
            self._simple_mesh = BlockMesh.from_Mesh( simplify_parallelepiped_mesh(self) )
        return self._simple_mesh
    
    def write(self, filename=None, simple_mesh_filename=None, **kwargs):
        """
        Write 'mesh' and 'simple_mesh' to a file.
        Optional arguments in SfePy's 'Mesh.write()' function is usable.
        
        Args:
            filename: str, optional
                The filename. If None, the mesh name is used instead.
            simple_mesh_filename: str, optional
                The filename for 'simple_mesh'. If None, 'filename'+'_simple_mesh.mesh' is used instead.
            **kwargs: dict, optional
                Additional arguments that can be passed to the 'Mesh.wrtie()' function.
        """
        if filename is None:
            filename = self.name + '.mesh'
        if simple_mesh_filename is None:
            import os
            simple_mesh_filename = os.path.splitext(filename)[0] + '_simple_mesh.mesh'
        super(BlockMesh, self).write(filename)
        super(BlockMesh, self.simple_mesh).write(simple_mesh_filename)
    
    @staticmethod
    def from_file(filename=None, simple_mesh_filename=None, **kwargs):
        """
        Read 'mesh' and 'simple_mesh' to a file.
        Optional arguments in SfePy's 'Mesh.from_file()' function is usable.
        
        Args:
            filename: str. The filename.
            simple_mesh_filename: str, optional
                The filename for 'simple_mesh'. If None, 'simple_mesh' is not loaded.
            **kwargs: dict, optional
                Additional arguments that can be passed to the 'Mesh.from_file()' function.
                
        Returns:
            mesh: BlockMesh instance.
        """
        mesh = BlockMesh.from_Mesh( Mesh.from_file(filename=filename, **kwargs) )
        if simple_mesh_filename is not None:
            simple_mesh = BlockMesh.from_Mesh( Mesh.from_file(filename=simple_mesh_filename, **kwargs) )
            mesh._simple_mesh = simple_mesh
            
        return mesh        
    
    
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()