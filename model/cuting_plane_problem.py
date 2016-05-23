#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script contains a cuting plane approach: We take the LinearProblem and supress the third constraint
# At each step we add a part from this third constraint.
# If the third constraint isn't violated we have the optimal solution

from model.main_problem import MainProblem
import gurobipy as gb
from utils.tools import convert_to_table


class ReducedProblem(MainProblem):
    """ Master problem: without the third constraint
    """
    def __init__(self, data, name='ReducedProblem'):
        super(ReducedProblem, self).__init__(name=name)
        self.c = 0.5
        self.ModelName = name

        self.build_problem(data)

    def build_variables(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the variables of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        self.vars.setdefault('x', {})
        self.vars.setdefault('y', {})
        for i in range(n):
            for k in range(r):
                # exam i in room k
                self.vars['x'][i, k] = self.problem.addVar(vtype=gb.GRB.BINARY, name='x[%s, %s]' % (i, k))
            for l in range(p):
                # exam i during period l
                self.vars['y'][i, l] = self.problem.addVar(vtype=gb.GRB.BINARY, name='y[%s, %s]' % (i, l))
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
        return True

    def build_objectif(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the constants of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        crit1 = (
            self.c * gb.quicksum([self.vars['x'][i, k] * self.constants['s'][i] for i in range(n) for k in range(r)])
        )
        crit2 = (
            gb.quicksum([self.constants['Q'][i][j] * gb.quicksum([self.constants['h'][l] * (self.vars['y'][i, l] - self.vars['y'][j, l]) * (self.vars['y'][i, l] - self.vars['y'][j, l]) for l in range(p)])
                         for i in range(n) for j in range(i + 1, n)])
        )
        self.problem.setObjective(crit1 - crit2, gb.GRB.MINIMIZE)
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


class CutingPlaneProblem(object):
    """ We generate the cuting plane algorithm
    """
    def __init__(self, data):
        self.c = 0.5
        self.reducedProblem = ReducedProblem(data)
        # TODO constraint to add at each step
        self.constraint = lambda x, y, i, j, k, l: x[j, k] + y[j, l] <= 3 - x[i, k] - y[i, l]

    def add_constraint(self):
        """ Add the constraint to have only one exam pro room pro period
        """
        pass

    def has_violated_constraint(self):
        """ Check if the constraint is violated
        """
        pass

    def find_variable_violated_constraint(self):
        """ Find the variable which violate the self.constraint
        """
        pass

    def solve(self):
        """ we run here the algorithm
        """
        self.optimize()
        while self.has_violated_constraint():
            var = self.find_variable_violated_constraint()
            self.add_constraint(var)
            self.optimize()
