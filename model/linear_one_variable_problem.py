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
from model.main_problem import MainProblem


class LinearOneVariableProblem(MainProblem):
    def __init__(self, data, name='ExaminationProblem'):
        super(LinearOneVariableProblem, self).__init__(name=name)
        self.c = 0.5  # criteria factor
        self.available_constants = ['s', 'c', 'Q', 'T', 'h']  # every constants names have to be included in this list

        self.build_problem(data)

    def build_variables(self):
        """
            Build the variables of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        self.vars.setdefault('x', {})
        for i in range(n):
            for k in range(r):
                for l in range(p):
                    self.vars['x'][i, k, l] = self.problem.addVar(vtype=gb.GRB.BINARY, name='x[%s,%s,%s]' % (i, k, l))
        return True

    def build_constraints(self):
        """
            Build the variables of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        for i in range(n):
            # Exactly one period and one room per exam
            constraint = (gb.quicksum([self.vars['x'][i, k, l] for k in range(r) for l in range(p)]) == 1)
            self.problem.addConstr(constraint, "c0")
            # Enough seat for one exam
            constraint = (
                gb.quicksum([self.vars['x'][i, k, l] * self.constants['c'][k] for k in range(r) for l in range(p)]) >=
                self.constants['s'][i]
            )
            self.problem.addConstr(constraint, "c1")
            for j in range(i + 1, n):
                for l in range(p):
                    # No conflicts
                    constraint = (
                        gb.quicksum([self.vars['x'][i, k, l] + self.vars['x'][j, k, l] for k in range(r)]) <=
                        2 - self.constants['Q'][i][j]
                    )
                    self.problem.addConstr(constraint, "c2")
        for k in range(r):
            for l in range(p):
                # maximal one exam per room per period
                constraint = (gb.quicksum([self.vars['x'][i, k, l] for i in range(n) for l in range(p)]) <= 1)
                self.problem.addConstr(constraint, "c3")
