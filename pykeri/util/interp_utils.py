# created on Jan 15 2020

from functools import partial
import numpy as np
from scipy.integrate import solve_bvp
import scipy.integrate as integrate
from scipy.optimize import minimize
from scipy.interpolate import lagrange
from scipy.interpolate import UnivariateSpline

from pykeri.thermoelectrics.TEProp import TEProp


def find_maximum(max_fun, initial_value):
    I0 = [initial_value]

    def min_fun(I_vec):
        return -max_fun(I_vec)

    # res = minimize(min_fun, I0, method='Nelder-Mead', tol=1e-3)
#    initial_simplex = np.array([[-0.1],[+0.1]])
    initial_simplex = np.array([[0.4],[0.6]])
    res = minimize(min_fun, I0, method='Nelder-Mead', tol=1e-4, \
                   options={'initial_simplex':initial_simplex,\
                            'maxfev':200})

    return -res.fun, res.x[0], res.success


def interpolate_barycentric_cl(x, y, num_cl_nodes, spline_order):
    xl = x[0]
    xr = x[-1]
    cl_nodes = (xl-xr)/2*np.cos(np.pi * np.linspace(0, num_cl_nodes - 1, num_cl_nodes) / (num_cl_nodes - 1)) + (xl+xr)/2

    exact_func = UnivariateSpline(x, y, k=spline_order, s=0)

    cl_interp_func = BarycentricLagrangeChebyshevNodes(cl_nodes, exact_func(cl_nodes))

    return cl_interp_func, exact_func, cl_nodes


def interpolate_barycentric_equi(x, y, num_equi_nodes, spline_order):
    xl = x[0]
    xr = x[-1]
    equi_nodes = np.linspace(xl, xr, num=num_equi_nodes)

    exact_func = UnivariateSpline(x, y, k=spline_order, s=0)

    equi_interp_func = BarycentricLagrangeEquidistantNodes(equi_nodes, exact_func(equi_nodes))

    return equi_interp_func, exact_func, equi_nodes


def interpolate_cl(x, y, num_cl_nodes, spline_order):
    xl = x[0]
    xr = x[-1]
    cl_nodes = (xl-xr)/2*np.cos(np.pi * np.linspace(0, num_cl_nodes - 1, num_cl_nodes) / (num_cl_nodes - 1)) + (xl+xr)/2

    exact_func = UnivariateSpline(x, y, k=spline_order, s=0)

    cl_interp_func = lagrange(cl_nodes, exact_func(cl_nodes))

    return cl_interp_func, exact_func, cl_nodes


def interpolate_equi(x, y, num_equi_nodes, spline_order):
    xl = x[0]
    xr = x[-1]
    equi_nodes = np.linspace(xl, xr, num=num_equi_nodes)

    exact_func = UnivariateSpline(x, y, k=spline_order, s=0)
    equi_interp_func = lagrange(equi_nodes, exact_func(equi_nodes))

    return equi_interp_func, exact_func, equi_nodes


def get_material_list(db_filename, first_id, last_id, interp_opt=None):
    """
    returns a list of TEProp classes.
    :param db_filename: database filename containing the thermoelectric material properties
    :param first_id: smallest id of a TEP.
    :param last_id: largest id of a TEP.
    :return:
    """
    material_list = [None] * (last_id + 1)
    material_id_list = []
    for id_num in range(first_id, last_id + 1):
        try:
            material = TEProp(db_filename=db_filename, id_num=id_num)
        except ValueError:
            pass
        else:
            if interp_opt is not None:
                material.set_interp_opt(interp_opt)
            material_list[id_num] = material
            material_id_list.append(id_num)

    return material_list, material_id_list


class BarycentricLagrangeChebyshevNodes():
    def __init__(self, raw_x, raw_y):
        """
        :param x: it is assumed that x is a Chebyshev nodes.
        :param y: interpolant values
        """
        self.raw_x = raw_x
        self.raw_y = raw_y
        self.num_nodes = len(raw_x)

        self.w = np.power(-1.0, np.arange(self.num_nodes))
        self.w[0] *= 0.5
        self.w[-1] *= 0.5

    def __call__(self, x):
        return self.eval(x)

    def eval(self, x):
        x_array = np.asarray(x, dtype=np.float64).reshape(-1)
        len_x = x_array.size
        numer = np.zeros((len_x,), dtype=np.float64)
        denom = np.zeros((len_x,), dtype=np.float64)
        exact = np.zeros((len_x,), dtype=np.float64)
        idx_to_avoid = np.repeat(False, len_x)

        for raw_x_elem, raw_y_elem, w_elem in zip(self.raw_x, self.raw_y, self.w):
            diff = x_array - raw_x_elem
            is_diff_zero = np.isclose(diff, 0.0)
            exact[is_diff_zero] = raw_y_elem
            idx_to_avoid[is_diff_zero] = True
            diff[is_diff_zero] = 1.0
            numer += w_elem / diff * raw_y_elem
            denom += w_elem / diff

        idx = np.logical_not(idx_to_avoid)
        y = exact
        y[idx] = numer[idx]/denom[idx]

        # if the original value is a scalar, return a scalar
        if np.asarray(x).shape == ():
            return np.float64(y)
        return y

    def derivative(self):
        raw_dydx = np.zeros((self.num_nodes,), dtype=np.float64)
        # for i in range(self.num_nodes):
        #     sum_of_a_ij = 0.0
        #     for j in range(self.num_nodes):
        #         if not(j == i):
        #             a_ij = self.w[j]/self.w[i]/(self.raw_x[i]-self.raw_x[j])
        #             raw_dydx[i] += self.raw_y[j] * a_ij
        #             sum_of_a_ij += a_ij
        #     raw_dydx[i] += self.raw_y[i]*(-sum_of_a_ij)

        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                if not(j == i):
                    raw_dydx[i] += (self.w[j]/self.w[i])*(self.raw_y[j]-self.raw_y[i])\
                                   /(self.raw_x[i]-self.raw_x[j])

        return BarycentricLagrangeChebyshevNodes(self.raw_x, raw_dydx)


class ThermoelctricEquationSolver():
    def __init__(self, L, A):
        self.L = L
        self.A = A

        self.Tc = None
        self.Th = None

        self.thrm_resi_func = None
        self.dthrm_resi_dT_func = None
        self.elec_resi_func = None
        self.Seebeck_func = None
        self.dSeebeck_dT_func = None

        self.efficiency = None
        self.power = None
        self.power_density = None
        self.res = None

    def set_bc(self, Tc, Th):
        self.Tc = Tc
        self.Th = Th

    def set_te_mat_func(self, thrm_resi_func, dthrm_resi_dT_func, elec_resi_func, Seebeck_func, dSeebeck_dT_func):
        self.thrm_resi_func = thrm_resi_func
        self.dthrm_resi_dT_func = dthrm_resi_dT_func
        self.elec_resi_func = elec_resi_func
        self.Seebeck_func = Seebeck_func
        self.dSeebeck_dT_func = dSeebeck_dT_func

    def te_eqn(self, x, y, J):
        # y = [T; (kappa(T)T')]
        T = y[0]
        thrm_resi = self.thrm_resi_func(T)
        dTdx = y[1]*thrm_resi
        rhs = -self.elec_resi_func(T)*(J**2) + self.dSeebeck_dT_func(T)*T*dTdx*J

        return np.vstack((dTdx, rhs))

    def te_bc(self, ya, yb):
        return np.array([ya[0]-self.Th, yb[0]-self.Tc])

    def solve_te_eqn(self, I):
        J = I / self.A
        te_func = partial(self.te_eqn, J=J)

        # initial mesh
        x = np.linspace(0, self.L, 5)
        # initial guess: linear function
        initial_y0 = (self.Tc - self.Th) / self.L * x + self.Th
        initial_y1 = ((self.Tc - self.Th) / self.L + x * 0.0) / self.thrm_resi_func(initial_y0)
        y_guess = np.vstack((initial_y0, initial_y1))

        # solve the bvp
        res = solve_bvp(te_func, self.te_bc, x, y_guess, tol=1e-3, max_nodes=1e5)
        self.res = res

        T_for_V_gen = np.linspace(self.Tc, self.Th, 1000)
        V_gen = integrate.simps(self.Seebeck_func(T_for_V_gen), T_for_V_gen)
        # V_gen = integrate.quad(self.Seebeck_func, self.Tc, self.Th, limit=1000)[0]
        kappa_dTdx_at_0 = res.sol(0)[1]
        x_for_R = np.linspace(0, self.L, 1000)
        R = integrate.simps(self.elec_resi_func(res.sol(x_for_R)[0]), x_for_R) / self.A
        if np.abs(I) > 0:
            self.gamma = V_gen / (I * R) - 1
        else:
            self.gamma = None

        self.power = I*(V_gen-I*R)
        if self.power >= 0:
            self.efficiency = self.power / (-self.A * kappa_dTdx_at_0 + I * self.Seebeck_func(self.Th) * self.Th)
        else:
            self.efficiency = -np.nan  # efficiency is meaningless in a thermoelectric cooler

        self.power_density = self.power / self.A

        return res

    def compute_max_power_density(self):
        I0 = [0.0]

        def min_fun(I_vec):
            I = I_vec[0]
            solver_res = self.solve_te_eqn(I)
            if not solver_res.success:
                #print("Convergence failed in compute_max_power_density() for I={}".format(I))
                #return 100+np.abs(I)
                return np.infty
            return -self.power_density/1e4

        # res = minimize(min_fun, I0, method='Nelder-Mead', tol=1e-3)
        initial_simplex = np.array([[-0.1],[+0.1]])
        res = minimize(min_fun, I0, method='Nelder-Mead', tol=1e-3, \
                       options={'initial_simplex':initial_simplex,\
                                'maxfev':200})

        return res

    def compute_max_efficiency(self):
        I0 = [0.0]

        def min_fun(I_vec):
            I = I_vec[0]
            solver_res = self.solve_te_eqn(I)
            if not solver_res.success:
                #print("Convergence failed in compute_max_efficiency() for I={}".format(I))
                #return 100+np.abs(I)
                return np.infty
            return -self.efficiency*100

        # res = minimize(min_fun, I0, method='Nelder-Mead', tol=1e-3)
        initial_simplex = np.array([[-0.1], [+0.1]])
        res = minimize(min_fun, I0, method='Nelder-Mead', tol=1e-3, \
                       options={'initial_simplex':initial_simplex,\
                                'maxfev':200})

        return res