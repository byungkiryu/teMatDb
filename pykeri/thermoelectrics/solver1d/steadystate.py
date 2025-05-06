# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 11:00:13 2017

@author: Byungki Ryu, Jaywan Chung

updated on Thu Mar 08 2018: added some properties for convenience: R_TE, K_TE, Vgen, beta, tau, alphaBar, T
updated on Wed Mar 07 2018: added "QhA_formular" property; uses tau-beta formulation.
updated on Tue Mar 06 2018: use "Leg" class instead of "Device" class.
updated on Tue Oct 10 2017: compatible with TEProp
updated on Tue Jul 11 2017: bug fixed for tau beta, which is occurred when A!=1. Do not believe data before this day.
updated on Wed Jun  7 2017: developing
"""


import numpy as np
import scipy
import time
from scipy import integrate
from scipy.integrate import cumulative_trapezoid as cumtrapz
from scipy.integrate import trapezoid as trapz

import warnings

# unique identifies for TEProp functions: DO NOT MODIFY
ELEC_COND = "elec_cond"
SEEBECK   = "Seebeck"
THRM_COND = "thrm_cond"

#cumintegrate = lambda y,x: scipy.integrate.cumtrapz(y,x,initial=0)
#integrate = lambda y,x: scipy.integrate.trapz(y,x)
cumintegrate = lambda y,x: cumtrapz(y,x,initial=0)
integrate = lambda y,x: trapz(y,x)

NUMERICAL_EFFICIENCY = 'efficiencyNumerical'
FORMULA_EFFICIENCY = 'effMaxFormula0'
POWER = 'power'
TEMPERATURE = 'temperature'

class SteadyState:    
    #GAMMA_MODE_FIXED_GAMMA = 'fixed gamma'
    GAMMA_MODE_FIXED_RL = 'fixed R_L'
    GAMMA_MODE_EFF_MAX = 'efficiency maximize'
    GAMMA_MODE_POWER_MAX = 'power maximize'
    
    def __init__(self, leg, environment, debugging=False):
        self.leg = leg           # leg has x-grids, material properties.
        self.env = environment      # environment has Th and Tc
        self.history = []
        self.report_dict = {}
        self.debugging = debugging
    
    def TE_props_at_xs(self, Ts):   # Ts is equal to T. To emphasize that T is a vector
        alpha = self.leg.seg.composition( SEEBECK, Ts )
        rho = 1/self.leg.seg.composition( ELEC_COND, Ts )
        kappa = self.leg.seg.composition( THRM_COND, Ts )
        return (alpha, rho, kappa)

    def circuit(self, alpha, rho, kappa, T):
        x = self.leg.xs      # Leg position
        A = self.leg.A       # Leg area
        L = self.leg.L       # Leg length
        deltaT = self.env.Th - self.env.Tc
        gradT = self.leg.seg.gradient(T)
        Vgen = -integrate( alpha * gradT, x )
        R_TE = integrate( rho, x ) * 1/A                # corrected by RBk 170607 10:36 // L/A -> 1/A
        inverseK= integrate( 1/kappa, x ) *1/A       # corrected by RBk 170607 10:36 // L/A -> 1/A
        K_TE= 1/inverseK
        
        alphaBar = Vgen/deltaT
        rhoBar   = R_TE*(A/L)
        kappaBar = K_TE*(L/A)
        Zgeneral = alphaBar**2 / R_TE/K_TE

        self.report_dict['Vgen'] = Vgen
        self.report_dict['R_TE'] = R_TE
        self.report_dict['K_TE'] = K_TE
        self.report_dict['alphaBar'] = alphaBar
        self.report_dict['rhoBar'] = rhoBar
        self.report_dict['kappaBar'] = kappaBar
        self.report_dict['Zgeneral'] = Zgeneral
        
        return (Vgen, R_TE, K_TE, alphaBar, rhoBar, kappaBar, Zgeneral)

    def effective_temperature(self,tau,beta):
        Th = self.env.Th
        Tc = self.env.Tc
        deltaT = Th-Tc
        ThPrime = Th - deltaT * tau
        TcPrime = Tc - deltaT * (tau+beta)
        TmPrime = (ThPrime + TcPrime)/2
        
        self.report_dict['ThPrime'] = ThPrime
        self.report_dict['TcPrime'] = TcPrime
        self.report_dict['TmPrime'] = TmPrime
        return (ThPrime,TcPrime,TmPrime)

    def current(self, Vgen,  R_TE, K_TE, Zgeneral, tau, beta, given_I, given_R_L, given_gamma ):
        I = None
        if given_I is not None:
            I = given_I
        elif given_gamma is not None:
            if given_gamma == SteadyState.GAMMA_MODE_POWER_MAX:
                gamma = 1
            elif given_gamma == SteadyState.GAMMA_MODE_EFF_MAX:
                (ThPrime,TcPrime,TmPrime) = self.effective_temperature(tau,beta)
                ZTmPrime = Zgeneral * TmPrime
                gammaMaxEffFormula = np.sqrt(1+ZTmPrime)                
                gamma = gammaMaxEffFormula
            else:
                gamma = given_gamma   # given_gamma is a value
            R_tot = (1+gamma)*R_TE
            I = Vgen/R_tot
            return I
        elif given_R_L is not None:
            R_L = given_R_L
            R_tot = R_L+R_TE
            I = Vgen/R_tot
        self.report_dict['I'] = I
        return I
    
    def is_convergent(self,T1,T2, abs_tol=1e-6):
        L = self.leg.L
        x = self.leg.xs
        tol = abs_tol
        absTdiff = np.abs(T1 - T2)
        err = integrate( absTdiff, x )/L
        self.report_dict['max_T_diff'] = np.max(absTdiff)
        self.report_dict['err in T, absTdiff_sum'] = err
        return err < tol
    
    def solve_T(self,T_prev,I):
        Th = self.env.Th
        Tc = self.env.Tc
        A = self.leg.A
        L = self.leg.L
        x = self.leg.xs
        deltaT = Th - Tc
        gradT = self.leg.seg.gradient(T_prev)

        ### 1. For given T(x), re-calculate the TEPs and obtain V,R,K
        T = T_prev
        (alpha, rho, kappa) = self.TE_props_at_xs(T)
        (Vgen, R_TE, K_TE, alphaBar,rhoBar,kappaBar, Zgeneral) = self.circuit( alpha, rho, kappa, T )
        zT_at_xs = alpha*alpha/rho/kappa*T
        self.report_dict['peakzT'] = max(zT_at_xs)
        
        self.report_dict['LEGPOSITIONX'] = x
        self.report_dict['SEEBECKFUNCTION']  = alpha
        self.report_dict['ELECCONDFUNCTION'] = 1/rho
        self.report_dict['THRMCONDFUNCTION'] = kappa
        
        

        
        ### 2. Calculate J, tau and beta ###
        J = I/A

        ######### Source Term #########
        f0 = 0*x
        #f1 = -T * dalphadx           ## JC: change to alpha * dT/dx
        f2 = rho
        ######### Indefinite Integral #########
        F0 = cumintegrate( f0, x )
        F1 = ( Th*alpha[0] - T*alpha + cumintegrate( alpha * gradT,x ) )# Here integral of f1 is calcualted by the integral by part method
        F2 = cumintegrate( f2, x )
        ######### Indefinite Integral #########
        FF0 = cumintegrate( F0/kappa, x )
        FF1 = cumintegrate( F1/kappa, x )
        FF2 = cumintegrate( F2/kappa, x )

        delTstar1_over_J  = FF1[-1]/A
        delTstar2_over_JJ = FF2[-1]/A/A

        ########## finally calculate tau and beta 
        tau_alphaBar_deltaT  = (1/(1 * Th)) * ( (alphaBar-alpha[0])*Th + K_TE * delTstar1_over_J ) * (Th/1)   ## is this correct? should alphaBar computed again?
        if (alphaBar == 0.0) or (deltaT == 0.0):
#        if( J == 0):
            tau =0
        else:
            tau = tau_alphaBar_deltaT / alphaBar / deltaT        
            # tau  = (1/(alphaBar * Th)) * ( (alphaBar-alpha[0])*Th + K_TE * delTstar1_over_J ) * (Th/deltaT)   ## is this correct? should alphaBar computed again?
        beta = (2/R_TE)               * ( K_TE * delTstar2_over_JJ )  -1
     
        ########## tau0 and beta0
        if (alpha[0]+alpha[-1] == 0.0):
            tau0 = 0.0
        else:
            tau0  = - (alpha[0]-alpha[-1]) / (alpha[0]+alpha[-1])/3
        beta0 = + (rho[0]*kappa[0] - rho[-1]*kappa[-1]) /(rho[0]*kappa[0] + rho[-1]*kappa[-1])/3
        
        self.report_dict['tau'] = tau
        self.report_dict['beta'] = beta
        
        self.report_dict['tau0'] = tau0
        self.report_dict['beta0'] = beta0
        
        ### 3. Solve next T ###
        FFJ0 = FF0 
        FFJ1 = FF1 * J
        FFJ2 = FF2 * J*J        
        ######### Update T, tau, beta #########
        #T1(x) = T_initial(x)
        T1 = Th - deltaT * cumintegrate(1/kappa,x) * kappaBar/L                # it can be expressed using kappaBar
        T1 = Th - deltaT * cumintegrate(1/kappa,x) / integrate(1/kappa,x)  # it is exact solution. to reduce the misstake I use exact equation here
        T3 = - (FFJ0 + FFJ1 + FFJ2) 
        delTstar = -T3[-1]       # actually I can reuse the delTstar1_over_J and delTstar2_overJJ.
        T4 = ( T1 - Th ) * delTstar / deltaT
        T2 = T3 - T4
 
#        T = T1 + T2       
        ### 20200103 mixing
        
#        ZZZZZZZZZZZZZ = 0.7
#        T_next = T_prev* ZZZZZZZZZZZZZ + (T1+T2)* (1-ZZZZZZZZZZZZZ)
        T_next = T1+T2
        max_increment = (Th-Tc)/20
        T_increment = T_next - T_prev
        T_increment[T_increment > max_increment] = max_increment
        T_increment[T_increment < -max_increment] = -max_increment
        T = T_prev + T_increment
        
        ## cutoff
#        T = T1 + T2
#        T_too_high = T > Th*2
#        T_too_low = T < Tc*0.5
#        T[T_too_high] = Th*2
#        T[T_too_low] = Tc*0.5        
        
        ### 4. Save report ###
        if I == 0:
            gamma = 10000000000
        else:
            gamma = Vgen/I/R_TE - 1
        R_L = gamma * R_TE
        gradT = self.leg.seg.gradient(T)
        Q = alpha * T * J - kappa * gradT
        Qh = Q[0]; Qc = Q[-1]
        power = Qh - Qc
        power2 = I*I*R_L/A
        
        eta = power/Qh
        
        if self.debugging: print('line-197 gamma eta dpower  ',gamma,eta,power-power2)
        self.report_dict['gamma'] = gamma
        self.report_dict[NUMERICAL_EFFICIENCY] = eta
        
#        self.report_dict['SeebeckT'] = alpha
        self.report_dict[TEMPERATURE] = T
        self.report_dict['Vgen'] = Vgen
        self.report_dict['R_TE'] = R_TE
        self.report_dict['K_TE'] = K_TE
        self.report_dict['Zgeneral'] = Zgeneral
        
        self.report_dict['Th'] = Th
        self.report_dict['Tc'] = Tc
        
        
        ThPrime = Th - tau * deltaT
        TcPrime = Tc - (tau + beta) * deltaT
        TmPrime = (ThPrime +TcPrime)/2
        ZTmPrime = Zgeneral * TmPrime
        
        self.report_dict['deltaT']  = deltaT
        self.report_dict['ThPrime']  = ThPrime 
        self.report_dict['TcPrime']  = TcPrime 
        
        self.report_dict['TmPrime'] = TmPrime
        self.report_dict['ZTmPrime'] = ZTmPrime
        if self.debugging: print('line-222 ZTmPrime', Zgeneral * TmPrime)
        self.report_dict['tau'] = tau 
        self.report_dict['beta'] = beta 
                
        self.report_dict['Qh']     = Qh
        self.report_dict['Qc']     = Qc
        self.report_dict[POWER]  = power
        self.report_dict['powerDensity'] = power2
        self.report_dict['errPower']  = power - power2
        
        effMaxFormula = deltaT / ThPrime * (np.sqrt(1+ZTmPrime)-1) / (np.sqrt(1+ZTmPrime) +TcPrime/ThPrime)
        
        ThPrime0  = Th - deltaT * tau0
        TcPrime0  = Tc - deltaT * (tau0+beta0)
        TmPrime0  = (ThPrime0+TcPrime0)/2
        ZTmPrime0 = Zgeneral * TmPrime0
        
        effMaxFormula0 = deltaT / ThPrime0 * (np.sqrt(1+ZTmPrime0)-1) / (np.sqrt(1+ZTmPrime0) +TcPrime0/ThPrime0 )
        
        self.report_dict['effMaxFormula'] = effMaxFormula
        self.report_dict[FORMULA_EFFICIENCY] = effMaxFormula0
        
        return (T, Vgen, R_TE, K_TE, Zgeneral, tau, beta)
    
    def solve(self, given_no_loop=None, max_no_loop = 100, abs_tol=1e-6, given_I=None, given_R_L=None, given_gamma=GAMMA_MODE_POWER_MAX, quiet=False):
        # tic = time.clock()
        tic = time.perf_counter()
        
        # for brevity
        Th = self.env.Th
        Tc = self.env.Tc
        L = self.leg.L
        x = self.leg.xs
        deltaT = Th - Tc

        ######### Value initialization #########
        
        ### Initial Parameter ###
        T_linear = (Tc-Th)/L*x + Th              ## BRyu ok
        kappa = self.leg.seg.composition( THRM_COND, T_linear )   # evaluate kapp(T)(x)
        T_initial = Th - deltaT * cumintegrate(1/kappa,x) / integrate(1/kappa,x)
        
        
        (alpha, rho, kappa) = self.TE_props_at_xs(T_initial)
                 
        (Vgen, R_TE, K_TE, alphaBar,rhoBar,kappaBar, Zgeneral) = self.circuit( alpha, rho, kappa, T_initial )
        
        
        
        
        
        alpha_Tc = alpha[-1]; rho_Tc= rho[-1]; kappa_Tc = kappa[-1]
        alpha_Th = alpha[0];  rho_Th = rho[0]; kappa_Th = kappa[0]
        if (alpha_Tc+alpha_Th == 0.0):
            tau = 0.0
        else:
            tau   = (1/3)*(alpha_Tc-alpha_Th)/(alpha_Tc+alpha_Th)
        beta  = (1/3)*(rho_Th*kappa_Th-rho_Tc*kappa_Tc)/(rho_Th*kappa_Th+rho_Tc*kappa_Tc)
        self.report_dict['Zgeneral']       = Zgeneral
        self.report_dict['tau']        = tau
        self.report_dict['beta']       = beta



        if self.debugging: print("line-332 tau beta= ", tau, beta)

        T_prev = T_initial.copy()

#        print("  line-341")
        I = self.current(Vgen, R_TE, K_TE, Zgeneral, tau, beta, given_I, given_R_L, given_gamma)
        T_initial2 = T_initial + R_TE/2/K_TE * I*I * (x/L)*(1-x/L)
        T_prev = T_initial2.copy()

        convergent = False
        I = None
        if (given_no_loop is not None) and (given_no_loop > max_no_loop):
            max_no_loop = given_no_loop
        for n in range(max_no_loop):
            if self.debugging: print(str(n)+'th loop running... (line-340)')
            self.update_history()
#            print('line-259 R_TE Vgen  ',R_TE,Vgen)
#            print('line-260 I  ',I)

            ##### Current Contol ######
            I = self.current(Vgen, R_TE, K_TE, Zgeneral, tau, beta, given_I, given_R_L, given_gamma)
            
            (T, Vgen, R_TE, K_TE, Zgeneral, tau, beta) = self.solve_T(T_prev,I)
            ThPrime = Th - tau * deltaT
            TcPrime = Tc - (tau + beta) * deltaT
            TmPrime = (ThPrime +TcPrime)/2
            ZTmPrime = Zgeneral * TmPrime
#            test_gamma = np.sqrt(1+ZTmPrime)
#            test_effMax = deltaT/ThPrime * (test_gamma -1)/(test_gamma + TcPrime/ThPrime)
            
            if self.is_convergent(T,T_prev, abs_tol=abs_tol):
                convergent = True
                break
            if n+1 == given_no_loop:
                break            
            T_prev = T.copy()

        self.report_dict['I'] = I
        self.update_history()
        

        if not convergent:
            print("SolverWarning: the temperature did not converge in " + str(max_no_loop) + " iteration loop. // Current is =",I, " // gamma is =", Vgen/I/R_TE -1)
                    
        if quiet is False:
            if not convergent:
                print("SolverWarning: the temperature did not converge in " + str(max_no_loop) + " loops.")
            toc = time.clock()
            print("Solver: did", n+1, "loops in", toc-tic, "seconds.")
        
        return convergent

    def update_history(self):
        self.history.append(self.report_dict.copy())
        
    def history_of(self,key):
        history = []
        for result in self.history:
            history.append(result.get(key))
        return history

    def get(self,key):
        return self.report_dict.get(key)
    
    def efficiency(self):
        return self.report_dict.get(NUMERICAL_EFFICIENCY)
    
    def power(self):
        return self.report_dict.get(POWER)
    
    def temperature(self):
        return self.report_dict.get(TEMPERATURE)
    def legpositionx(self):
        return self.report_dict.get("LEGPOSITIONX")

    def seebeckfunction(self):
        return self.report_dict.get("SEEBECKFUNCTION")
    def eleccondfunction(self):
        return self.report_dict.get("ELECCONDFUNCTION")
    def thrmcondfunction(self):
        return self.report_dict.get("THRMCONDFUNCTION")
    
    def peakzT(self):
        return self.report_dict.get("peakzT")


    
    def essentials(self):
        vars_name = ['Vgen', 'R_TE', 'K_TE', 'alphaBar', 'rhoBar', 'kappaBar', 'Zgeneral', 'tau', 'beta', NUMERICAL_EFFICIENCY, POWER]
        vars_dict = {}
        for name in vars_name:
            vars_dict[name] = self.get(name)
        return vars_dict
    
    @property
    def QhA_formular(self):
        I = self.get('I')
        alphaBar = self.get('alphaBar')
        Th = self.env.Th
        deltaT = self.env.deltaT
        tau = self.get('tau')
        beta = self.get('beta')
        K_TE = self.get('K_TE')
        R_TE = self.get('R_TE')
        
        result = I*alphaBar*(Th-tau*deltaT) + K_TE*deltaT - 0.5*I**2*R_TE*(1+beta)
        return result
    
    @property
    def QhA(self):
        return self.get('Qh') * self.leg.A

    @property
    def QcA_formular(self):
        I = self.get('I')
        alphaBar = self.get('alphaBar')
        Tc = self.env.Tc
        deltaT = self.env.deltaT
        tau = self.get('tau')
        beta = self.get('beta')
        K_TE = self.get('K_TE')
        R_TE = self.get('R_TE')
        
        result = I*alphaBar*(Tc-tau*deltaT) + K_TE*deltaT + 0.5*I**2*R_TE*(1-beta)
        return result
    
    @property
    def QcA(self):
        return self.get('Qc') * self.leg.A
    
    @property
    def R_TE(self):
        return self.get('R_TE')
    
    @property
    def Vgen(self):
        return self.get('Vgen')
    
    @property
    def beta(self):
        return self.get('beta')
    
    @property
    def K_TE(self):
        return self.get('K_TE')
    
    @property
    def alphaBar(self):
        return self.get('alphaBar')
    
    @property
    def tau(self):
        return self.get('tau')
    
    @property
    def T(self):
        return self.get(TEMPERATURE)

if __name__ == '__main__':
    from segment import Segment
    from leg import Leg
    from environment import Environment
    # read materials
    from pykeri.thermoelectrics.TEProp import TEProp
    mat1 = TEProp('tep.db',1)
    mat2 = TEProp('tep.db',2)
    mat4 = TEProp('tep.db',4)
    mat5 = TEProp('tep.db',5)
    mat6 = TEProp('tep.db',6)
    mat9 = TEProp('tep.db',9)
    all_mat = [mat1,mat2,mat4,mat5,mat6,mat9]
    # set interpolation options
    from pykeri.scidata.matprop import MatProp
    interp_opt = {MatProp.OPT_INTERP:MatProp.INTERP_LINEAR,\
              MatProp.OPT_EXTEND_LEFT_TO:0,          # ok to 0 Kelvin
              MatProp.OPT_EXTEND_RIGHT_BY:50}        # ok to +50 Kelvin from the raw data
    for mat in all_mat:
        mat.set_interp_opt(interp_opt)
        
    #segP = Segment([1280/1e6,720/1e6,400/1e6,400/1e6], [TAGSLa, PbTeNa004Ag001, BSTAg02HP, BSTAg005HP], 1/1e6, max_num_of_grid_per_interval=1001)   ## length, material, minimum for grid, maximum for grid
    #segN = Segment([1145/1e6,1255/1e6], [nPBTAg, nPBT], 1/1e6, max_num_of_grid_per_interval=1001)   ## length, material, minimum for grid, maximum for grid
    
    segP = Segment([1500/1e6,500/1e6], [mat4,mat1], 1/1e6)
    
    leg = Leg(segP, A=1/1e6)    # (seg, area)
    
    env = Environment(700,300)
    
    ss = SteadyState(leg, env, debugging=False)
    #convergent = ss.solve(given_gamma=SteadyState.GAMMA_MODE_EFF_MAX,given_no_loop=20, quiet=True)
    convergent = ss.solve(given_gamma=SteadyState.GAMMA_MODE_EFF_MAX, quiet=True)
    #convergent = ss.solve(given_gamma=SteadyState.GAMMA_MODE_FIXED_GAMMA,given_no_loop=10)
    #convergent = ss.solve(given_gamma=SteadyState.GAMMA_MODE_EFF_MAX)
    #print(convergent)
    print()
    print(SteadyState.GAMMA_MODE_EFF_MAX)
#    print( 'Th=', ss.get('Th') )
#    print( 'Tc=', ss.get('Tc') )
#    print( 'ThPrime', ss.get('ThPrime') )
#    print( 'TcPrime', ss.get('TcPrime') )
#    print( 'Zgeneral=', ss.get('Zgeneral') )
#    print( 'Vgen=', ss.get('Vgen') )
#    print( 'R_TE=', ss.get('R_TE') )
#    print( 'K_TE=', ss.get('K_TE') )    
#    print( 'tau=', ss.get('tau') )
#    print( 'beta=', ss.get('beta') )
    print( 'current=', ss.get('I') )
    print( '       [*1]effMaxNumerical=  ', ss.get(NUMERICAL_EFFICIENCY) )   # or 'efficiencyNumerical'
    print( '       effMaxFormula  = ', ss.get('effMaxFormula'))
    print( '       effMaxFormula0 =', ss.get(FORMULA_EFFICIENCY))
    print( '                       peak-zT        =',ss.get("peakzT"))
    
    print()
    print("I=0 mode")
    #convergent = ss.solve(given_I=0,given_no_loop=20, quiet=True)
    convergent = ss.solve(given_I=0, quiet=True)
#    print( 'Th=', ss.get('Th') )
#    print( 'Tc=', ss.get('Tc') )
#    print( 'ThPrime', ss.get('ThPrime') )
#    print( 'TcPrime', ss.get('TcPrime') )
#    print( 'Zgeneral=', ss.get('Zgeneral') )
#    print( 'Vgen=', ss.get('Vgen') )
#    print( 'R_TE=', ss.get('R_TE') )
#    print( 'K_TE=', ss.get('K_TE') )    
#    print( 'tau=', ss.get('tau') )
#    print( 'beta=', ss.get('beta') )
    print( 'current=', ss.get('I') )
    print( '       eff when J=0, numerical=  ', ss.get(NUMERICAL_EFFICIENCY) )
    print( '       effMaxFormula from Z,tau,beta with T(x) with J=0  ', ss.get('effMaxFormula'))
    print( '       [*2]effMaxFormula from Z,tau0,beta0 with T(x) with J=0 & edge TEPs ', ss.get(FORMULA_EFFICIENCY))
    
    
    #print(convergent, ss.history)
    #print( str(ss.history_of('Vgen')) ) # ok for test 1,2
    #print( str(ss.history_of('R_TE')) ) # ok for test 1,2
    #print( str(ss.history_of('K_TE')) ) # ok for test 1,2
    
    #print( str(ss.history_of('Zgeneral')) )  # ok
    #print( str(ss.history_of('Th')) )  # ok
    #print( str(ss.history_of('Tc')) )  # ok
    #print( str(ss.history_of('deltaT')) )  # ok
    #print( str(ss.history_of('tau')) ) 
    #print( str(ss.history_of('beta')) )  

    ############ restart here ############
    #print( str(ss.history_of('TmPrime')) )  # ok
    #print( str(ss.history_of('ZTmPrime')) ) #ok
    #print( str(ss.history_of('gamma')) ) #ok
    #print( str(ss.history_of(NUMERICAL_EFFICIENCY)) ) # maybe ok
    #print( str(ss.history_of('err in T, absTdiff_sum')) ) # fa