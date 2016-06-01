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
import GurobiModel.GurobiLinear_v_1 as gl1
import GurobiModel.GurobiLinear_v_2_Q as gl2
import GurobiModel.GurobiLinear_v_3 as gl3
import GurobiModel.GurobiLinear_v_4_Cliques as gl4
import GurobiModel.GurobiLinear_v_5_changed_obj as gl5
import GurobiModel.GurobiLinear_v_6_removed_c6 as gl6
import GurobiModel.GurobiLinear_v_7_new_obj as gl7


class TestConstraints(unittest.TestCase):
    """ Test for testing if the constraints are respected
        First the variable has to be transformed into the two variables x[i, k] and y[i, l]
    """
    def setUp(self):
        self.data = ins.build_small_input()
        # Build problems
        lprob = LinearProblem(self.data)
        loprob = LinearOneVariableProblem(self.data)
        rprob = ReducedProblem(self.data)
        cprob = CutingPlaneProblem(self.data)
        glprob1 = gl1.build_model(self.data)
        glprob2 = gl2.build_model(self.data)
        glprob3 = gl3.build_model(self.data)
        glprob4 = gl4.build_model(self.data)
        glprob5 = gl5.build_model(self.data)
        glprob6 = gl6.build_model(self.data)
        glprob7 = gl7.build_model(self.data)
        # Solve problems
        lprob.optimize()
        loprob.optimize()
        rprob.optimize()
        cprob.optimize()
        glprob1.optimize()
        glprob2.optimize()
        glprob3.optimize()
        glprob4.optimize()
        glprob5.optimize()
        glprob6.optimize()
        glprob7.optimize()
        self.problems = {
            'OneExamPerPeriod': [lprob, loprob, rprob, cprob, glprob1, glprob2, glprob3, glprob4, glprob5, glprob6,
                                 glprob7],
            'EnoughSeat': [lprob, loprob, rprob, cprob, glprob1, glprob2, glprob3, glprob4, glprob5, glprob6, glprob7],
            'OneExamPeriodRoom': [lprob, loprob, cprob, glprob1, glprob2, glprob3, glprob4, glprob5, glprob6, glprob7],
            'Conflicts': [lprob, loprob, rprob, cprob, glprob1, glprob2, glprob3, glprob4, glprob5, glprob6, glprob7]
        }

    def testIntegrality(self):
        """ Test if the variables are integer
        """
        probs = set(self.problems['OneExamPerPeriod'])
        probs.union(set(self.problems['EnoughSeat']))
        probs.union(set(self.problems['OneExamPerPeriod']))
        probs.union(set(self.problems['Conflicts']))
        for prob in probs:
            n, r, p = self.data['n'], self.data['r'], self.data['p']
            x, y = tools.update_variable(prob, n=n, r=r, p=p)
            for i in range(n):
                for k in range(r):
                    self.assertTrue(x[i, k].is_integer())
                for l in range(p):
                    self.assertTrue(y[i, l].is_integer())

    def testOneExamPerPeriod(self):
        """ Test here the constraint: one exam per period
        """
        for prob in self.problems['OneExamPerPeriod']:
            n, r, p = self.data['n'], self.data['r'], self.data['p']
            x, y = tools.update_variable(prob, n=n, r=r, p=p)
            for i in range(n):
                self.assertTrue(sum([y[i, l] for l in range(p)]) == 1,
                                msg="%s doesn't respect constraint for i=%s" % (prob.ModelName, i))

    def testEnoughSeat(self):
        """ Test here the constraint: enough seats for each exam
        """
        for prob in self.problems['EnoughSeat']:
            c, s = self.data['c'], self.data['s']
            n, r, p = self.data['n'], self.data['r'], self.data['p']
            x, y = tools.update_variable(prob, n=n, r=r, p=p)
            for i in range(n):
                self.assertTrue(sum([x[i, k] * c[k] for k in range(r)]) >= s[i],
                                msg="%s doesn't respect constraint for i=%s" % (prob.ModelName, i))

    def testOneExamPeriodRoom(self):
        """ Test here the constraint: For each room and period we have only one exam
        """
        for prob in self.problems['OneExamPeriodRoom']:
            n, r, p = self.data['n'], self.data['r'], self.data['p']
            x, y = tools.update_variable(prob, n=n, r=r, p=p)
            T = self.data['T']
            for k in range(r):
                for l in range(p):
                    self.assertTrue(sum(x[i, k] * y[i, l] for i in range(n)) <= T[k][l],
                                    msg="%s doesn't respect constraint for k=%s, l=%s" % (prob.ModelName, k, l))

    def testConflicts(self):
        """ Test here the constraint: no student has to write two exams or more at the same time
        """
        for prob in self.problems['Conflicts']:
            n, r, p = self.data['n'], self.data['r'], self.data['p']
            x, y = tools.update_variable(prob, n=n, r=r, p=p)
            Q = self.data['Q']
            for l in range(p):
                self.assertTrue(sum([y[i, l] * y[j, l] for i in range(n) for j in range(n) if Q[i][j] == 1 and i != j]) == 0,
                                msg="%s doesn't respect constraint for l=%s" % (prob.ModelName, l))


if __name__ == '__main__':
    unittest.main()
