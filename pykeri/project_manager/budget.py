# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 08:18:43 2017

@author: Jaywan Chung
"""

import numpy as np
from scipy.optimize import linprog

class Budget:
    def __init__(self, title):
        self._title = title
        self._items = []
        self._bounds = []
        self._pos_ub = []
        self._pos_eq = []
        self._coeff_ub = []
        self._coeff_eq = []
        self._b_ub = []
        self._b_eq = []
        self._num_items = 0
        self._subitems = []
        self._values = []
        self._result = None
        self.PAYROLL = "인건비"
        self._person_annual_salary = {}
        self._person_participation_months = {}
        self.maxiter = 1000000
        self.tol = 1e-3   # "1천원"

    # _index function queries the position of the name,
    # and ADD the name if there is no such name.        
    def _index(self, name):
        try:
            pos = self._items.index(name)
        except:
            # if there is no name, add the item and return the last pos
            self._add_item(name)
            pos = self._num_items-1
        return pos        
        
    def _add_item(self, name):  # DO NOT use this function explicitly. USE _index.
        self._items.append(name)
        self._num_items += 1
        self._bounds.append( (None,None) )   # no bound initially
        self._subitems.append([])            # no subitem initially
    
    def bound(self, name, lb, ub):
        pos = self._index(name)
        self._bounds[pos] = (lb,ub)
        
    def subitem(self, subitem_name, parent_name, lb, ub):
        self.bound(subitem_name, lb, ub)
        pos = self._index(subitem_name)
        parent_pos = self._index(parent_name)
        self._subitems[parent_pos].append(pos)   # register the subitem
        
    def _item_vec_to_pos_vec(self, item_vec):
        pos_vec = []
        for name in item_vec:
            pos = self._index(name)
            pos_vec.append(pos)
        return pos_vec

    def eq(self, item_vec, coeff_vec, value):
        pos_vec = self._item_vec_to_pos_vec(item_vec)
        self._pos_eq.append(pos_vec)
        self._coeff_eq.append(coeff_vec)
        self._b_eq.append(value)

    def ub(self, item_vec, coeff_vec, ub):
        pos_vec = self._item_vec_to_pos_vec(item_vec)
        self._pos_ub.append(pos_vec)
        self._coeff_ub.append(coeff_vec)
        self._b_ub.append(ub)
        
    def lb(self, item_vec, coeff_vec, lb):
        minus_coeff_vec = list( -np.array(coeff_vec) )
        ub = -lb
        pos_vec = self._item_vec_to_pos_vec(item_vec)
        self._pos_ub.append(pos_vec)
        self._coeff_ub.append(minus_coeff_vec)
        self._b_ub.append( ub )
        
    def payroll_name(self, person_name):
        return self.PAYROLL + ':' + person_name
    
    def payroll_name_to_person_name(self, payroll_name):
        if self.is_payroll_name(payroll_name):
            return payroll_name[len(self.PAYROLL+':'):]
        else:
            return payroll_name
    
    def is_payroll_name(self, payroll_name):
        if payroll_name.startswith(self.PAYROLL+':'):
            return True
        else:
            return False
        
    def person(self, person_name, annual_salary, participation_months, lb_participation_rate, ub_participation_rate):
        lb_expense = annual_salary / 12 * participation_months * lb_participation_rate / 100
        ub_expense = annual_salary / 12 * participation_months * ub_participation_rate / 100
        #print(person_name, lb_expense, ub_expense)
        payroll_name = self.payroll_name(person_name)
        self.subitem(payroll_name, self.PAYROLL, lb_expense, ub_expense)
        # hold the additional information for process
        self._person_annual_salary[payroll_name] = annual_salary
        self._person_participation_months[payroll_name] = participation_months
        
    def _pos_vec_to_A_vec(pos_vec, coeff_vec, num_items):
        A_vec = [0]*num_items
        for pos,coeff in zip(pos_vec, coeff_vec):
            A_vec[pos] = coeff
        return A_vec
    
    def _pos_to_A(list_pos_vec, list_coeff_vec, num_items):
        A = []
        for pos_vec,coeff_vec in zip(list_pos_vec, list_coeff_vec):
            A_vec = Budget._pos_vec_to_A_vec(pos_vec, coeff_vec, num_items)
            A.append(A_vec)
        if len(A) == 0:
            A = None
        return A
    
    def report(self):
        print("항목수:", self._num_items)
        print("예산항목:", self._items)
        print("상하한:", self._bounds)
        print("상한조건:", self._pos_ub, self._coeff_ub, self._b_ub)
        print("값조건:", self._pos_eq, self._coeff_eq, self._b_eq)
        print("subitems:", self._subitems)
    
    def minimize(self, item_vec, coeff_vec):
        # translate position lists
        A_ub = Budget._pos_to_A(self._pos_ub, self._coeff_ub, self._num_items)
        A_eq = Budget._pos_to_A(self._pos_eq, self._coeff_eq, self._num_items)
        b_ub = self._b_ub
        b_eq = self._b_eq
        # additional summation constraints for the subitems: sum of the values of subitems = value of the parent item
        for pos,subitems in enumerate(self._subitems):
            if len(subitems) == 0:
                continue
            subitem_pos_vec = [pos] + subitems
            subitem_coeff_vec = [-1] + [1]*len(subitems)
            #print(subitem_pos_vec, subitem_coeff_vec)
            A_vec = Budget._pos_vec_to_A_vec(subitem_pos_vec, subitem_coeff_vec, self._num_items)
            A_eq.append(A_vec)
            b_eq.append(0)
        # solve the linear programming problem
        pos_vec = self._item_vec_to_pos_vec(item_vec)
        c = Budget._pos_vec_to_A_vec(pos_vec, coeff_vec, self._num_items)
#        print(c, A_ub, b_ub, A_eq, b_eq, self._bounds)
#        print('c=', c)
#        print('A_ub=', A_ub, 'b_ub=', b_ub)
#        print('A_eq=', A_eq, 'b_eq=', b_eq)
#        print('bounds=', self._bounds)
        #result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=self._bounds, options={'maxiter':self.maxiter, 'tol':self.tol, 'bland':True})
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=self._bounds, options={'maxiter':self.maxiter, 'tol':self.tol})
#        print(result.message)
#        print(result.x)
        if result.success == True:
            self._values = np.around(result.x).astype(int)
            #self._values = result.x
        else:
            print("조건을 만족하는 예산 편성이 불가능해 보입니다.")
        self._result = result
    
    def maximize(self, item_vec, coeff_vec):
        minus_coeff_vec = list( -np.array(coeff_vec) )
        self.minimize(item_vec, minus_coeff_vec)
        
    def plan(self):
        print(self._title)
        if self._values is None:
            raise AttributeError("No plan is available. Please run the minimization process.")
        for item, value in zip(self._items, self._values):
            if self.is_payroll_name(item):
                annual_salary = self._person_annual_salary[item]
                participation_months = self._person_participation_months[item]
                participation_rate = 1200 * value / annual_salary / participation_months
                print(item + "= ", value, "( 연봉=", annual_salary, 
                                            "참여기간(개월)=", participation_months,
                                            "참여율(%)=", participation_rate, ")" )
            else:
                print(item + "= ", value)