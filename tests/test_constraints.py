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
import itertools
import model.instance as ins
import utils.tools as tools
from model.linear_problem import LinearProblem
from model.linear_one_variable_problem import LinearOneVariableProblem
from model.cuting_plane_problem import ReducedProblem, CutingPlaneProblem


class TestConstraints(unittest.TestCase):
    """ Test for testing if the constraints are respected
        First the variable has to be transformed into the two variables x[i, k] and y[i, l]
    """
    def setUp(self):
        data = {
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
        self.problems = {
            'OneExamPerPeriod': [
                LinearProblem(data),
                LinearOneVariableProblem(data),
                ReducedProblem(data)
            ],
            'EnoughSeat': [
                LinearProblem(data),
                LinearOneVariableProblem(data),
                ReducedProblem(data)
            ],
            'OneExamPeriodRoom': [
                LinearProblem(data),
                LinearOneVariableProblem(data),
            ],
            'Conflicts': [
                LinearProblem(data),
                LinearOneVariableProblem(data),
                ReducedProblem(data)
            ]
        }

    def testOneExamPerPeriod(self):
        """ Test here the constraint: one exam per period
        """
        for prob in self.problems['OneExamPerPeriod']:
            prob.optimize()
            x, y = tools.update_variable(prob)
            n, _, p = tools.get_dimensions_from(x, y)
            for i in range(n):
                self.assertTrue(sum([y[i, l] for l in range(p)]) == 1,
                                msg="%s doesn't respect constraint for i=%s" % (prob.ModelName, i))

    def testEnoughSeat(self):
        """ Test here the constraint: enough seats for each exam
        """
        for prob in self.problems['EnoughSeat']:
            prob.optimize()
            x, y = tools.update_variable(prob)
            n, r, _ = tools.get_dimensions_from(x, y)
            c, s, _, _, _ = tools.get_constants_from(prob)
            for i in range(n):
                self.assertTrue(sum([x[i, k] * c[k] for k in range(r)]) >= s[i],
                                msg="%s doesn't respect constraint for i=%s" % (prob.ModelName, i))

    def testOneExamPeriodRoom(self):
        """ Test here the constraint: For each room and period we have only one exam
        """
        for prob in self.problems['OneExamPeriodRoom']:
            prob.optimize()
            x, y = tools.update_variable(prob)
            n, r, p = tools.get_dimensions_from(x, y)
            _, _, _, T, _ = tools.get_constants_from(prob)
            for k in range(r):
                for l in range(p):
                    self.assertTrue(sum(x[i, k] * y[i, l] for i in range(n)) <= T[k][l],
                                    msg="%s doesn't respect constraint for k=%s, l=%s" % (prob.ModelName, k, l))

    def testConflicts(self):
        """ Test here the constraint: no student has to write two exams or more at the same time
        """
        for prob in self.problems['Conflicts']:
            prob.optimize()
            x, y = tools.update_variable(prob)
            n, r, p = tools.get_dimensions_from(x, y)
            _, _, Q, _, _ = tools.get_constants_from(prob)
            for l in range(p):
                self.assertTrue(sum([y[i, l] * y[j, l] * Q[i][j] for i, j in itertools.combinations(range(n), 2) if Q[i][j] == 1]) == 0,
                                msg="%s doesn't respect constraint for l=%s" % (prob.ModelName, l))


if __name__ == '__main__':
    unittest.main()
