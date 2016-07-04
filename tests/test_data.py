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
from model.instance import *
from inputData import examination_data


class TestConstraints(unittest.TestCase):
    """ Test for testing if the constraints are respected
        First the variable has to be transformed into the two variables x[i, k] and y[i, l]
    """
    def setUp(self):
        self.constants_p = ['c', 's', 'T', 'Q', 'h', 'conflicts', 'w']
        self.constants = ['c', 's', 'T', 'Q', 'h', 'conflicts', 'locking_times', 'w', 'location', 'similarp',
                          'similare', 'similarr', 'exam_names', 'result_times', 'result_rooms', 'exam_rooms',
                          'room_names', 'campus_ids']
        self.dimensions = ['n', 'p', 'r']

    def testBuildRandomData(self):
        data = build_random_data(n=10, p=10, r=10)
        for cst in self.constants:
            self.assertIsNotNone(data.get(cst), msg='%s is not in data' % cst)
            self.assertTrue(len(data[cst]) > 0, msg='%s is empty' % cst)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim), msg='%s is not in data' % dim)
            self.assertTrue(data[dim] > 0, msg='%s is yero' % dim)

    def testBuildSimpleData(self):
        data = build_simple_data()
        for cst in self.constants:
            self.assertIsNotNone(data.get(cst), msg='%s is not in data' % cst)
            self.assertTrue(len(data[cst]) > 0, msg='%s is empty' % cst)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim), msg='%s is not in data' % dim)
            self.assertTrue(data[dim] > 0)

    def testBuildSmallInput(self):
        data = build_small_input()
        for cst in self.constants:
            self.assertIsNotNone(data.get(cst), msg='%s is not in data' % cst)
            self.assertTrue(len(data[cst]) > 0, msg='%s is empty' % cst)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim), msg='%s is not in data' % dim)
            self.assertTrue(data[dim] > 0, msg='%s is yero' % dim)

    def testRealData16S(self):
        data = examination_data.read_data(semester="16S")
        for cst in self.constants_p:
            self.assertIsNotNone(data.get(cst), msg='%s is not in data' % cst)
            self.assertTrue(len(data[cst]) > 0, msg='%s is empty' % cst)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim), msg='%s is not in data' % dim)
            self.assertTrue(data[dim] > 0, msg='%s is yero' % dim)

    def testRealData(self):
        data = examination_data.read_data()
        n = data['n']
        Q = data['Q']
        conflicts = data['conflicts']

        for i in range(n):
            for j in range(n):
                if Q[i][j] == 1:
                    assert j in conflicts[i]
                    assert i in conflicts[j]
                else:
                    assert j not in conflicts[i]
                    assert i not in conflicts[j]

        #for cst in self.constants:
            #self.assertIsNotNone(data.get(cst), msg='%s is not in data' % cst)
            #self.assertTrue(len(data[cst]) > 0, msg='%s is empty' % cst)
        #for dim in self.dimensions:
            #self.assertIsNotNone(data.get(dim), msg='%s is not in data' % dim)
            #self.assertTrue(data[dim] > 0, msg='%s is yero' % dim)

    def testBuildSmartRandom(self):
        data = build_smart_random(n=10, p=10, r=10)
        for cst in self.constants:
            self.assertIsNotNone(data.get(cst), msg='%s is not in data' % cst)
            self.assertTrue(len(data[cst]) > 0, msg='%s is empty' % cst)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim), msg='%s is not in data' % dim)
            self.assertTrue(data[dim] > 0, msg='%s is yero' % dim)


if __name__ == '__main__':
    unittest.main()
