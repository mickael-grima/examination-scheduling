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

import random as rd
from heuristics.generate_starting_solution import generate_starting_solution_by_maximal_time_slot_filling
from heuristics.AC import AC
import heuristics.groups_heuristic as group
import heuristics.schedule_exams as scheduler
from heuristics import tools
from model.instance import build_smart_random, build_small_input, build_random_data
import heuristics.schedule_times as schedule_times
from heuristics.ColorGraph import ColorGraph

from heuristics import tools

    
from utils.tools import transform_variables
from model.constraints_handler import (
    test_conflicts,
    test_enough_seat,
    test_one_exam_per_period,
    test_one_exam_period_room,
    is_feasible
)


class TestConstraints(unittest.TestCase):
    """ Test here the heuristics. Heuristics can be found in folder heuristics
    """
    def setUp(self):
        # self.data = build_small_input()
        self.data = build_smart_random(n=15, p=20, r=15, tseed=1)

    def testColouringHeuristic(self):
        graph = ColorGraph()
        graph.build_graph(self.data['n'], self.data['conflicts'])
        graph.color_graph()
        x, y = {}, graph.build_variable()
        self.assertTrue(test_conflicts(y, conflicts=self.data['conflicts']), msg="conflict constraint failed")

    def testGenerateStartingSolution(self):
        """ This test tests if the heuristics generate_starting_solution return a feasible solution
        """
        x, y = generate_starting_solution_by_maximal_time_slot_filling(self.data)
        n, r, p = self.data['n'], self.data['r'], self.data['p']
        x, y = transform_variables(x, y, n=n, p=p, r=r)
        self.assertTrue(x, msg="dct x doesn't contain any variables")
        self.assertTrue(y, msg="dct y doesn't contain any variables")
        self.assertTrue(test_conflicts(y, conflicts=self.data['conflicts']),
                        msg="conflict constraint failed")
        self.assertTrue(test_enough_seat(x, c=self.data['c'], s=self.data['s']),
                        msg="seat capacity constraint failed")
        self.assertTrue(test_one_exam_per_period(y), msg="one exam per period constraint failed")
        self.assertTrue(test_one_exam_period_room(x, y, T=self.data['T']),
                        msg="one exam per period per room constraint failed")

    def testACAlgorithm(self):
        """ We test here the Ant Colony algorithm, without taking room scheduling in consideration
        """
        x = {}
        y, _ = AC(self.data).optimize_time(epochs=10)
        self.assertTrue(y, msg="dct y doesn't contain any variables")
        self.assertTrue(test_conflicts(y, conflicts=self.data['conflicts']),
                        msg="conflict constraint failed")

    def testHeuristic(self):
        """ This test tests if the heuristics generate_starting_solution return a feasible solution
        """
        
        coloring = tools.get_coloring(self.data['conflicts'])
        x, y, color_schedule, obj_val = scheduler.heuristic(coloring, self.data, gamma = 1, max_iter = 100, beta_0 = 10, debug=False)

        self.assertTrue(x, msg="dct x doesn't contain any variables")
        self.assertTrue(y, msg="dct y doesn't contain any variables")
        self.assertTrue(test_conflicts(y, conflicts=self.data['conflicts'], n=self.data['n'], p = self.data['p']),
                        msg="conflict constraint failed")
        self.assertTrue(test_enough_seat(x, c=self.data['c'], s=self.data['s'], n=self.data['n'], p = self.data['r']),
                        msg="seat capacity constraint failed")
        self.assertTrue(test_one_exam_per_period(y, n=self.data['n'], p = self.data['p']), msg="one exam per period constraint failed")
        self.assertTrue(test_one_exam_period_room(x, y, T=self.data['T'], n=self.data['n'], r=self.data['r'], p = self.data['p']),
                        msg="one exam per period per room constraint failed")


    def testACHeuristics(self):
        """ This test tests if the heuristics generate_starting_solution return a feasible solution
        """
        x, y, _ = scheduler.optimize(AC(self.data), self.data)
        n, r, p = self.data['n'], self.data['r'], self.data['p']
        x, y = transform_variables(x, y, n=n, p=p, r=r)
        self.assertTrue(x, msg="dct x doesn't contain any variables")
        self.assertTrue(y, msg="dct y doesn't contain any variables")
        self.assertTrue(test_conflicts(y, conflicts=self.data['conflicts']),
                        msg="conflict constraint failed")
        self.assertTrue(test_enough_seat(x, c=self.data['c'], s=self.data['s']),
                        msg="seat capacity constraint failed")
        self.assertTrue(test_one_exam_per_period(y), msg="one exam per period constraint failed")
        self.assertTrue(test_one_exam_period_room(x, y, T=self.data['T']),
                        msg="one exam per period per room constraint failed")

    def testGreedyHeuristics(self):
        x, y = group.optimize(self.data)
        n, r, p = self.data['n'], self.data['r'], self.data['p']
        x, y = transform_variables(x, y, n=n, p=p, r=r)
        self.assertTrue(x, msg="dct x doesn't contain any variables")
        self.assertTrue(y, msg="dct y doesn't contain any variables")
        self.assertTrue(test_conflicts(y, conflicts=self.data['conflicts']),
                        msg="conflict constraint failed")
        self.assertTrue(test_enough_seat(x, c=self.data['c'], s=self.data['s']),
                        msg="seat capacity constraint failed")
        self.assertTrue(test_one_exam_per_period(y), msg="one exam per period constraint failed")
        self.assertTrue(test_one_exam_period_room(x, y, T=self.data['T']),
                        msg="one exam per period per room constraint failed")


if __name__ == '__main__':
    unittest.main()
