#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Sudoku(object):
    def __init__(self):
        self.size = 0  # Size of the square that represents the sudoku
        self.groups = []  # Represents the subgroups
        self.grill = []  # The sudoku grill: None is no value on the case

    def build_sudoku(self, size):
        """ Build the grill with None values
        """
        for i in range(size):
            self.grill.append([])
            for j in range(size):
                self.grill[i].append(None)

    def set_groups(self, groups):
        self.groups = groups

    def build_groups(self):
        """ construct groups using the symetry
        """
        if self.size:
            pass

    def set_constraints(self, cases):
        """ @param cases: dictionnary with numbers associated to the tuple cases
        if this number is bigger than the size we don't consider the case
        """
        for case, number in cases.iteritems():
            if number < self.size:
                self.grill[case] = number

    def draw(self):
        """ Draw the grill with groups, and the cases with not None numbers
        """
        pass

    def solve(self):
        """ Find a solution
        """
        pass
