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


class LinearOneVariableProblem(BaseProblem):
    def __init__(self, name='ExaminationProblem'):
        super(LinearOneVariableProblem, self).__init__(name=name)
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
