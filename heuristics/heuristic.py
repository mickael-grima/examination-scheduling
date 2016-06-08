#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)


import numpy as np
import random as rd
import collections

from model.instance import force_data_format

from heuristics.AC import AC
from heuristics.SA import simulated_annealing, swap_color_dictionary
from heuristics.schedule_rooms import schedule_rooms


def obj1(x, n, r):
    '''
        Room objective
    '''
    # TODO: Can we just sum over whole x?
    return sum( x[i,k] for i in range(n) for k in range(r) ) 


def heuristic(coloring, data, gamma = 1):
    
    # create time schedule permuting the time solts for each coloring
    time_schedule, value = simulated_annealing(coloring, data['h'])

    # get exams for each color
    color_exams = swap_color_dictionary(coloring)
    
    for color in color_exams:
        x = schedule_rooms(data, color_exams[color], time_schedule[color])
        # TODO Combine x values!
    
    # if infeasible, return large objVal since we are minimizing
    if x is None:
        return None, None, 1e10

    # evaluate combined objectives
    objVal = obj1(x, data['n'], data['r']) - gamma * value

    return x, y, objVal


def optimize(ant_colony, data, epochs=100, gamma = 1, reinitialize=False):
    
    # init best values
    x, y, objVal = None, None, 1e10

    # iterate
    for epoch in range(epochs):
        xs, ys, objVals = dict(), dict(), dict()

        # Generate colourings
        colorings = ant_colony.generate_colorings()

        # evaluate all colorings
        for col, coloring in enumerate(colorings):
            xs[col], ys[col], objVals[col] = heuristic(coloring, data, gamma)

        # search for best coloring
        # TODO: Replace by list() ??
        values = [ objVals[col] for col in range(len(colorings)) ]
        best_index = np.argmax(values)

        # Update pheromone traces
        ant_colony.update_edges_weight(best_index)

        # save best value so far.. MINIMIZATION
        if values[best_index] < objVal:
            x, y, objVal = xs[best_index], ys[best_index], values[best_index]

    return x, y, objVal

