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
        self.constants = ['c', 's', 'T', 'Q', 'h', 'conflicts']
        self.dimensions = ['n', 'p', 'r']

    def testBuildRandomData(self):
        data = build_random_data(n=10, p=10, r=10)
        for cst in self.constants:
            self.assertIsNotNone(data.get(cst))
            self.assertTrue(len(data[cst]) > 0)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim))
            self.assertTrue(data[dim] > 0)

    def testBuildSimpleData(self):
        data = build_simple_data()
        for cst in self.constants:
            self.assertIsNotNone(data.get(cst))
            self.assertTrue(len(data[cst]) > 0)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim))
            self.assertTrue(data[dim] > 0)

    def testBuildSmallInput(self):
        data = build_small_input()
        for cst in self.constants:
            self.assertIsNotNone(data.get(cst))
            self.assertTrue(len(data[cst]) > 0)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim))
            self.assertTrue(data[dim] > 0)

    def test_real_data(self):
        data = examination_data.read_data()
        for cst in self.constants:
            self.assertIsNotNone(data.get(cst))
            self.assertTrue(len(data[cst]) > 0)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim))
            self.assertTrue(data[dim] > 0)
    
    def test(self):
        data = build_smart_random(n=10, p=10, r=10)
        for cst in self.constants:
            self.assertIsNotNone(data.get(cst))
            self.assertTrue(len(data[cst]) > 0)
        for dim in self.dimensions:
            self.assertIsNotNone(data.get(dim))
            self.assertTrue(data[dim] > 0)


if __name__ == '__main__':
    unittest.main()
