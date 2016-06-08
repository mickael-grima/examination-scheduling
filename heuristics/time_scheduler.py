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
from heuristics.schedule_times import schedule_times
from heuristics.schedule_rooms import schedule_rooms


def time_heuristic(coloring, data):
    
    # create time schedule permuting the time solts for each coloring
    time_schedule, time_value = schedule_times(coloring, data, beta_0 = 0.01, max_iter = 1e4)
    
    # if infeasible, return large objVal since we are minimizing
    if time_schedule is None:
        return None, 1e10

    # evaluate combined objectives
    obj_val = - time_value

    return time_schedule, obj_val


def optimize_time(ant_colony, data, epochs=100, gamma = 1, reinitialize=False):
    
    # init best values
    y, objVal = None, 1e10

    # iterate
    for epoch in range(epochs):
        ys, objVals = dict(), dict()

        # Generate colourings
        colorings = ant_colony.generate_colorings()

        # evaluate all colorings
        for col, coloring in enumerate(colorings):
            ys[col], objVals[col] = time_heuristic(coloring, data, gamma)

        # search for best coloring
        # TODO: Replace by list() ??
        values = [ objVals[col] for col in range(len(colorings)) ]
        best_index = np.argmax(values)

        # Update pheromone traces
        ant_colony.update_edges_weight(best_index)

        # save best value so far.. MINIMIZATION
        if values[best_index] < objVal:
            y, objVal = ys[best_index], values[best_index]

    return y, objVal

