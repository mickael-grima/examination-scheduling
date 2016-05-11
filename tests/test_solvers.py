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
from solvers import problem as pb


class TestSolvers(unittest.TestCase):
    """ for testing the solvers
    """

    def setUp(self):
        self.small_input = {
            'n': 5,  # 5 exams
            'r': 3,  # 3 rooms
            'p': 3,  # 3 periods
            's': [3, 2, 4, 2, 1],  # number of students per exams
            'c': [5, 5, 5],  # number os seats per rooms
            'Q': [[0, 1, 0, 0, 0],
                  [1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]],  # Conflicts matrix
            'T': [[1, 1, 1], [1, 1, 1], [1, 1, 0]],  # Opening times for rooms
            'h': [0, 2, 4]  # number of hours before period
        }
        """
        self.small_input = {
            'n': 2,  # 5 exams
            'r': 1,  # 3 rooms
            'p': 2,  # 3 periods
            's': [3, 4],  # number of students per exams
            'c': [5],  # number os seats per rooms
            'Q': [[0, 1], [1, 0]],  # Conflicts matrix
            'T': [[1]],  # Opening times for rooms
            'h': [0, 2]  # number of hours before period
        }
        """
        self.prob = pb.Problem()

    def testProblemBuild(self):
        """ We test the builder, if we have enough variables, constants
        """
        self.prob.build_problem(self.small_input)

        # Tests
        # n, p and r
        self.assertEqual(self.prob.constants['n'], self.small_input['n'])
        self.assertEqual(self.prob.constants['r'], self.small_input['r'])
        self.assertEqual(self.prob.constants['p'], self.small_input['p'])
        # Constants
        self.assertEqual(len(self.prob.constants['s']), self.small_input['n'])
        self.assertEqual(len(self.prob.constants['Q']), self.small_input['n'] ** 2)
        self.assertEqual(len(self.prob.constants['c']), self.small_input['r'])
        self.assertEqual(len(self.prob.constants['h']), self.small_input['p'])
        self.assertEqual(len(self.prob.constants['T']), self.small_input['r'] * self.small_input['p'])
        # Variables
        self.assertEqual(len(self.prob.vars['x']), self.small_input['n'] * self.small_input['r'])
        self.assertEqual(len(self.prob.vars['y']), self.small_input['n'] * self.small_input['p'])
        self.assertEqual(len(self.prob.vars['z']), self.small_input['n'] * (self.small_input['n'] - 1) / 2)

    def testSolveProb(self):
        """ We test the solver on small_input
        """
        self.prob.build_problem(self.small_input)
        self.prob.solve()


if __name__ == "__main__":
    unittest.main()
