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
from heuristics import generate_starting_solution
from model.instance import build_small_input
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
        x, y = generate_starting_solution(self.data)
        x, y = transform_variables(x, y)
        test_conflicts(x, y)
        test_enough_seat(x, y)
        test_one_exam_per_period(x, y)
        test_one_exam_period_room(x, y)


if __name__ == '__main__':
    unittest.main()
