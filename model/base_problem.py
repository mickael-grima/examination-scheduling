#!/usr/bin/env python
# -*- coding: utf-8 -*-

import picos as pic
import logging


class BaseProblem(object):
    """ The base of every problems
    """

    def __init__(self):
        self.vars = {}
        self.constants = {}
        self.dimensions = {}
        self.problem = pic.Problem()

        self.available_constants = []
        self.logger = logging

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
            # ----------- CONSTRAINTS -------------
            self.build_constraints()
            # ----------- CRITERIA -------------
            self.build_objectif()
            return True
        return False

    def solve(self):
        """ Solve the problem
        """
        self.problem.solve()

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
            res += '%s=%s' % (name, str({key: str(value) if value.is_valued() else '0.0'
                                         for key, value in varss.iteritems()}))
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
