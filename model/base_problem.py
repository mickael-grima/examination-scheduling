#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import gurobipy as gb
from utils.tools import get_value


class BaseProblem(object):
    """ The base of every problems
    """

    def __init__(self, name='ExaminationProblem'):
        self.vars = {}
        self.constants = {}
        self.dimensions = {}
        self.problem = gb.Model(name)
        self.ModelName = name

        self.available_constants = []
        self.logger = logging

    def get_variables(self):
        for _, dct in self.vars.iteritems():
            yield {key: get_value(var) for key, var in dct.iteritems()}

    def update_variable(self):
        """ Rewrite variable in order to have only the values
        """
        x = {key: get_value(var) for key, var in self.vars['x'].iteritems()}
        y = {key: get_value(var) for key, var in self.vars['y'].iteritems()}
        return x, y

    def get_constants(self):
        """ @returns: constants of the problem: c,s,Q,T,h
        """
        c = self.constants['c']
        s = self.constants['s']
        Q = self.constants['Q']
        T = self.constants['T']
        h = self.constants['h']
        return c, s, Q, T, h

    def build_dimensions(self, data):
        return True

    def build_constants(self, data):
        return True

    def build_variables(self):
        return True

    def build_constraints(self):
        return True

    def build_objectif(self):
        return True

    def build_problem(self, data):
        """ @param data: contains the constants: 'Q', 's', ...
            the constants are representing as a dictionnary
        """
        # First extract the dimension problems: n, r and p
        if self.build_dimensions(data):
            # ----------- CONSTANTS -------------
            self.build_constants(data)
            # ----------- VARIABLES -------------
            self.build_variables()
            self.problem.update()
            # ----------- CONSTRAINTS -------------
            self.build_constraints()
            # ----------- CRITERIA -------------
            self.build_objectif()
            return True
        return False

    def optimize(self):
        """ Solve the problem
        """
        self.problem.optimize()
        try:
            self.objVal = self.problem.objVal
        except:
            self.objVal = 0

    def __str__(self):
        # Dimensions
        res = 'Dimensions: %s\n' % ', '.join('%s=%s' % (name, value)
                                             for name, value in self.dimensions.iteritems())
        # Variables
        res += 'Variables: '
        first = True
        for name, varss in self.vars.iteritems():
            if not first:
                res += '\n           '
            res += '%s=%s' % (name, str({key: value.Obj for key, value in varss.iteritems()}))
            first = False
        # Constants
        res += '\nConstants: '
        first = True
        for name, consts in self.constants.iteritems():
            if not first:
                res += '\n           '
            res += '%s=%s' % (name, str(consts))
            first = False
        return res
