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
