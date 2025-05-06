# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 07:33:55 2017

@author: Jaywan Chung

Functions relevant to the Constant Properties Model (CPM)
"""

def material_figure_of_merit(Seebeck_coef, electrical_resistivity, thermal_conductivity):
    alpha = Seebeck_coef
    rho = electrical_resistivity
    kappa = thermal_conductivity
    return alpha**2 / rho / kappa

def device_figure_of_merit(Seebeck_coef, internal_resistance, device_thermal_conductance):
    S = Seebeck_coef
    R = internal_resistance
    K = device_thermal_conductance
    return S**2 / R / K

def power_factor(Seebeck_coef, electrical_resistivity, device_length, device_cross_sectional_area):
    alpha = Seebeck_coef
    rho = electrical_resistivity
    L = device_length
    A = device_cross_sectional_area
    R = L/A*rho
    return alpha**2 / R

def maximum_efficiency(Seebeck_coef, electrical_resistivity, thermal_conductivity, hot_side_temperature, cold_side_temperature):
    alpha = Seebeck_coef
    rho = electrical_resistivity
    kappa = thermal_conductivity
    Th = hot_side_temperature
    Tc = cold_side_temperature
    # computation
    z = material_figure_of_merit(alpha, rho, kappa)
    Z = z
    Tm = (Th+Tc)/2
    deltaT = Th-Tc
    from numpy import sqrt
    max_eta = deltaT/Th * ( sqrt(1+Z*Tm)-1 ) / ( sqrt(1+Z*Tm) +Tc/Th )
    
    return max_eta

def maximum_power(Seebeck_coef, electrical_resistivity, device_length, device_cross_sectional_area, hot_side_temperature, cold_side_temperature):
    alpha = Seebeck_coef
    rho = electrical_resistivity
    L = device_length
    A = device_cross_sectional_area
    Th = hot_side_temperature
    Tc = cold_side_temperature
    # computation
    R = L/A*rho
    deltaT = Th-Tc
    max_power = alpha**2 * (deltaT)**2 / (4*R)
    
    return max_power