# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 09:12:12 2018

@author: 정재환
"""

import numpy as np
import time


from pykeri.thermoelectrics.solver1d.environment import Environment
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.device import Device
from pykeri.thermoelectrics.TEProp import TEProp
from pykeri.util.partition import number_partition, generate_fixed_num_stages
from pykeri.util.misc import print_progress    


def put_and_sort( sorted_names, descending_scores, new_name, new_score, maintain_size ):
    """
    Add 'new_name' and 'new_score' and maintain the 'descending_scores' as descending.
    'sorted_names' and 'descending_scores' should be lists.
    """
    inserting_idx = None
    for idx, score in enumerate(descending_scores):  # in ascending order
        if new_score > score:
            inserting_idx = idx
            break
    if inserting_idx is not None:
        sorted_names.insert(inserting_idx, new_name)
        descending_scores.insert(inserting_idx, new_score)
    else:
        sorted_names.append(new_name)
        descending_scores.append(new_score)
    # maintain the size of the list
    size = len(sorted_names)
    while size > maintain_size:
        sorted_names.pop(-1)
        descending_scores.pop(-1)
        size = len(sorted_names)


def rank_mats_as_leg(**kwargs):
    """
    Changing materials, find top rank legs. Return devices of the single leg.
    Need to specify:
        pn_type: 'p' or 'n'. default='p'
        length: total length of a leg
        area
        materials
        interface_mat: optional. default=None
        interface_length: optional. default=0
        multiplier: Optional. default=1
        env
        num_ranks: Integer. how many devices you are interested. default=1
        max_num_stages: Integer. How many sgements are there. default=1
        resolution: integer. the base unit length is 'L/resolution'. default=1
        mode: 'max efficiency' or 'max power'.
        show_alert: Optional. default=True.
        min_length_per_grid: Optional: default=length/100
        max_num_of_grid_per_interval: Optional. default=50
    """    
    # process the input
    pn_type = kwargs.get('pn_type', 'p')
    length = kwargs['length']
    area = kwargs['area']
    materials = kwargs['materials']
    interface_mat = kwargs.get('interface_mat', None)
    interface_length = kwargs.get('interface_length', 0)
    multiplier = kwargs.get('multiplier', 1)
    env = kwargs['env']
    num_ranks = kwargs.get('num_ranks', 1)
    max_num_stages = kwargs.get('max_num_stages', 1)
    resolution = kwargs.get('resolution', 1)
    mode = kwargs['mode']
    show_alert = kwargs.get('show_alert', True)
    min_length_per_grid = kwargs.get('min_length_per_grid', length/100)
    max_num_of_grid_per_interval = kwargs.get('max_num_of_grid_per_interval', 50)

    # rank materials    
    num_mats = len(materials)

    # estimate number of tasks
    total_count = 0
    for num_stages in range(1,max_num_stages+1):
        for mat_structure in generate_fixed_num_stages(num_elems=num_mats, num_stages=num_stages):  # p-materials
            for length_structure in number_partition( natural_number=resolution, number_of_partitions=num_stages, min_number=1 ):
                total_count += 1
    
    if show_alert:
        # estimate time cost per task
        TIME_REQUIRED = estimate_time_cost_per_leg()  # sec for each computation

        total_minutes = TIME_REQUIRED*total_count/60
        if total_minutes >= 1:
            print("The computation can take %.2f minutes (%d possible device structures)" % (total_minutes, total_count))
        else:
            print("The computation can take %.2f seconds (%d possible device structures)" % (total_minutes*60, total_count))
        yn = input("Will you continue? (y/(n)) ")
        if yn != 'y':
            print("Computation interrupted.")
            return None, None
        
    ## do the computation
    tic = time.clock()
    count = 0
    devs = []
    scores = []
    print("Computing:")
    for num_stages in range(1,max_num_stages+1):
        for mat_structure in generate_fixed_num_stages(num_elems=num_mats, num_stages=num_stages):
            for length_structure in number_partition( natural_number=resolution, number_of_partitions=num_stages, min_number=1 ):
                mats = [materials[idx] for idx in mat_structure]
                leg = Leg.from_dict( {
                        'type': pn_type,
                        'length': length,
                        'area': area,
                        'materials': mats,
                        'material_ratios': length_structure,
                        'interfaces': [interface_mat]*(len(mats)+1),
                        'interface_lengths': [interface_length]*(len(mats)+1),
                        'min_length_per_grid': min_length_per_grid,        # for mesh generation
                        'max_num_of_grid_per_interval': max_num_of_grid_per_interval   # for mesh generation; omissible
                        } )
                    
                device_spec = {
                    'global_env': env,
                    'legs': [leg],
                    'multipliers': [multiplier]
                    }
                dev = Device.from_dict(device_spec)
                
                if mode == 'max efficiency':
                    dev.run_with_max_efficiency()
                    score = dev.efficiency
                elif mode == 'max power':
                    dev.run_with_max_power()
                    score = dev.power
                else:
                    raise ValueError("Wrong 'mode': choose 'max efficiency' or 'max power'.")
                                            
                put_and_sort(devs, scores, dev, score, maintain_size=num_ranks)
                
                count += 1
                print_progress(count/total_count)
    
    toc = time.clock()
    print('\n>>', total_count, 'possible devices are computed in ', toc-tic, 'seconds. <<')
    
    return devs, scores

def estimate_time_cost_per_leg(num_iteration=3, verbose=False):
    """
    Returns average time (sec) to compute one leg.
    """
    # define p-type test material properties (BST-Ag0.05(HP))
    elec_resi_raw_data = ((298.15,1/81955), (373.15,1/64394), (423.15,1/51772), (473.15,1/43850), (523.15,1/39214), (573.15,1/37487))
    Seebeck_raw_data = ((298.15,2.01E-04), (373.15,2.15E-04), (423.15,2.18E-04), (473.15,2.12E-04), (523.15,1.92E-04), (573.15,1.66E-04))
    thrm_cond_raw_data = ((298.15,0.95), (373.15,0.89), (423.15,0.92), (473.15,1.00), (523.15,1.15), (573.15,1.33))
    p_type_tep = TEProp.from_raw_data(elec_resi_raw_data,Seebeck_raw_data,thrm_cond_raw_data,name="BST-Ag0.05(HP)")
    
    length = 1/1000 *    2.5     # unit of m
    area   = 1/1000**2 * 3*3     # unit of m^2
    N_pairs    = 50                  # unit of number
    
    Tcold = 320
    Thot  = 550
    
    global_env = Environment.from_dict( {
           'Th': Thot,
           'Tc': Tcold
           } )
    leg = Leg.from_dict( {
            'type': 'p',
            'length': length,
            'area': area,
            'materials': [p_type_tep],
            'material_ratios': [100],
            } )    
    dev = Device.from_dict( {
        'global_env': global_env,
        'legs': [leg],
        'multipliers': [N_pairs]
        } )

    if verbose:
        print("Estimating time cost per each leg computation...  ", end='')
    tic = time.clock()
    for idx in range(num_iteration):
        dev.run_with_max_efficiency()
    toc = time.clock()
    if verbose:
        print("complete.")
    
    return (toc-tic)/num_iteration * 2   # overestimate for complicated legs

def estimate_time_cost_per_device(num_iteration=3, verbose=False):
    """
    Returns average time (sec) to compute one device.
    """
    # define p-type test material properties (BST-Ag0.05(HP))
    elec_resi_raw_data = ((298.15,1/81955), (373.15,1/64394), (423.15,1/51772), (473.15,1/43850), (523.15,1/39214), (573.15,1/37487))
    Seebeck_raw_data = ((298.15,2.01E-04), (373.15,2.15E-04), (423.15,2.18E-04), (473.15,2.12E-04), (523.15,1.92E-04), (573.15,1.66E-04))
    thrm_cond_raw_data = ((298.15,0.95), (373.15,0.89), (423.15,0.92), (473.15,1.00), (523.15,1.15), (573.15,1.33))
    p_type_tep = TEProp.from_raw_data(elec_resi_raw_data,Seebeck_raw_data,thrm_cond_raw_data,name="BST-Ag0.05(HP)")
    
    # define n-type test material properties (Pb1.02Te1Bi0.002)
    elec_resi_raw_data = ((298,1/84754), (323,1/73865), (373,1/52789), (423,1/37808), (473,1/28186), (523,1/21461), (573,1/17083))
    Seebeck_raw_data = ((298,-2.06E-04), (323,-2.12E-04), (373,-2.39E-04), (423,-2.61E-04), (473,-2.79E-04), (523,-2.97E-04), (573,-3.09E-04))
    thrm_cond_raw_data = ((298,2.32), (323,2.14), (373,1.82), (423,1.56), (473,1.35), (523,1.19), (573,1.07))
    n_type_tep = TEProp.from_raw_data(elec_resi_raw_data,Seebeck_raw_data,thrm_cond_raw_data,name="Pb1.02Te1Bi0.002")


    length = 1/1000 *    2.5     # unit of m
    area   = 1/1000**2 * 3*3     # unit of m^2
    N_pairs    = 50                  # unit of number
    
    Tcold = 320
    Thot  = 550
    
    global_env = Environment.from_dict( {
           'Th': Thot,
           'Tc': Tcold
           } )
    pLeg = Leg.from_dict( {
            'type': 'p',
            'length': length,
            'area': area,
            'materials': [p_type_tep],
            'material_ratios': [100],
            } )
    nLeg = Leg.from_dict( {
            'type': 'n',
            'length': length,
            'area': area,
            'materials': [n_type_tep],
            'material_ratios': [100],
            } )
    
    dev = Device.from_dict( {
        'global_env': global_env,
        'legs': [pLeg, nLeg],
        'multipliers': [N_pairs, N_pairs]
        } )

    if verbose:
        print("Estimating time cost per each device computation...  ", end='')
    tic = time.clock()
    for idx in range(num_iteration):
        dev.run_with_max_efficiency()
    toc = time.clock()
    if verbose:
        print("complete.")
    
    return (toc-tic)/num_iteration * 2.26   # overestimate for complicated devices


def fast_rank_mats_as_device(**kwargs):
    """
    Changing materials, find top rank devices.
    
    Warning: This method produces inaccurate result; but 2.7 times faster than "rank_mats_as_device()" function.
    
    Need to specify:
        p_materials
        n_materials
        p_interface_mat: optional. default=None
        p_interface_length: optional. default=0
        n_interface_mat: optional. default=None
        n_interface_length: optional. default=0
        length
        p_area
        n_area
        p_multiplier: Optional. default=1
        n_multiplier: Optional. default=1
        global_env
        num_ranks: Integer. how many devices you are interested. default=1
        max_num_stages: Integer. How many sgements are there. default=1
        resolution: integer. the base unit length is 'L/resolution'. default=1
        mode: 'max efficiency' or 'max power'.
        show_alert: Optional. default=True.
        min_length_per_grid: Optional: default=length/100
        max_num_of_grid_per_interval: Optional. default=50
    """
    
    # process the input
    p_materials = kwargs['p_materials']
    n_materials = kwargs['n_materials']
    p_interface_mat = kwargs.get('p_interface_mat', None)
    p_interface_length = kwargs.get('p_interface_length', 0)
    n_interface_mat = kwargs.get('n_interface_mat', None)
    n_interface_length = kwargs.get('n_interface_length', 0)
    length = kwargs['length']
    p_area = kwargs['p_area']
    n_area = kwargs['n_area']
    p_multiplier = kwargs.get('p_multiplier', 1)
    n_multiplier = kwargs.get('n_multiplier', 1)
    global_env = kwargs['global_env']
    num_ranks = kwargs.get('num_ranks', 1)
    max_num_stages = kwargs.get('max_num_stages', 1)
    resolution = kwargs.get('resolution', 1)
    mode = kwargs['mode']
    show_alert = kwargs.get('show_alert', True)
    min_length_per_grid = kwargs.get('min_length_per_grid', length/100)
    max_num_of_grid_per_interval = kwargs.get('max_num_of_grid_per_interval', 50)

    # rank materials    
    num_p_mats = len(p_materials)
    num_n_mats = len(n_materials)
    
    # estimate the number of tasks
    total_count = 0
    for num_p_mat_stages in range(1,max_num_stages+1):
        for p_mat_structure in generate_fixed_num_stages(num_elems=num_p_mats, num_stages=num_p_mat_stages):  # p-materials
            for length_structure in number_partition( natural_number=resolution, number_of_partitions=num_p_mat_stages, min_number=1 ):
                for num_n_mat_stages in range(1,max_num_stages+1):
                    for n_mat_structure in generate_fixed_num_stages(num_elems=num_n_mats, num_stages=num_n_mat_stages):  # n-materials
                        for length_structure in number_partition( natural_number=resolution, number_of_partitions=num_n_mat_stages, min_number=1 ):
                            total_count += 1    
    
    if show_alert:
        # estimate time cost per task
        TIME_REQUIRED = estimate_time_cost_per_device() / 2.7  # sec for each computation; fast method is faster
        
        total_minutes = TIME_REQUIRED*total_count/60
        if total_minutes >= 1:
            print("The computation can take %.2f minutes (%d possible device structures)" % (total_minutes, total_count))
        else:
            print("The computation can take %.2f seconds (%d possible device structures)" % (total_minutes*60, total_count))
        yn = input("Will you continue? (y/(n)) ")
        if yn != 'y':
            print("Computation interrupted.")
            return None, None
        
    ## do the computation
    tic = time.clock()
    count = 0
    devs = []
    scores = []
    print("Computing:")
    for num_p_mat_stages in range(1,max_num_stages+1):
        for p_mat_structure in generate_fixed_num_stages(num_elems=num_p_mats, num_stages=num_p_mat_stages):  # p-materials
            for p_mat_length_structure in number_partition( natural_number=resolution, number_of_partitions=num_p_mat_stages, min_number=1 ):
                pMats = [p_materials[idx] for idx in p_mat_structure]
                pLeg = Leg.from_dict( {
                        'type': 'p',
                        'length': length,
                        'area': p_area,
                        'materials': pMats,
                        'material_ratios': p_mat_length_structure,
                        'interfaces': [p_interface_mat]*(len(pMats)+1),
                        'interface_lengths': [p_interface_length]*(len(pMats)+1),
                        'min_length_per_grid': min_length_per_grid,        # for mesh generation
                        'max_num_of_grid_per_interval': max_num_of_grid_per_interval   # for mesh generation; omissible
                        } )
    
                for num_n_mat_stages in range(1,max_num_stages+1):
                    for n_mat_structure in generate_fixed_num_stages(num_elems=num_n_mats, num_stages=num_n_mat_stages):  # n-materials
                        for n_mat_length_structure in number_partition( natural_number=resolution, number_of_partitions=num_n_mat_stages, min_number=1 ):
                            nMats = [n_materials[idx] for idx in n_mat_structure]
                            nLeg = Leg.from_dict( {
                                    'type': 'n',
                                    'length': length,
                                    'area': n_area,
                                    'materials': nMats,
                                    'material_ratios': n_mat_length_structure,
                                    'interfaces': [n_interface_mat]*(len(nMats)+1),
                                    'interface_lengths': [n_interface_length]*(len(nMats)+1),
                                    'min_length_per_grid': min_length_per_grid,        # for mesh generation
                                    'max_num_of_grid_per_interval': max_num_of_grid_per_interval   # for mesh generation; omissible
                                    } )
        
                            device_spec = {
                                'global_env': global_env,
                                'legs': [pLeg, nLeg],
                                'multipliers': [p_multiplier,n_multiplier]
                                }
                            dev = Device.from_dict(device_spec)
                            
                            if mode == 'max efficiency':
                                dev.fast_run_with_max_efficiency()
                                score = dev.efficiency
                            elif mode == 'max power':
                                dev.fast_run_with_max_power()
                                score = dev.power
                            else:
                                raise ValueError("Wrong 'mode': choose 'max efficiency' or 'max power'.")
                                                        
                            put_and_sort(devs, scores, dev, score, maintain_size=num_ranks)
                            
                            count += 1
                            print_progress(count/total_count)
    
    toc = time.clock()
    print('\n>>', total_count, 'possible devices are computed in ', toc-tic, 'seconds. <<')
    
    return devs, scores


def rank_mats_as_device(**kwargs):
    """
    Changing materials, find top rank devices.
    Need to specify:
        p_materials
        n_materials
        p_interface_mat: optional. default=None
        p_interface_length: optional. default=0
        n_interface_mat: optional. default=None
        n_interface_length: optional. default=0
        length
        p_area
        n_area
        p_multiplier: Optional. default=1
        n_multiplier: Optional. default=1
        global_env
        num_ranks: Integer. how many devices you are interested. default=1
        max_num_stages: Integer. How many sgements are there. default=1
        resolution: integer. the base unit length is 'L/resolution'. default=1
        mode: 'max efficiency' or 'max power'.
        show_alert: Optional. default=True.
        min_length_per_grid: Optional: default=length/100
        max_num_of_grid_per_interval: Optional. default=50
    """    
    # process the input
    p_materials = kwargs['p_materials']
    n_materials = kwargs['n_materials']
    p_interface_mat = kwargs.get('p_interface_mat', None)
    p_interface_length = kwargs.get('p_interface_length', 0)
    n_interface_mat = kwargs.get('n_interface_mat', None)
    n_interface_length = kwargs.get('n_interface_length', 0)
    length = kwargs['length']
    p_area = kwargs['p_area']
    n_area = kwargs['n_area']
    p_multiplier = kwargs.get('p_multiplier', 1)
    n_multiplier = kwargs.get('n_multiplier', 1)
    global_env = kwargs['global_env']
    num_ranks = kwargs.get('num_ranks', 1)
    max_num_stages = kwargs.get('max_num_stages', 1)
    resolution = kwargs.get('resolution', 1)
    mode = kwargs['mode']
    show_alert = kwargs.get('show_alert', True)
    min_length_per_grid = kwargs.get('min_length_per_grid', length/100)
    max_num_of_grid_per_interval = kwargs.get('max_num_of_grid_per_interval', 50)

    # rank materials    
    num_p_mats = len(p_materials)
    num_n_mats = len(n_materials)
    # estimate the number of tasks
    total_count = 0
    for num_p_mat_stages in range(1,max_num_stages+1):
        for p_mat_structure in generate_fixed_num_stages(num_elems=num_p_mats, num_stages=num_p_mat_stages):  # p-materials
            for length_structure in number_partition( natural_number=resolution, number_of_partitions=num_p_mat_stages, min_number=1 ):
                for num_n_mat_stages in range(1,max_num_stages+1):
                    for n_mat_structure in generate_fixed_num_stages(num_elems=num_n_mats, num_stages=num_n_mat_stages):  # n-materials
                        for length_structure in number_partition( natural_number=resolution, number_of_partitions=num_n_mat_stages, min_number=1 ):
                            total_count += 1    
    
    if show_alert:
        # estimate time cost per task
        TIME_REQUIRED = estimate_time_cost_per_device()   # sec for each computation

        total_minutes = TIME_REQUIRED*total_count/60
        if total_minutes >= 1:
            print("The computation can take %.2f minutes (%d possible device structures)" % (total_minutes, total_count))
        else:
            print("The computation can take %.2f seconds (%d possible device structures)" % (total_minutes*60, total_count))
        yn = input("Will you continue? (y/(n)) ")
        if yn != 'y':
            print("Computation interrupted.")
            return None, None
        
    ## do the computation
    tic = time.clock()
    count = 0
    devs = []
    scores = []
    print("Computing:")
    for num_p_mat_stages in range(1,max_num_stages+1):
        for p_mat_structure in generate_fixed_num_stages(num_elems=num_p_mats, num_stages=num_p_mat_stages):  # p-materials
            for p_mat_length_structure in number_partition( natural_number=resolution, number_of_partitions=num_p_mat_stages, min_number=1 ):
                pMats = [p_materials[idx] for idx in p_mat_structure]
                pLeg = Leg.from_dict( {
                        'type': 'p',
                        'length': length,
                        'area': p_area,
                        'materials': pMats,
                        'material_ratios': p_mat_length_structure,
                        'interfaces': [p_interface_mat]*(len(pMats)+1),
                        'interface_lengths': [p_interface_length]*(len(pMats)+1),
                        'min_length_per_grid': min_length_per_grid,        # for mesh generation
                        'max_num_of_grid_per_interval': max_num_of_grid_per_interval   # for mesh generation; omissible
                        } )
    
                for num_n_mat_stages in range(1,max_num_stages+1):
                    for n_mat_structure in generate_fixed_num_stages(num_elems=num_n_mats, num_stages=num_n_mat_stages):  # n-materials
                        for n_mat_length_structure in number_partition( natural_number=resolution, number_of_partitions=num_n_mat_stages, min_number=1 ):
                            nMats = [n_materials[idx] for idx in n_mat_structure]
                            nLeg = Leg.from_dict( {
                                    'type': 'n',
                                    'length': length,
                                    'area': n_area,
                                    'materials': nMats,
                                    'material_ratios': n_mat_length_structure,
                                    'interfaces': [n_interface_mat]*(len(nMats)+1),
                                    'interface_lengths': [n_interface_length]*(len(nMats)+1),
                                    'min_length_per_grid': min_length_per_grid,        # for mesh generation
                                    'max_num_of_grid_per_interval': max_num_of_grid_per_interval   # for mesh generation; omissible
                                    } )
        
                            device_spec = {
                                'global_env': global_env,
                                'legs': [pLeg, nLeg],
                                'multipliers': [p_multiplier,n_multiplier]
                                }
                            dev = Device.from_dict(device_spec)
                            
                            if mode == 'max efficiency':
                                dev.run_with_max_efficiency()
                                score = dev.efficiency
                            elif mode == 'max power':
                                dev.run_with_max_power()
                                score = dev.power
                            else:
                                raise ValueError("Wrong 'mode': choose 'max efficiency' or 'max power'.")
                                                        
                            put_and_sort(devs, scores, dev, score, maintain_size=num_ranks)
                            
                            count += 1
                            print_progress(count/total_count)
    
    toc = time.clock()
    print('\n>>', total_count, 'possible devices are computed in ', toc-tic, 'seconds. <<')
    
    return devs, scores


def spec_tables(device_spec_dict, Th_list, Tc_list, mode='max power', given_no_loop=None, max_no_loop=100, abs_tol=1e-6):
    """
    Return a dictionary of pandas tables. Each table describes performance values with given Th and Tc.
    """
    import pandas as pd
    dev = Device.from_dict(device_spec_dict)

    # init empty lists
    list_I = []
    list_QhA = []
    list_Vgen = []
    list_R_TE = []
    list_K_TE = []
    list_efficiency = []
    list_power = []
    
    for Tc in Tc_list:
        for Th in Th_list:
            if Th <= Tc:   # if condition is inappropriate, fill with NaNs.
                list_I.append(np.nan)
                list_QhA.append(np.nan)
                list_Vgen.append(np.nan)
                list_R_TE.append(np.nan)
                list_K_TE.append(np.nan)
                list_efficiency.append(np.nan)
                list_power.append(np.nan)
                continue
            # set the global Environment
            global_env = Environment(Th, Tc)
            dev.set_all_envs(global_env)
            # solve the problem
            if mode == 'max power' or mode == 'maximum power':
                dev.run_with_max_power(given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=True)
            elif mode == 'max efficiency' or mode == 'maximum efficiency':
                dev.run_with_max_efficiency(given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=True)
            else:
                raise ValueError("The option 'mode' can be 'max power' or 'max efficiency'.")
            # remember the result
            list_I.append(dev.I)
            list_QhA.append(dev.QhA)
            list_Vgen.append(dev.Vgen)
            list_R_TE.append(dev.R_TE)
            list_K_TE.append(dev.K_TE)
            list_efficiency.append(dev.efficiency)
            list_power.append(dev.power)

    # construct a dictionary of pandas tables
    dict_tables = {}
    x_size = len(Th_list)
    y_size = len(Tc_list)
    x_index = pd.Index(Th_list, name='Th')
    y_index = pd.Index(Tc_list, name='Tc')

    dict_tables['I'] = pd.DataFrame( np.array(list_I).reshape(y_size,x_size), index=y_index, columns=x_index )
    dict_tables['QhA'] = pd.DataFrame( np.array(list_QhA).reshape(y_size,x_size), index=y_index, columns=x_index )
    dict_tables['Vgen'] = pd.DataFrame( np.array(list_Vgen).reshape(y_size,x_size), index=y_index, columns=x_index )
    dict_tables['R_TE'] = pd.DataFrame( np.array(list_R_TE).reshape(y_size,x_size), index=y_index, columns=x_index )
    dict_tables['K_TE'] = pd.DataFrame( np.array(list_K_TE).reshape(y_size,x_size), index=y_index, columns=x_index )
    dict_tables['efficiency'] = pd.DataFrame( np.array(list_efficiency).reshape(y_size,x_size), index=y_index, columns=x_index )
    dict_tables['power'] = pd.DataFrame( np.array(list_power).reshape(y_size,x_size), index=y_index, columns=x_index )

    return dict_tables