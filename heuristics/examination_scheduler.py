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
from time import time

from model.instance import force_data_format, build_random_data
import GurobiModel.GurobiLinear_v_8_removed_obj as gurobi
from gurobipy import GurobiError

from heuristics.AC import AC
from heuristics.schedule_times import schedule_times
from heuristics.schedule_rooms import schedule_rooms
from heuristics.tools import to_binary, get_coloring
from heuristics.check_feasibility import build_statespace

from model.constraints_handler import is_feasible
def heuristic(coloring, data, gamma = 1, max_iter = 100):
    '''
        The heuristiv which iteratively solves first the time scheduling problem, and afterwards the room scheduling problems.
        @Param: coloring dictionary which gives the color for each exam i
        @Param: data is the data and setup of the problem
        @Param: gamma is the weighting of room and time objectives
        @Returnvalues:
        room_schedule: binary. 1 if exami i in room k
        color_schedule: dict of ints
        obj_val: combined objective
    '''
    
    # check feasibility
    statespace, color_exams = build_statespace(coloring, data)
    
    # create time schedule permuting the time solts for each coloring
    color_schedule, time_value = schedule_times(coloring, data, max_iter = max_iter, statespace = statespace, color_exams = color_exams)
    
    if color_schedule is None:
        #print "infeas color"
        return None, None, sys.maxint
    
    # create room schedule
    room_schedule, room_value = schedule_rooms(coloring, color_schedule, data)
    
    # if infeasible, return large obj_val since we are minimizing
    if room_schedule is None:
        #print "infeas room"
        return None, None, sys.maxint

    # evaluate combined objectives
    obj_val = room_value - gamma * time_value

    return room_schedule, color_schedule, obj_val


def log_epoch(logger, epoch, **kwargs):
    ''' 
        Save epoch data in logger.
        Logger[key] is a dictionary!
    '''
    for key in kwargs:
        logger[key][epoch] = kwargs[key]
        

def optimize(meta_heuristic, data, epochs=10, gamma = 1, annealing_iterations = 1000, lazy_threshold = 0.2, verbose = False, log_history = False):
    
    # init best values
    x, y, obj_val = None, None, sys.maxint
        
    if log_history:
        logger = collections.defaultdict(collections.defaultdict)
    
    best_value_duration = 0
    
    # iterate
    for epoch in range(epochs):
        
        if verbose:
            print epoch
        
        xs, ys, obj_vals = dict(), dict(), dict()
        color_schedules = dict()

        # Generate colourings
        colorings = meta_heuristic.generate_colorings()

        ## evaluate all colorings
        for ind, coloring in enumerate(colorings):
            
            xs[ind], color_schedules[ind], obj_vals[ind] = heuristic(coloring, data, gamma = gamma, max_iter = annealing_iterations)
            # build binary variable 
            ys[ind] = to_binary(coloring, color_schedules[ind], data['h'])
            
            if xs[ind] is not None:
                print is_feasible(xs[ind], ys[ind], data)
            else:
                print "None infeasible"
                
        # filter infeasibles
        values = filter(lambda x: x[1] < sys.maxint, enumerate(obj_vals.values()))
        
        # check feasibility
        if len(values) == 0:
            #print "infeasible"
            if log_history:
                log_epoch(logger, epoch, obj_val = obj_val, n_feasible = 0.0) 
            continue
        
        # search for best coloring
        best_index, best_value = min( values, key = lambda x: x[1] )

        if log_history:
            worst_index, worst_value = max( values, key = lambda x: x[1] )
            log_epoch(logger, epoch, obj_val = obj_val, best_value=best_value, n_feasible = 1.0 * len(values) / len(colorings))#, mean_value=np.mean(map(lambda x:x[1],values)), worst_value=worst_value, ) 
                      
        # Update meta heuristic
        meta_heuristic.update(obj_vals.values(), best_index = best_index, time_slots = color_schedules)

        best_value_duration += 1
        
        # save best value so far.. MINIMIZATION
        if best_value < obj_val:
            x, y, obj_val = xs[best_index], ys[best_index], best_value    
            best_value_duration = 0
    
        if best_value != sys.maxint and best_value_duration > lazy_threshold * epochs:
            break
        
    if log_history:
        return x, y, obj_val, logger
    else:
        return x, y, obj_val


      
        
if __name__ == '__main__':
    
    print "Nothing implemented here.\nRun 'tests/test_scheduler.py' instead!"