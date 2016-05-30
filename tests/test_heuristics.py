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
from heuristics.generate_starting_solution import generate_starting_solution_by_maximal_time_slot_filling
from model.instance import build_small_input, build_random_data
from utils.tools import transform_variables
from model.constraints_handler import (
    test_conflicts,
    test_enough_seat,
    test_one_exam_per_period,
    test_one_exam_period_room
)


class TestConstraints(unittest.TestCase):
    """ Test here the heuristics. Heuristics can be found in folder heuristics
    """
    def setUp(self):
        self.data = build_small_input()

    def testGenerateStartingSolution(self):
        """ This test tests if the heuristics generate_starting_solution return a feasible solution
        """
        x, y = generate_starting_solution_by_maximal_time_slot_filling(self.data)
        n, r, p = self.data['n'], self.data['r'], self.data['p']
        x, y = transform_variables(x, y, n=n, p=p, r=r)
        self.assertTrue(x, msg="dct x doesn't contain any variables")
        self.assertTrue(y, msg="dct y doesn't contain any variables")
        self.assertTrue(test_conflicts(x, y, Q=self.data['Q']),
                        msg="conflict constraint failed")
        self.assertTrue(test_enough_seat(x, y, c=self.data['c'], s=self.data['s']),
                        msg="seat capacity constraint failed")
        self.assertTrue(test_one_exam_per_period(x, y), msg="one exam per period constraint failed")
        self.assertTrue(test_one_exam_period_room(x, y, T=self.data['T']),
                        msg="one exam per period per room constraint failed")


if __name__ == '__main__':
    unittest.main()
