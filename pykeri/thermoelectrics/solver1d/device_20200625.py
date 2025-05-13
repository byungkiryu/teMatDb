# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 11:22:29 2018

@author: Jaywan Chung

updated on Mon Mar 12 2018: bug fix "plot" function: switch the position of "Th" and "Tc".
updated on Thu Mar 08: each element of the "legs" list has a "steadystate" class as a member: e.g.: use dev.legs[0].steadystate
updated on Wed Mar 07: added "plot" method. can handle not given envs.
"""

import numpy as np
import warnings

#from pykeri.thermoelectrics.solver1d.steadystate import SteadyState
#from pykeri.thermoelectrics.solver1d.leg import Leg
#from pykeri.thermoelectrics.solver1d.environment import Environment

from pykeri.thermoelectrics.solver1d.steadystate import SteadyState
from pykeri.thermoelectrics.solver1d.leg import Leg
from pykeri.thermoelectrics.solver1d.environment import Environment


def get_num_loop(given_no_loop, max_no_loop):
    if given_no_loop is not None:
        no_loop = min(given_no_loop, max_no_loop)
    else:
        no_loop = max_no_loop
    return no_loop


class DeviceSpecError(Exception):
    pass

class Device:
    """
    Define a one-dimensional thermoelectric device.
    """
    def __init__(self, legs=[], environments=[], **kwargs):
        """
        legs: a list of Leg objects,
        environments: a list of Environment objects; each one corresponds to a Leg obejct above.
        kwargs: one of the following arguments:
            'type': 'common'; does NOT work right now,
            'length': the height of the device; does NOT work right now,
            'area': the area of the device; does NOT work right now,
            'global_env': global environment imposed when a leg has none,
            'multipliers': a list of natural numbers: each number means the number of virtual legs for each explicitly given legs.
                For example, if this value for the first leg is two, we assume there are two identical, first leg.
            
        Create and return a Device object.
        """
        self.legs = legs
        self.envs = environments
        self.pn_type     = kwargs.get("type", "common")
        self.length      = kwargs.get("length", None)
        self.area        = kwargs.get("area", None)
        self.global_env  = kwargs.get("global_env", None)
        self.multipliers = kwargs.get("multipliers", None)
        
        self.validate_all()        
        self.init_solver_results()
        

    def init_solver_results(self):
        self.Vgen = None
        self.R_TE = None
        self.I = None
        
        self.QhA = None
        self.QhA_formula = None
        self.QcA = None
        self.QcA_formula = None

        self.beta = None

    @property
    def Tc(self):
        return self.global_env.Tc
    
    @property
    def Th(self):
        return self.global_env.Th
    
    @property
    def TmPrime(self):
        """
        To define this, "global_env" is needed.
        """
        return (self.ThPrime + self.TcPrime)/2

    @property
    def ThPrime(self):
        """
        To define this, "global_env" is needed.
        """
        return self.global_env.Th - self.tau * self.global_env.deltaT

    @property
    def TcPrime(self):
        """
        To define this, "global_env" is needed.
        """
        return self.global_env.Tc - (self.tau+self.beta) * self.global_env.deltaT

    @property
    def Zgeneral(self):
        """
        To define this, "global_env" is needed.
        """
        return self.alphaBar**2 / (self.K_TE * self.R_TE)

    @property
    def tau(self):
        """
        To define "tau", "global_env" is needed.
        """
        rhs = 0
        for leg, env, mult in zip(self.legs, self.envs, self.multipliers):
            value = leg.steadystate.alphaBar * (env.Th - leg.steadystate.tau * env.deltaT) * mult
            if leg.pn_type == 'n':
                rhs -= value
            else:
                rhs += value
        if (self.alphaBar == 0.0) or (self.global_env.deltaT == 0.0):
            tau = 0.0
        else:
            tau = (self.global_env.Th - rhs/self.alphaBar) / self.global_env.deltaT
        
        return tau
    
    @property
    def K_TE(self):
        """
        To define "K_TE", "global_env" is needed.
        """
        result = 0
        for leg, env, mult in zip(self.legs, self.envs, self.multipliers):
            result += leg.steadystate.K_TE * env.deltaT * mult
        return result / self.global_env.deltaT
    
    @property
    def alphaBar(self):
        """
        To define "alphaBar", "global_env" is needed.
        """
        return self.Vgen / self.global_env.deltaT
    
    @property
    def gamma(self):
        if self.I == 0:
            return 1.00000E+20 
        else:
            return self.Vgen / (self.I * self.R_TE) - 1
    
    @property
    def R_L(self):
        return self.Vgen/self.I - self.R_TE
    
    @property
    def R_tot(self):
        return self.R_TE + self.R_L
    
    @property
    def dQA(self):
        return self.QhA - self.QcA
    
    @property
    def dQA_formular(self):
        return self.QhA_formular - self.QcA_formular
    
    @property
    def power(self):
#        return self.I**2 * self.R_L
        return self.I * ( self.Vgen - self.I * self.R_TE)
    
    @property
    def efficiency(self):
        return self.power / self.QhA

    def fast_run_with_max_efficiency(self, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, quiet=True):
        """
        To run this function, every environments should be identical.
        
        Warning: This function produces inaccurate result; but 2.7 times faster than "run_with_max_efficiency()" function.
        """
        self.assert_identical_envs()
        I_prev = 0

        self.run_with_given_I(I=I_prev, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)
        gamma = np.sqrt(1 + self.Zgeneral * self.TmPrime)
        I_next = self.Vgen / (self.R_TE * (1+gamma))

        is_convergent = self.run_with_given_I(I=I_next, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)
        self.I = I_next

        return is_convergent
    
    def run_with_max_efficiency(self, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, quiet=True):
        """
        To run this function, every environments should be identical.
        """
        self.assert_identical_envs()
        no_loop = get_num_loop(given_no_loop, max_no_loop)
        I_prev = 0
        is_convergent = False
        for idx in range(no_loop):
            self.run_with_given_I(I=I_prev, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)
            gamma = np.sqrt(1 + self.Zgeneral * self.TmPrime)
            I_next = self.Vgen / (self.R_TE * (1+gamma))
            if abs(I_next - I_prev) <= abs_tol:
                is_convergent = True
                break
            I_prev = I_next
        if not is_convergent:
            warnings.warn("The solution did NOT converge in %dth iteration." % idx)
        self.I = I_next
        is_convergent = self.run_with_given_I(I=self.I, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)

        return is_convergent

    def fast_run_with_max_power(self, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, quiet=True):
        """
        Warning: This function produces inaccurate result; but 2.7 times faster than "run_with_max_power()" function.
        """
        I_prev = 0
        gamma = 1

        self.run_with_given_I(I=I_prev, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)
        I_next = self.Vgen / (self.R_TE * (1+gamma))

        is_convergent = self.run_with_given_I(I=I_next, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)
        self.I = I_next

        return is_convergent

    def run_with_max_power(self, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, quiet=True):
        is_convergent = self.run_with_given_gamma(gamma=1, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, quiet=True)

        return is_convergent

    def run_with_given_R_L(self, R_L, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, quiet=True):
        no_loop = get_num_loop(given_no_loop, max_no_loop)
        I_prev = 0
        is_convergent = False
        for idx in range(no_loop):
            self.run_with_given_I(I=I_prev, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)
            I_next = self.Vgen / (self.R_TE + R_L)
            if abs(I_next - I_prev) <= abs_tol:
                is_convergent = True
                break
            I_prev = I_next
        if not is_convergent:
            #warnings.warn("The solution did NOT converge in %dth iteration: current mismatch |I_next - I_prev| > abs_tol=1e-6." % idx)
            print("\t\tI diverges during {:3d}th iterations: |I_next - I_prev|>abs_tol={:g}. / I_next = {:f} / R_L= {:f}\n".format(no_loop,abs_tol,I_next,R_L))
        is_convergent = self.run_with_given_I(I=self.I, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)
        self.I = I_next


        return is_convergent
    
    def run_with_given_gamma(self, gamma, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, quiet=True):
        no_loop = get_num_loop(given_no_loop, max_no_loop)
        I_prev = 0
        is_convergent = False
        for idx in range(no_loop):
            self.run_with_given_I(I=I_prev, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)
            I_next = self.Vgen / (self.R_TE * (1+gamma))
            if abs(I_next - I_prev) <= abs_tol:
                is_convergent = True
                break
            I_prev = I_next

        self.I = I_next
        if not is_convergent:
            #warnings.warn("The solution did NOT converge in %dth iteration: current mismatch |I_next - I_prev| > abs_tol=1e-6." % idx)
            print("\t\tI diverges during {:3d}th iterations: |I_next - I_prev|>abs_tol={:g}. / I_next = {:f} / gamma= {:f}\n".format(no_loop,abs_tol,I_next,gamma))
        is_convergent = self.run_with_given_I(I=self.I, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=quiet)
        
        return is_convergent
    
    def run_with_given_I(self, I, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, quiet=True):
        for idx, leg in enumerate(self.legs):
            if leg.pn_type == 'n':
                is_convergent = leg.steadystate.solve(given_no_loop=given_no_loop, max_no_loop = max_no_loop, abs_tol=abs_tol, given_I=-I, quiet=quiet)
            else:
                is_convergent = leg.steadystate.solve(given_no_loop=given_no_loop, max_no_loop = max_no_loop, abs_tol=abs_tol, given_I=I, quiet=quiet)
            if not is_convergent:
                #warnings.warn("%dth leg did NOT converge: |T-T'| L1 norm > abs_tol=1e-6." % idx)
                print("\t\tT diverges for {:3d}th leg: int|T-T'|dx/L > abs_tol={:g}.".format(idx,abs_tol))
        self.I = I
        self.update_circuit_values()

        return is_convergent
## Note: this function, given I, update T.
## Note: this function has a convergent return. However, it only returns the temperature convergence. We need current convergence checker.
    
    def update_circuit_values(self):
        self.update_Vgen()
        self.update_R_TE()
        self.update_QhA()
        self.update_QcA()
        self.update_beta()

    def update_beta(self):
        result = 0
        for leg, mult in zip(self.legs, self.multipliers):
            result += leg.steadystate.R_TE * leg.steadystate.beta * mult
        self.beta = result / self.R_TE

    def update_QhA(self):
        QhA = 0
        QhA_formular = 0
        for leg, mult in zip(self.legs, self.multipliers):
            QhA += leg.steadystate.QhA * mult
            QhA_formular += leg.steadystate.QhA_formular * mult
        self.QhA = QhA
        self.QhA_formular = QhA_formular        

    def update_QcA(self):
        QcA = 0
        QcA_formular = 0
        for leg, mult in zip(self.legs, self.multipliers):
            QcA += leg.steadystate.QcA * mult
            QcA_formular += leg.steadystate.QcA_formular * mult
        self.QcA = QcA
        self.QcA_formular = QcA_formular
    
    def update_Vgen(self):
        Vgen = 0
        for leg, mult in zip(self.legs, self.multipliers):
            if leg.pn_type == 'n':
                Vgen -= leg.steadystate.Vgen * mult
            else:
                Vgen += leg.steadystate.Vgen * mult
        self.Vgen = Vgen
        
    def update_R_TE(self):
        R_TE = 0
        for leg, mult in zip(self.legs, self.multipliers):
            R_TE += leg.steadystate.R_TE * mult
        self.R_TE = R_TE

    def validate_all(self):
        self.validate_global_env()
        self.validate_legs()
        self.validate_envs()
        self.validate_multipliers()
        
        if self.length is None:
            self.update_length()
        if self.area is None:
            self.update_area()
        self.update_steadystates()

    def validate_global_env(self):
        if isinstance(self.global_env, dict):
            self.global_env = Environment.from_dict(self.global_env)

    def update_steadystates(self):
        for leg, env in zip(self.legs, self.envs):
            leg.steadystate = SteadyState(leg, env, debugging=False)   # add new member for each leg
        self.init_solver_results   # new steadystates => blank results

    def update_length(self):
        """
        Update the height of the device by the maximum length among the legs
        """
        leg_lengths = np.array( [leg.L for leg in self.legs] )
        self.length = leg_lengths.max()

    def update_area(self):
        """
        Update the area of the device by the total sum of the area of the legs
        """
        leg_areas = np.array( [leg.A for leg in self.legs] )
        self.area = leg_areas.sum()
        
    def validate_legs(self):
        """
        Convert all dictionary elements in legs to a Leg object.
        """
        result = []
        for leg_elem in self.legs:
            if isinstance(leg_elem, dict):
                leg = Leg.from_dict(leg_elem)
                result.append(leg)
            else:
                result.append(leg_elem)
        self.legs = result
        
    def set_all_envs(self, global_env):
        """Set all the Environments to the given global one."""
        self.global_env = global_env
        self.validate_global_env()
        self.envs = [self.global_env] * len(self.legs)
        self.update_steadystates()        

    def validate_envs(self):
        """
        Convert all dictionary elements in envs to a Environment object.
        Also set them to the global environment if they are not given.
        """
        result = []
        for env_elem in self.envs:
            if isinstance(env_elem, dict):
                env = Environment.from_dict(env_elem)
                result.append(env)
            elif env_elem is None:
                result.append(self.global_env)
            else:
                result.append(env_elem)
        self.envs = result
        
    def validate_multipliers(self):
        """Fill the 'None' multipliers by list of 1's."""
        if self.multipliers is None:
            self.multipliers = [1]*len(self.legs)
            
    def assert_identical_envs(self):
        """Check all the local and global environments are the same."""
        if self.global_env is None:
            raise DeviceSpecError("The global Environment should be given!")
        Th = self.global_env.Th
        Tc = self.global_env.Tc
        for env in self.envs:
            if (env.Th != Th) or (env.Tc != Tc):
                raise DeviceSpecError("All the Environments should be the same!")
                
                
    def get_y_list(self, x_name, y_name, x_list, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6):
        """
        Return a list of "y_name" for given "x_name".
            x_name : 'I' or 'R_L'
            y_name : 'QhA' or 'power' or 'efficiency'
            x_list : a list of x values.
            kwargs : additional options for matplotlib.
        """
        y_list = []
        for x_elem in x_list:
            if x_name == 'I':
                self.run_with_given_I(I=x_elem, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=True)
            elif x_name == 'R_L':
                self.run_with_given_R_L(R_L=x_elem, given_no_loop=given_no_loop, max_no_loop=max_no_loop, abs_tol=abs_tol, quiet=True)
            else:
                raise ValueError("'x_name' should be 'I' or 'R_L'")
            if y_name == 'QhA':
                y_list.append(self.QhA)
            elif y_name == 'power':
                y_list.append(self.power)
            elif y_name == 'efficiency':
                y_list.append(self.efficiency)
            else:
                raise ValueError("'y_name' should be 'QhA' or 'power' or 'efficiency'")
        return y_list
    
    def plot_xy(self, x_name, y_name, x_list, title=None, x_label=None, y_label=None, \
             given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, **kwargs):
        """
        Draw a graph of "x_name" vs. "y_name".
        "x_label" and "y_label" are used for labels in the graph.
            x_name : 'I' or 'R_L'
            y_name : 'QhA' or 'power' or 'efficiency'
            x_list : a list of x values.
            kwargs : additional options for matplotlib.
        """
        y_list = self.get_y_list(x_name, y_name, x_list, given_no_loop, max_no_loop, abs_tol)
        import matplotlib.pyplot as plt
        fig = plt.figure()   # draw new figure
        plt.plot(x_list, y_list, **kwargs)
        if x_label is None:
            x_label = x_name
        if y_label is None:
            y_label = y_name
        if title is None:
            title = x_label + ' vs. ' + y_label
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        return fig
        
    @staticmethod
    def from_dict(a_dict):
        """
        'a_dict' is a dictionary containing the following information on a thermoelectric device:
            'type': 'common'; does NOT work right now,
            'length': the height of the device; does NOT work right now,
            'area': the area of the device; does NOT work right now,
            'Th': hot side temperature; imposed when a leg has none,
            'Tc': cold side temperature; imposed when a leg has none,
            'legs': a list of Leg objects,
            'environments': a list of Environment objects; each one corresponds to a Leg obejct above.
            
        Create and return a Device object.
        """
        copy_dict = a_dict.copy()
        legs = copy_dict.pop("legs", [])
        environments = copy_dict.pop("environments", [None]*len(legs))
        return Device(legs, environments, **copy_dict)

    def plot(self, length_unit='[m]', length_multiplier=1, show_legend=False, show_mat_name=True):
        """
        Plot the structure of a thermoelectric device and return the figure handle.
        Assume "TEProp.color" attribute exists.
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        x_sizes = [np.sqrt(leg.A) * length_multiplier for leg in self.legs]
        x_pad = np.min(x_sizes) * 0.05
        x_total = np.sum(x_sizes) + x_pad*(len(x_sizes)-1)
        y_sizes = [leg.L * length_multiplier for leg in self.legs]
        y_total = np.max(y_sizes)
        y_pad = y_total * 0.07
        leg_mults = [mult for mult in self.multipliers]

        fig = plt.figure()
        ax = fig.add_subplot(111, aspect='equal')

        x_pos = 0
        for leg, x_size, y_size, leg_mult in zip(self.legs, x_sizes, y_sizes, leg_mults):
            # show the multiplier
            if leg_mult > 1:
                plt.text(x_pos+x_size, 0, '(x%d)'% leg_mult, ha='right', va='bottom', color='w')            
            # draw a leg
            y_pos = 0
            for mat, length in zip(leg.mats, leg.mat_lengths):
                name = mat.name
                length = length * length_multiplier
                if not hasattr(mat, 'color'):
                    raise AttributeError("Material does NOT have 'color' attribute.")
                color = mat.color
                p = patches.Rectangle( (x_pos, y_pos), x_size, length, facecolor=color, label=name )
                ax.add_patch(p)
                if show_mat_name:
                    plt.text(x_pos+x_size/2, y_pos+length/2, name, ha='center', va='center', color='w')  # plot material name
                y_pos += length
            x_pos += x_size + x_pad
        if show_legend:
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)
        # add Th, Tc and labels
        x_mid   = (0+x_total)/2
        SILVER = (192/255,192/255,192/255)
        p = patches.Rectangle( (0-x_pad, 0-y_pad), x_total+2*x_pad, y_pad, facecolor=SILVER ) # lower plate
        ax.add_patch(p)
        p = patches.Rectangle( (0-x_pad, y_total), x_total+2*x_pad, y_pad, facecolor=SILVER ) # upper plate
        ax.add_patch(p)
        if self.global_env is None:
            plt.text(x_mid, 0, '$T_c$', ha='center', va='top', color='k')
            plt.text(x_mid, y_size, '$T_h$', ha='center', va='bottom', color='k')
        else:
            plt.text(x_mid, 0, '$T_h = %d [K]$' % self.global_env.Th, ha='center', va='top', color='k')
            plt.text(x_mid, y_size, '$T_c = %d [K]$' % self.global_env.Tc, ha='center', va='bottom', color='k')            
        ax.set_xlim(0-x_pad, x_total+x_pad)
        ax.set_ylim(0-y_pad, y_total+y_pad)
        plt.xlabel('area$^{1/2}$ '+length_unit)
        plt.ylabel('length '+length_unit)
        
        return fig

    def report(self):
        """
        Print computed results to console.
        """
        print('_____Device Analysis_____')
        print('       Vgen = %f [V]' % self.Vgen)
        print('          I = %f [A]' % self.I)
        print('      gamma = %f [1]' % self.gamma)
        print('       R_TE = %f [Ohm]' % self.R_TE)
        print('        R_L = %f [Ohm]' % self.R_L)
        print('      R_tot = %f [Ohm]' % self.R_tot)        
        print('       Qh*A = %f [W] vs. Qh*A (formular) = %f [W]' % (self.QhA,self.QhA_formular) )
        print('       Qc*A = %f [W] vs. Qc*A (formular) = %f [W]' % (self.QcA,self.QcA_formular) )
        print('        dQA = %f [W] vs.  dQA (formular) = %f [W]' % (self.dQA,self.dQA_formular) )
        print('      power = %f [W]' % self.power )        
        print(' efficiency = %f [1]' % self.efficiency )

        temporary548 = self.Zgeneral * self.TmPrime
        temporary549 = (self.Th - self.Tc)/self.Th * ( np.sqrt(1+temporary548) - 1 )/(np.sqrt(1+temporary548) + self.Tc/self.Th  )
        temporary550 = self.efficiency / temporary549
        
        print('')
        print('_____Ztb analysis_____')
        print('  Zgeneral   = %f [1/T]' % self.Zgeneral )
        print('  ZgenTm     = %f [1]' % temporary548 )
        print('  tau        = %f [1]' % self.tau )
        print('  beta       = %f [1]' % self.beta )
        print('  eff(Z)     = %f [1]' % temporary549)
        print('  eff/eff(Z) = %f [1]' % temporary550)



if __name__ == '__main__':
    pass