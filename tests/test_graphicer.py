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

from model.instance import build_smart_random
from heuristics.generate_starting_solution import generate_starting_solution_by_maximal_time_slot_filling
from utils.tools import transform_variables
from visualization.graphicer import generate_file


class TestGraphicer():
    """ Test everything about the graphicer
    """
    def setUp(self):
        self.data = build_smart_random(n=30, p=30, r=30)

    def testGenerateExcelFile(self):
        """ We generate here the excel file from the problem we solved
        """
        x, y = generate_starting_solution_by_maximal_time_slot_filling(self.data)
        x, y = transform_variables(x, y, n=self.data['n'], r=self.data['r'], p=self.data['p'])
        generate_file(x, y, self.data, name='visual-test')

    def main(self):
        self.setUp()
        self.testGenerateExcelFile()


if __name__ == '__main__':
    test = TestGraphicer()
    test.main()
