#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)

import gurobipy as gb
from model.base_problem import BaseProblem
import itertools


class NonLinearProblem(BaseProblem):
    def __init__(self, name='ExaminationProblem'):
        super(NonLinearProblem, self).__init__(name=name)
        self.c = 0.5  # criteria factor
        self.available_constants = ['s', 'c', 'Q', 'T', 'h']  # every constants names have to be included in this list

    def build_dimensions(self, data):
        """ get the dimension from data
        """
        self.dimensions['n'] = data.get('n', 0)
        self.dimensions['r'] = data.get('r', 0)
        self.dimensions['p'] = data.get('p', 0)
        if not self.dimensions['n'] or not self.dimensions['r'] or not self.dimensions['p']:
            self.logger.warning("%s: at least one variable is missing" % self.__class__.__name__)
            return False
        return True

    def build_constants(self, data):
        for name in self.available_constants:
            self.constants[name] = data.get(name, [])

    def build_variables(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the variables of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        for i in range(n):
            self.vars.setdefault('x', {})
            for k in range(r):
                # exam i in room k
                self.vars['x'][i, k] = self.problem.addVar(vtype=gb.GRB.BINARY, name='x[%s, %s]' % (i, k))
            self.vars.setdefault('y', {})
            for l in range(p):
                # exam i during period l
                self.vars['y'][i, l] = self.problem.addVar(vtype=gb.GRB.BINARY, name='y[%s, %s]' % (i, l))
        self.problem.update()
        return True

    def build_constraints(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the variables of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        for i in range(n):
            # Add constraint: Each exam is planned in exactly one period
            constraint = (gb.quicksum(self.vars['y'][i, l] for l in range(p)) == 1)
            self.problem.addConstr(constraint, "c0")
            # Add constraint: Each exam has enough seats
            constraint = (
                gb.quicksum(self.vars['x'][i, k] * self.constants['c'][k] for k in range(r)) >= self.constants['s'][i]
            )
            self.problem.addConstr(constraint, "c1")
            # Add constraint: Each exam is planned in exactly one period
            constraint = (gb.quicksum(self.vars['y'][i, l] for l in range(p)) == 1)
            self.problem.addConstr(constraint, "c0")
        # Add constraint: Each room has at most one exam per period
        for k in range(r):
            for l in range(p):
                constraint = (
                    gb.quicksum(self.vars['x'][i, k] * self.vars['y'][i, l] for i in range(n)) <=
                    self.constants['T'][k][l]
                )
                self.problem.addQConstr(constraint, "c2")
        # Add constraint: There are no conflicts
        for l in range(p):
            constraint = (gb.quicksum(self.vars['y'][i, l] * self.vars['y'][j, l] * self.constants['Q'][i][j] for i, j in itertools.combinations(range(n),2) ) == 0)
            self.problem.addQConstr(constraint, "c3")
        return True

    def build_objectif(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the constants of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        obj1 = (gb.quicksum(self.vars['x'][i, k] * self.constants['s'][i] for i, k in itertools.product(range(n), range(r))))
        obj21 = (gb.quicksum(self.constants['Q'][i][j] * (gb.quicksum(self.vars['y'][i, l] * self.constants['h'][l] - self.vars['y'][j, l] * self.constants['h'][l] for l in range(p))))
        obj22 = (gb.quicksum(self.vars['y'][i, l] * self.constants['h'][l] - self.vars['y'][j, l] * self.constants['h'][l] for l in range(p))) for i, j in itertools.combinations(range(n), 2))
        obj = obj1 - obj21 * obj22
        self.problem.setObjective(obj, gb.GRB.MINIMIZE)
        self.problem.optimize()
        return True
