#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
paths = os.getcwd().split('/')
path = ''
for p in paths:
    path += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(path)

import unittest
from model import linear_problem as lpb
from model import colouring_problem as cpb
from model import linear_one_variable_problem as lopb
from model import non_linear_problem as nlpb


class TestSolvers(unittest.TestCase):
    """ for testing the solvers
    """

    def setUp(self):
        self.small_input = {
            'n': 5,  # 5 exams
            'r': 3,  # 3 rooms
            'p': 3,  # 3 periods
            's': [5, 3, 4, 2, 1],  # number of students per exams
            'c': [5, 4, 1],  # number os seats per rooms
            'Q': [[0, 0, 0, 1, 1],
                  [0, 0, 0, 1, 0],
                  [0, 0, 0, 1, 1],
                  [1, 1, 1, 0, 1],
                  [1, 0, 1, 1, 0]],  # Conflicts matrix
            'T': [[1, 0, 1],
                  [1, 1, 0],
                  [1, 1, 0]],  # Opening times for rooms
            'h': [0, 2, 4]  # number of hours before period
        }
        self.lprob = lpb.LinearProblem(self.small_input)
        self.cprob = cpb.ColouringGraphProblem()
        self.loprob = lopb.LinearOneVariableProblem(self.small_input)
        self.nlprob = nlpb.NonLinearProblem(self.small_input)

    def testLinearProblem(self):
        """ We test the builder, if we have enough variables, constants for linear problem
        """
        # Tests
        # n, p and r
        self.assertEqual(self.lprob.dimensions['n'], self.small_input['n'])
        self.assertEqual(self.lprob.dimensions['r'], self.small_input['r'])
        self.assertEqual(self.lprob.dimensions['p'], self.small_input['p'])
        # Constants
        self.assertEqual(len(self.lprob.constants['s']), self.small_input['n'])
        self.assertEqual(len(self.lprob.constants['Q']), self.small_input['n'])
        for i in range(self.small_input['n']):
            self.assertEqual(len(self.lprob.constants['Q'][i]), self.small_input['n'])
        self.assertEqual(len(self.lprob.constants['c']), self.small_input['r'])
        self.assertEqual(len(self.lprob.constants['h']), self.small_input['p'])
        self.assertEqual(len(self.lprob.constants['T']), self.small_input['r'])
        for i in range(self.small_input['r']):
            self.assertEqual(len(self.lprob.constants['T'][i]), self.small_input['p'])
        # Variables
        self.assertEqual(len(self.lprob.vars['x']), self.small_input['n'] * self.small_input['r'])
        self.assertEqual(len(self.lprob.vars['y']), self.small_input['n'] * self.small_input['p'])
        self.assertEqual(len(self.lprob.vars['z']), self.small_input['n'] ** 2)

    def testLinearOneVariableProblem(self):
        """ We test the builder, if we have enough variables, constants for linear problem with one variable
        """
        # Tests
        # n, p and r
        self.assertEqual(self.loprob.dimensions['n'], self.small_input['n'])
        self.assertEqual(self.loprob.dimensions['r'], self.small_input['r'])
        self.assertEqual(self.loprob.dimensions['p'], self.small_input['p'])
        # Constants
        self.assertEqual(len(self.loprob.constants['s']), self.small_input['n'])
        self.assertEqual(len(self.loprob.constants['Q']), self.small_input['n'])
        for i in range(self.small_input['n']):
            self.assertEqual(len(self.loprob.constants['Q'][i]), self.small_input['n'])
        self.assertEqual(len(self.loprob.constants['c']), self.small_input['r'])
        self.assertEqual(len(self.loprob.constants['h']), self.small_input['p'])
        self.assertEqual(len(self.loprob.constants['T']), self.small_input['r'])
        for i in range(self.small_input['r']):
            self.assertEqual(len(self.loprob.constants['T'][i]), self.small_input['p'])
        # Variables
        self.assertEqual(len(self.loprob.vars['x']), self.small_input['n'] * self.small_input['r'] * self.small_input['p'])

    def testNonLinearProblem(self):
        """ We test the builder, if we have enough variables, constants for non linear problem
        """
        # Tests
        # n, p and r
        self.assertEqual(self.nlprob.dimensions['n'], self.small_input['n'])
        self.assertEqual(self.nlprob.dimensions['r'], self.small_input['r'])
        self.assertEqual(self.nlprob.dimensions['p'], self.small_input['p'])
        # Constants
        self.assertEqual(len(self.nlprob.constants['s']), self.small_input['n'])
        self.assertEqual(len(self.nlprob.constants['Q']), self.small_input['n'])
        for i in range(self.small_input['n']):
            self.assertEqual(len(self.nlprob.constants['Q'][i]), self.small_input['n'])
        self.assertEqual(len(self.nlprob.constants['c']), self.small_input['r'])
        self.assertEqual(len(self.nlprob.constants['h']), self.small_input['p'])
        self.assertEqual(len(self.nlprob.constants['T']), self.small_input['r'])
        for i in range(self.small_input['r']):
            self.assertEqual(len(self.nlprob.constants['T'][i]), self.small_input['p'])
        # Variables
        self.assertEqual(len(self.nlprob.vars['x']), self.small_input['n'] * self.small_input['r'])
        self.assertEqual(len(self.nlprob.vars['y']), self.small_input['n'] * self.small_input['p'])

    def testColouringProblem(self):
        """ We test here the colouring ILP problem
        """
        self.cprob.build_problem(self.small_input)
        self.assertEqual(len(self.cprob.colorGraph.graph.nodes()), self.cprob.dimensions['n'])


if __name__ == "__main__":
    unittest.main()
