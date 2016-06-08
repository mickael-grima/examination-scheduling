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
    '''
        The heuristiv which iteratively solves first the time scheduling problem, and afterwards the room scheduling problems.
        @Param: coloring dictionary which gives the color for each exam i
        @Param: data is the data and setup of the problem
        @Param: gamma is the weighting of room and time objectives
        @Returnvalues:
        x[i,k]: binary room variable
        y[i,l]: binary time variable
        obj_val: combined objective
    '''
    # create time schedule permuting the time solts for each coloring
    color_schedule, time_value = schedule_times(coloring, data, beta_0 = 0.01, max_iter = 1e4)
    
    if color_schedule is None:
        return None, None, sys.maxint
    
    # create room schedule
    x, room_value = schedule_rooms(coloring, color_schedule, data)
    
    # if infeasible, return large obj_val since we are minimizing
    if room_schedule is None:
        return None, None, sys.maxint

    # build binary variable 
    y = to_binary(coloring, color_schedule, data['h'])
    
    # evaluate combined objectives
    obj_val = room_value - gamma * time_value

    return x, y, obj_val


def optimize(meta_heuristic, data, epochs=100, gamma = 1, reinitialize=False):
    
    # init best values
    x, y, obj_val = None, None, sys.maxint

    # iterate
    for epoch in range(epochs):
        xs, ys, obj_vals = dict(), dict(), dict()

        # Generate colourings
        colorings = meta_heuristic.generate_colorings()

        # evaluate all colorings
        for col, coloring in enumerate(colorings):
            xs[col], ys[col], obj_vals[col] = heuristic(coloring, data, gamma)

        # search for best coloring
        best_index, best_value = max( enumerate(obj_vals.values()), key=lambda x: x[1] )

        # Update pheromone traces
        meta_heuristic.update(values = obj_vals.values(), best_index = best_index)

        # save best value so far.. MINIMIZATION
        if values[best_index] < obj_val:
            x, y, obj_val = xs[best_index], ys[best_index], values[best_index]

    return x, y, obj_val



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
    