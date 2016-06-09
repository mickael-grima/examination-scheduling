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
import GurobiModel.GurobiLinear_v_8_removed_obj as gurobi
from gurobipy import GurobiError

from heuristics.AC import AC
from heuristics.schedule_times import schedule_times
from heuristics.schedule_rooms import schedule_rooms
from heuristics.tools import to_binary, get_coloring


def heuristic(coloring, data, gamma = 1, max_iter = 100):
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
    color_schedule, time_value = schedule_times(coloring, data, max_iter = max_iter)
    
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


def log_epoch(logger, epoch, **kwargs):
    ''' 
        Save epoch data in logger.
        Logger[key] is a dictionary!
    '''
    for key in kwargs:
        logger[key][epoch] = kwargs[key]
        

def optimize(meta_heuristic, data, epochs=100, gamma = 1, annealing_iterations = 10, verbose = False, log_history = False):
    
    # init best values
    x, y, obj_val = None, None, sys.maxint
        
    if log_history:
        logger = collections.defaultdict(collections.defaultdict)
    
    # iterate
    for epoch in range(epochs):
        
        if verbose:
            print epoch
        
        xs, ys, obj_vals = dict(), dict(), dict()

        # Generate colourings
        colorings = meta_heuristic.generate_colorings(ILP_test = True)

        # evaluate all colorings
        for col, coloring in enumerate(colorings):
            xs[col], ys[col], obj_vals[col] = heuristic(coloring, data, gamma = gamma, max_iter = annealing_iterations)

        # filter infeasibles
        values = filter(lambda x: x[1] < sys.maxint, enumerate(obj_vals.values()))
        
        # check feasibility
        if len(values) == 0:
            if log_history:
                log_epoch(logger, epoch, obj_val = obj_val, n_feasible = 0.0) 
            continue
        
        #if verbose:
            #print values
        
        # search for best coloring
        best_index, best_value = min( values, key = lambda x: x[1] )

        if log_history:
            log_epoch(logger, epoch, obj_val = obj_val, best_value=best_value, mean_value=np.mean(values), worst_value=max(values), n_feasible = 1.0 * len(values) / len(colorings)) 
                      
        # Update pheromone traces
        meta_heuristic.update(obj_vals.values(), best_index)

        # save best value so far.. MINIMIZATION
        if best_value < obj_val:
            x, y, obj_val = xs[best_index], ys[best_index], best_value
    
    if log_history:
        return x, y, obj_val, logger
    else:
        return x, y, obj_val


def test_optimize_dummy(n = 15, r = 6, p = 15, prob_conflicts = 0.6, seed = 42):
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
    
    
def test_optimize(n = 15, r = 10, p = 15, prob_conflicts = 0.2, seed = 42):
    ''' 
        Test optimize with dummy meta heuristic 
    '''
    print "Testing ant colony meta heuristic optimization"
    
    rd.seed(seed)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    T = AC(data, num_ants = 100)
    x, y, v = optimize(T, data, epochs=10, gamma = 0.1, annealing_iterations = 1, verbose = True)
    print "VALUE:", v
    
    # Create and solve GUROBI model
    try:        
        model = gurobi.build_model(data, n_cliques = 30, verbose = False)      
        model.optimize()
        print('OPTIMUM: %g' % model.objVal)
    except GurobiError:
        print('Error reported')
    
    
def test_heuristic(n = 15, r = 5, p = 15, prob_conflicts = 0.6, seed = 42):
    
    print "Testing heuristics"
    
    rd.seed(seed)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    coloring = get_coloring(data['conflicts'])
    print "VALUE:", heuristic(coloring, data, gamma = 0.01)[2]
    
    
def test_logging(n = 15, r = 5, p = 15, prob_conflicts = 0.6, seed = 420):
    
    print "Testing logging"
    
    rd.seed(seed)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    T = AC(data, num_ants = 50)
    x, y, v, logger = optimize(T, data, epochs=50, gamma = 0.1, annealing_iterations = 1, verbose = True, log_history = True)
    
    import matplotlib.pyplot as plt
    # TODO: DEBUG Worst value 
    for key in logger:
        values = logger[key].values()
        if key == "obj_val":
            values.pop(0)
            print values
            
        plt.clf()
        plt.plot(values)
        plt.ylabel(key)
        plt.savefig("plots/%s.jpg" %key)
        
if __name__ == '__main__':
    
    #test_heuristic()
    #test_optimize_dummy()
    #test_optimize()
    test_logging()
    