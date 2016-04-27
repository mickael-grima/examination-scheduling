#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math


def get_closest_dividers(number):
    """ Find two dividers of number, and take two whose euclidian norm is minimal
    """
    width, length = 1, number
    crit = length - width
    for i in range(2, int(math.sqrt(number) + 1)):
        if i * (number / i) == number and math.fabs((i - (number / i))) <= crit:
            length = max(i, number / i)
            width = min(i, number / i)
            crit = length - width
    return width, length


def check_sudoku_groups(size, groups):
    """ @param size: a positive int
        @param groups: a dictionnary of integer associated to 2-tuple: 2-tuple represent sudoku cases, integer groups
        @return: boolean
        Check if value of grops are exactly the integer between 0 and size - 1
        check if for each value, the number of cases belonging to this group is exactly size
    """
    res = True
    reversed_groups = {}
    for key, value in groups.iteritems():
        reversed_groups.setdefault(value, set())
        reversed_groups[value].add(key)
    res = (set(reversed_groups.iterkeys()) == set(range(size)))
    res = (set([len(reversed_groups[key]) for key in reversed_groups.iterkeys()]) == set([size]))
    return res
