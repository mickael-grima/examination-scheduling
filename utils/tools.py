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
