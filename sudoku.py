#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Test

#Test 2

import logging
from utils.tools import get_closest_dividers, check_sudoku_groups


class Sudoku(object):
    """ Class to represent a sudoku game
    Cases are represented by a 2-tuple: first coordinate is from left to right,
    second coordinate is from top to bottom
    the (0,0) is the case at the top-left side
    """
    def __init__(self, size):
        self.size = size  # Size of the square that represents the sudoku
        self.groups = {}  # Represents the subgroups: list of list of tuple. Reqiure exactly size subgroups
        self.grill = []  # The sudoku grill: None is no value on the case
        self.logger = logging  # to save the logs

        # We build the sudoku function of the size
        self.build_sudoku()
        self.build_groups()

    def build_sudoku(self):
        """ Build the grill with None values
        """
        for i in range(self.size):
            self.grill.append([])
            for j in range(self.size):
                self.grill[i].append(None)

    def set_groups(self, groups):
        if not check_sudoku_groups(self.size, groups):
            self.logger.warning("Sudoku: invalid groups to set. Groups must contains every index between 0 and %s"
                                % len(groups))
        else:
            self.groups = groups

    def get_groups(self):
        """ @return: a dictionnary with set of case associated to integer
        integers are the groups, the set the cases associated to this group
        """
        res = {}
        for key, value in self.groups.iteritems():
            res.setdefault(value, set())
            res[value].add(key)
        return res

    def build_groups(self):
        """ construct groups using the symetry
        """
        if self.size:
            # Split first self.size into two dividers
            width, length = get_closest_dividers(self.size)
            # If we found dividers, groups will be rectangle with length and width as parameters
            if width > 1:
                ind = 0
                for i in range(length):
                    for j in range(width):
                        for l in range(length):
                            for k in range(width):
                                self.groups[(i * width + k, j * length + l)] = ind
                        ind += 1
            # Else self.size is a primary number, we treat each case
            else:
                if self.size == 1:
                    self.groups[(0, 0)] = 0
                elif self.size == 2:
                    for i in range(self.size):
                        ind = 0
                        for j in range(self.size):
                            self.groups[(i, j)] = ind
                        ind += 1
                elif self.size == 3:
                    for i in range(self.size):
                        ind = 0
                        for j in range(self.size):
                            self.groups[(i, j)] = ind
                        ind += 1
                elif self.size == 5:
                    self.groups = {
                        (0, 0): 0, (0, 1): 0, (0, 2): 0, (1, 0): 0, (1, 1): 0,
                        (0, 3): 1, (0, 4): 1, (1, 3): 1, (1, 4): 1, (2, 4): 1,
                        (2, 0): 2, (3, 0): 2, (3, 1): 2, (4, 0): 2, (4, 1): 2,
                        (3, 3): 3, (3, 4): 3, (4, 2): 3, (4, 3): 3, (4, 4): 3,
                        (1, 2): 4, (2, 1): 4, (2, 2): 4, (2, 3): 4, (3, 2): 4
                    }
                else:
                    self.logger.warning("No groups implementation for the size %s yet" % self.size)

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
