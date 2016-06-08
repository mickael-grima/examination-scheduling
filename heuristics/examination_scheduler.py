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
from heuristics.tools import to_binary


def heuristic(coloring, data, gamma = 1):
    
    # create time schedule permuting the time solts for each coloring
    color_schedule, time_value = schedule_times(coloring, data, beta_0 = 0.01, max_iter = 1e4)
    
    # create room schedule
    room_schedule, room_value = schedule_rooms(coloring, color_schedule, data)
    
    # if infeasible, return large objVal since we are minimizing
    if room_schedule is None or time_schedule is None:
        return None, None, 1e10

    # evaluate combined objectives
    obj_val = room_value - gamma * time_value

    # build binary variable 
    time_schedule = to_binary(coloring, color_schedule, data['h'])
    
    return room_schedule, time_schedule, obj_val


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



if __name__ == '__main__':
    
    n = 25
    r = 6
    p = 30
    prob_conflicts = 0.6
    
    rd.seed(42)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = get_coloring(conflicts)
    n_colors = len(set(exam_colors[k] for k in exam_colors))
    
    print "Nothing happening here yet"
    