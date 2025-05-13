# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 11:14:30 2017

@author: Jaywan Chung
"""

from scipy.integrate import quad
from scipy.optimize import newton
import numpy as np
from fractions import Fraction

def Fermi_integral(n, eta, tol=1e-10):
    func = lambda x: (x**n)*np.exp(-x) / (np.exp(-x) + np.exp(-eta))
    return quad(func, 0, np.inf, epsabs=tol, epsrel=tol)


def Lo_parabolic_band_approx(S, r=-Fraction(1,2), tol=1e-10):
    """
    Lorenz number [W ohm/K^2] applying the parabolic band approximation.
    S has unit [V/K]. The default 'r' is for phonon-dominated case (r=-1/2).
    For ionized impurity dominated scattering, use 'r=3/2'.
    """
    k_B = 1.3806488e-23      # Boltzmann constant [J/K]
    q_e = 1.6021766208e-19   # elementary charge [C]
    k_B_over_q_e = k_B / q_e
    
    F = lambda r1,r2,eta: Fermi_integral(r1,eta, tol=tol)[0]/Fermi_integral(r2,eta, tol=tol)[0]
    
    r5h = r + Fraction(5,2)
    r3h = r + Fraction(3,2)
    r1h = r + Fraction(1,2)
    func = lambda eta: abs(S)/k_B_over_q_e - (r5h/r3h*F(r3h,r1h,eta)-eta)
    # find the root of the func
    eta = newton(func, 0, tol=tol, maxiter=1000)

    r7h = r + Fraction(7,2)
    L = (k_B_over_q_e)**2 * ( r7h/r3h*F(r5h,r1h,eta) - (r5h/r3h*F(r3h,r1h,eta))**2 )

    return L


if __name__ == '__main__':
    print('Lorenz number for S=1e-06 [V/K] is', Lo_parabolic_band_approx(1e-6), '[W ohm/K^2].')
    print('Lorenz number for S=-1e-06 [V/K] is', Lo_parabolic_band_approx(-1e-6), '[W ohm/K^2].')