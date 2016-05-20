#!/usr/bin/env python
# -*- coding: utf-8 -*-

# In this file we can find every functions concerning the visualization
# The principal function make a visualisation for two variable: x[i, k] and y[i, l]
# i=exam, k=room, l=period
# If we have an other variable, we transform it to both variables above

from utils.tools import convert_to_table, get_dimensions_from


def print_variables(x, y):
    """ x, y have to be 2-dimensional variables
    """
    res = 'VARIABLES: \n'
    # ----- x -------
    res += '-------- x --------  lines=rooms, columns=exams\n'
    dims = get_dimensions_from(x)
    res += convert_to_table(x, dims[0], dims[1])
    # ----- y -------
    res += '-------- y --------  lines=periods, columns=exams\n'
    dims = get_dimensions_from(y)
    res += convert_to_table(y, dims[0], dims[1])
    return res
