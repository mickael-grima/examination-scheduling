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

from model.instance import force_data_format, build_random_data

from heuristics.AC import AC
from heuristics.schedule_times import schedule_times
from heuristics.schedule_rooms import schedule_rooms
from heuristics.tools import to_binary, get_coloring


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
    if x is None:
        return None, None, sys.maxint

    # build binary variable 
    y = to_binary(coloring, color_schedule, data['h'])
    
    # evaluate combined objectives
    obj_val = room_value - gamma * time_value

    return x, y, obj_val


def optimize(meta_heuristic, data, epochs=100, gamma = 1):
    
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

        # Update meta heuristic
        meta_heuristic.update(obj_vals.values(), best_index = best_index)

        # save best value so far.. MINIMIZATION
        if best_value < obj_val:
            x, y, obj_val = xs[best_index], ys[best_index], best_value

    return x, y, obj_val


def test_optimize(n = 15, r = 6, p = 15, prob_conflicts = 0.6, seed = 42):
    ''' 
        Test optimize with dummy meta heuristic 
    '''
    print "Testing dummy meta heuristic optimization"
    
    class TestHeuristic:
        def __init__(self, data):
            self.data = data
        def generate_colorings(self):
            conflicts = self.data['conflicts']
            return [ get_coloring(conflicts) ]
        def update(self, values, best_index = None):
            #print "Do nothing. Value is", values[best_index]
            pass
    
    rd.seed(seed)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    T = TestHeuristic(data)
    x, y, v = optimize(T, data, epochs=10, gamma = 0.01)
    print "VALUE:", v
    
    
def test_heuristic(n = 15, r = 6, p = 15, prob_conflicts = 0.6, seed = 42):
    
    print "Testing heuristics"
    
    rd.seed(seed)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    coloring = get_coloring(data['conflicts'])
    print "VALUE:", heuristic(coloring, data, gamma = 0.01)[2]
    
    
if __name__ == '__main__':
    
    test_heuristic()
    test_optimize()
    