#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gurobipy as gb
from model.main_problem import MainProblem
from utils.tools import convert_to_table


class LinearProblem(MainProblem):
    def __init__(self, data, name='ExaminationProblem'):
        super(LinearProblem, self).__init__(name=name)
        self.c = 0.5  # criteria factor
        self.ModelName = name

        self.build_problem(data)

    def build_variables(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the variables of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        self.vars.setdefault('x', {})
        self.vars.setdefault('y', {})
        self.vars.setdefault('z', {})
        for i in range(n):
            for k in range(r):
                # exam i in room k
                self.vars['x'][i, k] = self.problem.addVar(vtype=gb.GRB.BINARY, name='x[%s, %s]' % (i, k))
            for l in range(p):
                # exam i during period l
                self.vars['y'][i, l] = self.problem.addVar(vtype=gb.GRB.BINARY, name='y[%s, %s]' % (i, l))
            for j in range(n):
                self.vars['z'][i, j] = self.problem.addVar(vtype=gb.GRB.INTEGER, name='z[%s, %s]' % (i, j))
        return True

    def build_constraints(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the variables of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        for i in range(n):
            # Each exam i is scheduled on exactly one period
            constraint = (gb.quicksum([self.vars['y'][i, l] for l in range(p)]) == 1)
            self.problem.addConstr(constraint, "c0")
            # enough seats for each student for exam i
            constraint = (
                gb.quicksum([self.vars['x'][i, k] * self.constants['c'][k] for k in range(r)]) >=
                self.constants['s'][i]
            )
            self.problem.addConstr(constraint, "c1")
            # No conflicts
            for l in range(p):
                constrant = (
                    gb.quicksum([self.vars['y'][j, l] * self.constants['Q'][i][j] for j in range(n) if j != i]) <=
                    (1 - self.vars['y'][i, l]) * n
                )
                self.problem.addConstr(constrant, "c2")
            for k in range(r):
                for l in range(p):
                    if self.constants['T'][k][l] == 0:
                        # We use room k if and only if the room is open
                        constraint = (self.vars['x'][i, k] + self.vars['y'][i, l] <= 1)
                        self.problem.addConstr(constraint, "c3")
            for j in range(i + 1, n):
                for k in range(r):
                    for l in range(p):
                        # One room k can have only exam for a given period l
                        constraint = (
                            self.vars['x'][j, k] + self.vars['y'][j, l] <=
                            3 - self.vars['x'][i, k] - self.vars['y'][i, l]
                        )
                        self.problem.addConstr(constraint, "c4")
                # Criteria constraint for 'z'
                constraint = (
                    self.vars['z'][i, j] >= gb.quicksum([self.vars['y'][i, l] * self.constants['h'][l] for l in range(p)]) -
                    gb.quicksum([self.vars['y'][j, l] * self.constants['h'][l] for l in range(p)])
                )
                self.problem.addConstr(constraint, "c5")
                constraint = (
                    self.vars['z'][i, j] >= gb.quicksum([self.vars['y'][j, l] * self.constants['h'][l] for l in range(p)]) -
                    gb.quicksum([self.vars['y'][i, l] * self.constants['h'][l] for l in range(p)])
                )
                self.problem.addConstr(constraint, "c6")
        return True

    def build_objectif(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the constants of the problem from the data
        """
        n, r = self.dimensions['n'], self.dimensions['r']
        crit = (
            self.c * gb.quicksum([self.vars['x'][i, k] * self.constants['s'][i] for i in range(n) for k in range(r)]) -
            gb.quicksum([self.vars['z'][i, j] for i in range(n) for j in range(i + 1, n)])
        )
        self.problem.setObjective(crit, gb.GRB.MINIMIZE)
        return True

    def __str__(self):
        # Dimensions
        res = 'DIMENSIONS: %s\n' % ', '.join('%s=%s' % (name, value)
                                             for name, value in self.dimensions.iteritems())
        # Variables
        res += 'VARIABLES: \n'
        # ----- x -------
        res += '-------- x --------  lines=rooms, columns=exams\n'
        res += convert_to_table(self.vars['x'], self.dimensions['n'], self.dimensions['r'])
        # ----- y -------
        res += '-------- y --------  lines=periods, columns=exams\n'
        res += convert_to_table(self.vars['y'], self.dimensions['n'], self.dimensions['p'])
        # Constants
        res += '\nConstants: '
        first = True
        for name, consts in self.constants.iteritems():
            if not first:
                res += '\n           '
            res += '%s=%s' % (name, str(consts))
            first = False
        return res
