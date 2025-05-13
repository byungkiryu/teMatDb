# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 08:07:20 2017

@author: Jaywan Chung

updated on Thu Mar 15 2018: fix: "None" interface is ignored.
updated on Mon Mar 12 2018: bug fix "plot" function: switch the position of "Th" and "Tc".
updated on Fri Mar 08 2018: added "mats" property to "Leg" class; uses "mats" property of "Segment" class.
updated on Fri Mar 09 2018: added "plot_leg_TEP" function and "plot_mat_TEP" function to "Leg" class.
updated on Thu Mar 08 2018: added "mat_names" and "mat_lengths" property.
updated on Tue Mar 06 2018: added "from_dict" method.
"""

import numpy as np
#from pykeri.thermoelectrics.TEProp_xls import TEProp
#from pykeri.thermoelectrics.segment import Segment

from pykeri.thermoelectrics.solver1d.segment import Segment
from pykeri.thermoelectrics.TEProp_xls import TEProp


class LegSpecError(Exception):
    pass

class Leg:
    """
    Define a thermoelectric leg.
    """
    def __init__( self, segment, A, pn_type='p' ):
        self.seg = segment
        self.A = A
        self.pn_type = pn_type
        self.xs = segment.grid()
        self.L = self.xs[-1]
        self.mesh_size = len(self.xs)
        
    @staticmethod
    def from_dict(a_dict):
        """
        'a_dict' is a dictionary containing the following information on a leg:
            'type': 'p' or 'n',
            'length': the total length of a leg,
            'area': the cross-sectional area of a leg,
            'materials': a list of materials,
            'material_ratios': the ratio of length of each material,
            'material_lengths': the length of each material,
            'interfaces': a list of interface materials,
            'interface_lengths': the length of each material,
            'min_length_per_grid': for mesh generation,
            'max_num_of_grid_per_interval': for mesh generation
        
        Create and return a Leg object.
        """
        # extract info from a_dict
        pn_type = a_dict.get('type', 'p')
        L       = a_dict.get('length', None)
        A       = a_dict['area']
        raw_materials = a_dict['materials']
        raw_material_ratios = a_dict.get('material_ratios', None)
        raw_material_lengths = a_dict.get('material_lengths', None)
        raw_interfaces = a_dict.get('interfaces', [])
        raw_interface_lengths = a_dict.get('interface_lengths', None)
        min_length_per_grid = a_dict.get('min_length_per_grid', L/100)
        max_num_of_grid_per_interval = a_dict.get('max_num_of_grid_per_interval', 50)
        
        # construct materials
        materials = []
        for raw_mat in raw_materials:
            if isinstance(raw_mat, dict):  # if the material is given by a dictionary
                mat = TEProp.from_dict(raw_mat)
                materials.append(mat)
            else:
                materials.append(raw_mat)
        num_mats = len(materials)
        # construct inteface materials
        interfaces = []
        for raw_mat in raw_interfaces:
            if isinstance(raw_mat, dict):  # if the material is given by a dictionary
                mat = TEProp.from_dict(raw_mat)
                interfaces.append(mat)
            else:
                interfaces.append(raw_mat)
        # construct interface lengths
        if raw_interface_lengths is None:
            interfaces = [None]*(num_mats+1)
            interface_lengths = [0]*(num_mats+1)
        else:
            interface_lengths = raw_interface_lengths
        if (len(interfaces) != num_mats+1) or (len(interface_lengths) != num_mats+1):
            raise LegSpecError("Number of interfaces and interface lengths should be 'number of materials+1'")
        sum_interface_lengths = np.array(interface_lengths).sum()
        # construct material lengths
        if raw_material_lengths is None:
            if raw_material_ratios is None:  # no ratio, no lengths
                raise LegSpecError("Material lengths cannot be defined: provide 'material_ratios' or 'material_lengths'")
            elif L is None:  # ratio ok but no total length
                raise LegSpecError("Material lengths cannot be defined: need 'material_ratios' AND 'length'")
            else:  # ratios and total length are given
                ratios = np.array(raw_material_ratios)
                material_lengths = (L-sum_interface_lengths) * ratios / ratios.sum()    # true ratio
        else:
            material_lengths = raw_material_lengths
        if num_mats != len(material_lengths):
            raise LegSpecError("Number of materials and number of lengths do NOT match!")
            
        # check the structure of interfaces: updated on Thu Mar 15 2018
        if len(interfaces) != len(interface_lengths):
            raise LegSpecError("Size of 'interfaces' and 'interface_lengths' does not match.")
            
        # combine materials and interfaces
        all_lengths = []
        all_materials = []
        for idx in range(num_mats+1):
            if (interfaces[idx] is not None) and (interface_lengths[idx] > 0):   # modified on Thu Mar 15 2018
                all_materials.append(interfaces[idx])
                all_lengths.append(interface_lengths[idx])
            if (idx < num_mats) and (material_lengths[idx] > 0):
                all_materials.append(materials[idx])
                all_lengths.append(material_lengths[idx])
        # define a leg
        segment = Segment(all_lengths, all_materials, min_length_per_grid=min_length_per_grid, max_num_of_grid_per_interval=max_num_of_grid_per_interval)
        return Leg(segment, A, pn_type=pn_type)
    
    @property
    def mat_names(self):
        """
        Returns a tuple of the material names in the segment.
        """
        result = []
        for mat in self.seg._mats:
            result.append(mat.name)
        return tuple(result)
    
    @property
    def mat_lengths(self):
        """
        Returns a tuple of the lengths of each material in the segment.
        """
        return self.seg._lengths
    
    def plot_leg_TEP(self, x_label='x [m]', x_multiplier=1, show_grid=True, show_each_title=False, show_title=True):
        """
        Plot thermoelectric properties on 'x' variable and returns a Figure handle.
        """
        # unique identifies for TEProp functions: DO NOT MODIFY
        ELEC_COND = "elec_cond"
        SEEBECK   = "Seebeck"
        THRM_COND = "thrm_cond"
        
        import matplotlib.pyplot as plt
        x = self.seg._xs * x_multiplier
        T = self.steadystate.T
        elec_cond = self.seg.composition(ELEC_COND,T)
        elec_res = 1/elec_cond
        seebeck = self.seg.composition(SEEBECK,T)
        thrm_cond = self.seg.composition(THRM_COND,T)
                
        fig = plt.figure(figsize=(8,10))
        
        y_datas = [('Temperature', '[K]', T),
                   (None, None, None),
                   ('Electrical Conductivity', '[S/cm]', elec_cond *1e-2),
                   ('Electrical Resistivity', '[$\mu\Omega$ m]', elec_res *1e6),
                   ('Seebeck Coefficient', '[$\mu$V/K]', seebeck *1e6),
                   ('Thermal Conductivity', '[W/m/K]', thrm_cond),
                   ('Power Factor', '[mW/m/K$^2$]', seebeck**2*elec_cond *1e3),
                   ('Figure of Merit (ZT)', '[1]', seebeck**2*elec_cond/thrm_cond*T)]
        
        for idx, data in enumerate(y_datas):
            plt.subplot(4,2,idx+1)
            title, unit, y = data
            if y is None:
                plt.text(0.5, 0.5, 'pykeri by JChung,BKRyu', horizontalalignment='center')
                plt.axis('off')
                continue
            plt.plot(x, y)
            plt.xlabel(x_label)
            if show_each_title:
                plt.ylabel(unit)
                plt.title(title)
            else:
                plt.ylabel(title+'\n'+unit)
            plt.grid(show_grid)

        fig.tight_layout(pad=2)
        
        if show_title:
            fig.suptitle("Thermoelectric Properties of " + self.pn_type +"-type Leg", size=16)
            if show_each_title:
                fig.subplots_adjust(top=0.9)
            else:
                fig.subplots_adjust(top=0.93)
        return fig
    
    @property
    def mats(self):
        return self.seg.mats
    
    def plot_mat_TEP(self, mat_pos, Tc, Th, num_grid=50, **plt_kwargs):
        T = np.linspace(Tc, Th, num=num_grid)
        fig = self.mats[mat_pos].plot(T, **plt_kwargs)
        return fig

    def plot_mat_TEP2(self, x_label='T [K]', x_multiplier=1, show_grid=True, show_each_title=False, show_title=True, print_result=True):
        """
        Plot thermoelectric properties on 'x' variable and returns a Figure handle.
        """
        # unique identifies for TEProp functions: DO NOT MODIFY
        ELEC_COND = "elec_cond"
        SEEBECK   = "Seebeck"
        THRM_COND = "thrm_cond"
        
        import matplotlib.pyplot as plt
        x = self.seg._xs * x_multiplier
        T = self.steadystate.T
        elec_cond = self.seg.composition(ELEC_COND,T)
        elec_res = 1/elec_cond
        seebeck = self.seg.composition(SEEBECK,T)
        thrm_cond = self.seg.composition(THRM_COND,T)
                
        fig = plt.figure(figsize=(8,10))
        
        y_datas = [('Temperature', '[K]', T),
                   (None, None, None),
                   ('Electrical Conductivity', '[S/cm]', elec_cond *1e-2),
                   ('Electrical Resistivity', '[$\mu\Omega$ m]', elec_res *1e6),
                   ('Seebeck Coefficient', '[$\mu$V/K]', seebeck *1e6),
                   ('Thermal Conductivity', '[W/m/K]', thrm_cond),
                   ('Power Factor', '[mW/m/K$^2$]', seebeck**2*elec_cond *1e3),
                   ('Figure of Merit (ZT)', '[1]', seebeck**2*elec_cond/thrm_cond*T)]
        
        for idx, data in enumerate(y_datas):
            plt.subplot(4,2,idx+1)
            title, unit, y = data
            if y is None:
                plt.text(0.5, 0.5, 'pykeri by JChung,BKRyu', horizontalalignment='center')
                plt.axis('off')
                continue
            #plt.plot(x, y)
            plt.plot(T, y)
            plt.xlabel(x_label)
            if show_each_title:
                plt.ylabel(unit)
                plt.title(title)
            else:
                plt.ylabel(title+'\n'+unit)
            plt.grid(show_grid)

        fig.tight_layout(pad=2)
        
        if (print_result==True):
            for counta in range(len(T)):
                print(T[counta],x[counta],elec_cond[counta],elec_res[counta],seebeck[counta],thrm_cond[counta],seebeck[counta]**2*elec_cond[counta],seebeck[counta]**2*elec_cond[counta]/thrm_cond[counta]*T[counta])
            
        
        if show_title:
            fig.suptitle("Thermoelectric Properties of " + self.pn_type +"-type Leg", size=16)
            if show_each_title:
                fig.subplots_adjust(top=0.9)
            else:
                fig.subplots_adjust(top=0.93)
        return fig
        
    def plot(self, length_unit='[m]', length_multiplier=1, show_legend=False, show_mat_name=True):
        """
        Plot the structure of a leg. Assume "TEProp.color" attribute exists.
        Returns the figure handle.
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        x_size = np.sqrt(self.A) * length_multiplier
        y_size = self.L * length_multiplier
        y_pos = 0
        fig = plt.figure()
        ax = fig.add_subplot(111, aspect='equal')
        for mat, length in zip(self.mats, self.mat_lengths):
            name = mat.name
            length = length * length_multiplier
            if not hasattr(mat, 'color'):
                raise AttributeError("Material does NOT have 'color' attribute.")
            color = mat.color
            p = patches.Rectangle( (0, y_pos), x_size, length, facecolor=color, label=name )
            ax.add_patch(p)
            if show_mat_name:
                plt.text(0+x_size/2, y_pos+length/2, name, ha='center', va='center', color='w')  # plot material name
            y_pos += length
        if show_legend:
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)
        # add Th, Tc and labels
        x_mid   = (0+x_size)/2
        plt.text(x_mid, 0, '$T_h$', ha='center', va='bottom', color='k')
        plt.text(x_mid, y_size, '$T_c$', ha='center', va='top', color='k')
        ax.set_xlim(0, x_size)
        ax.set_ylim(0, y_size)
        plt.xlabel('area$^{1/2}$ '+length_unit)
        plt.ylabel('length '+length_unit)
        
        return fig