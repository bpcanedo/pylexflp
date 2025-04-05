#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 01:31:22 2025

@author: Boris Pérez-Cañedo
"""

from pulp import (LpProblem, LpVariable, LpBinary, LpAffineExpression, 
                  LpConstraint, getSolver)

from pulp import LpMaximize as flpMaximize
from pulp import LpMinimize as flpMinimize

from scipy.optimize import direct, Bounds


class FLP(LpProblem):
    def __init__(self, criteria=[lambda x: x.am, lambda x: x.au, lambda x: x.al], 
                 L=1e+3, e=1e-4, name="NonName", sense=flpMaximize):
        LpProblem.__init__(self, name, sense)
        self.L = L
        self.e = e
        self.criteria = criteria
        self.objs = []
        self._binary = []
    def __iadd__(self, other):
        if type(other) is TFN_Var:
            LpProblem.__iadd__(self, other.al <= other.am)
            LpProblem.__iadd__(self, other.am <= other.au)
            self.objs = [criterion(other) for criterion in self.criteria]
        elif type(other) is FuzzyLinearExp:
            self.objs = [criterion(other) for criterion in self.criteria]
        elif type(other) is LpAffineExpression:
            self.objs += [other]
        elif type(other) is LpConstraint:
            LpProblem.__iadd__(self, other)                        
        elif type(other) is tuple:
            LpProblem.__iadd__(self, other[0])
        elif type(other) is FuzzyEqConstraint:
            LpProblem.__iadd__(self, other.rhs.al == other.lhs.al)
            LpProblem.__iadd__(self, other.rhs.am == other.lhs.am)
            LpProblem.__iadd__(self, other.rhs.au == other.lhs.au)
        else:
            n_criteria = len(self.criteria)
            bin_var_index = int(len(self._binary)/n_criteria)+1
            bin_vars = [LpVariable(f"bin{bin_var_index}{k}", cat=LpBinary) 
                        for k in range(1, n_criteria+1)]
            self._binary += bin_vars
            for k in range(n_criteria):
                s = 0
                if k>0:
                    for i in range(k):
                        s += bin_vars[i]
                    s = -self.L*s
                LpProblem.__iadd__(self, s+self.e*bin_vars[k] <= self.criteria[k](other.rhs)-self.criteria[k](other.lhs))
                LpProblem.__iadd__(self, self.criteria[k](other.rhs)-self.criteria[k](other.lhs) <= self.L*bin_vars[k])
        return self
    def solve(self, solver=None):
        return LpProblem.sequentialSolve(self, self.objs, solver=solver)
    def sequentialSolve(self):
        raise NotImplementedError
    def __str__(self):
        return LpProblem.__str__(self)
    
class TFN:
    def __init__(self, al, am, au):
        self.al = al
        self.am = am
        self.au = au
    def __call__(self, x):
        def safe_div(a, b):
            if abs(b) <= 1e-6:
                return 1.0
            else:
                return a/b
        return max(0, min(safe_div(x-self.al, self.am-self.al), safe_div(self.au-x, self.au-self.am)))
    
    def IS(self, predicate):
        # To Evaluate the degree of truth
        obj = lambda x: -min(self(x), predicate(x))
        if self.al < self.au:
            bounds = Bounds(self.al, self.au)
            res = direct(obj, bounds, maxfun=10000, locally_biased=False)
            return -res.fun
        return predicate(self.am)
    def __add__(self, other):
        if type(other) is TFN:
            return TFN(self.al+other.al, self.am+other.am, self.au+other.au)
        else:
            return FuzzyLinearExp(self.al+other.al, self.am+other.am, self.au+other.au)
    def __sub__(self, other):
        if type(other) is TFN:
            return TFN(self.al-other.au, self.am-other.am, self.au-other.al)
        else:
            return FuzzyLinearExp(self.al-other.au, self.am-other.am, self.au-other.al)
    def __mul__(self, other):
        if type(other) is TFN:
            return TFN(self.al*other.al, self.am*other.am, self.au*other.au)
        else:
            return FuzzyLinearExp(self.al*other.al, self.am*other.am, self.au*other.au)
    def abs(self, other):
        return sum(abs(self.al-other.al)+abs(self.am-other.am)+abs(self.au-other.au))
    def __str__(self):
        return f"TFN({self.al}, {self.am}, {self.au})"
    def __repr__(self):
        return f"TFN({self.al}, {self.am}, {self.au})"
    def nonzero_vars(self):
        return [var for var in ["al", "am", "au"] 
                if abs(getattr(self, var))>=10**-6]
            

class TFN_Var:
    def __init__(self, name, unrestricted=False):
        self.name = name
        self.unrestricted = unrestricted
        if not self.unrestricted:
            self.al = LpVariable(f"{self.name}l", 0)
            self.au = LpVariable(f"{self.name}u", 0)
            self.am = LpVariable(f"{self.name}m", 0)
        else:
            self.al = LpVariable(f"{self.name}l")
            self.au = LpVariable(f"{self.name}u")
            self.am = LpVariable(f"{self.name}m")
    def value(self):
        return TFN(self.al.value(), self.am.value(), self.au.value())
    def nonzero_vars(self):
        return [var for var in [self.al, self.am, self.au] if abs(var.value())<=10**-6]
    def __eq__(self, other):
        return FuzzyEqConstraint(self, other)
    def __le__(self, other):
        return FuzzyLeConstraint(self, other)
    def __ge__(self, other):
        return FuzzyLeConstraint(other, self)
    def __add__(self, other):
        return FuzzyLinearExp(self.al+other.al, self.am+other.am, self.au+other.au)
    def __sub__(self, other):
        return FuzzyLinearExp(self.al-other.au, self.am-other.am, self.au-other.al)
    def __str__(self):
        return f"TFN({self.al.value()}, {self.am.value()}, {self.au.value()})"
    def __repr__(self):
        return f"TFN({self.al.value()}, {self.am.value()}, {self.au.value()})"
    def IS(self, predicate):
        return self.value().IS(predicate)

class FuzzyEqConstraint:
    def __init__(self, lhs, rhs):
        self.rhs = rhs
        self.lhs = lhs
    
class FuzzyLeConstraint:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

class FuzzyLinearExp:
    def __init__(self, al, am, au):
        self.al = al
        self.am = am
        self.au = au
    def value(self):
        return TFN(self.al.value(), self.am.value(), self.au.value())
    def __mul__(self, other):
        return FuzzyLinearExp(self.al*other.al, self.am*other.am, 
                              self.au*other.au)
    def __add__(self, other):
        return FuzzyLinearExp(self.al+other.al, self.am+other.am, 
                              self.au+other.au)
    def __eq__(self, other):
        return FuzzyEqConstraint(self, other)
    def __le__(self, other):
        return FuzzyLeConstraint(self, other)
    def __ge__(self, other):
        return FuzzyLeConstraint(other, self)
    def __str__(self):
        return f"TFN({self.al.value()}, {self.am.value()}, {self.au.value()})"
    def __repr__(self):
        return f"TFN({self.al.value()}, {self.am.value()}, {self.au.value()})"
