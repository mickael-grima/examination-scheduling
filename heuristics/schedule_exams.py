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
import heuristics.tools as tools
import model.constraints_handler as constraints
from heuristics.schedule_rooms import schedule_rooms_in_period, schedule_greedy



def build_statespace_similar_periods(coloring, data):
    
    #print "Similar periods"
    
    h = data['h']
    
    # refactor dicts
    color_exams = tools.swap_color_dictionary(coloring)
    
    # empty statespace -> init
    statespace = { color: [] for color in color_exams }
    
    # get similar periods
    similar_periods = data['similar_periods']
    
    for color in color_exams:
        
        periods = range(data['p'])
        while len(periods) > 0:
            
            period = periods[0]
            greedy_schedule = schedule_greedy(color_exams[color], period, data)
            
            feasible = greedy_schedule is not None
            
            if feasible:
                statespace[color].append(h[period])
                    
            for period2 in similar_periods[period]:
                if period2 not in periods:
                    continue
                if period2 != period and feasible:
                    statespace[color].append(h[period2])
                periods.remove(period2)
            periods.pop(0)
        
        if len(statespace[color]) == 0:
            return None, None

    return statespace, color_exams


def build_statespace(coloring, data):
    '''
        Build statespace by checking feasibility for every color and every possible time slot.
        If the similar_periods field is present in the data, this is spead up by considering duplicate times slots.
    '''
    
    if 'similar_periods' in data:
        return build_statespace_similar_periods(coloring, data)
    
    h = data['h']
    
    # refactor dicts
    color_exams = tools.swap_color_dictionary(coloring)
    
    # empty statespace -> init
    statespace = { color: [] for color in color_exams }
    
    for color in color_exams:
        for period, time in enumerate(h):
            greedy_schedule = schedule_greedy(color_exams[color], period, data)
            if greedy_schedule is not None:
                statespace[color].append(time)
        if len(statespace[color]) == 0:
            return None, None

    return statespace, color_exams



def heuristic(coloring, data, gamma = 1, max_iter = 100, beta_0 = 10, debug=False):
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
    
    
    #print "Building Statespace"
    # check feasibility
    statespace, color_exams = build_statespace(coloring, data)
    #print "OK"
    if statespace is None:
        if debug: print "infeas"
        return None, None, None, sys.maxint
    
    # create time schedule permuting the time solts for each coloring
    #print "ANNEALING"
    color_schedule, time_value = schedule_times(coloring, data, max_iter = max_iter, beta_0 = beta_0, statespace = statespace, color_exams = color_exams)
    #print "OK"
    # build binary variable 
    y_binary = tools.to_binary(coloring, color_schedule, data['h'])
    
    if y_binary is None or not all(constraints.time_feasible(y_binary, data).values()):
        #print constraints.time_feasible(y_binary, data)
        return None, None, None, sys.maxint
    
    # create room schedule
    room_schedule, room_value = schedule_rooms(coloring, color_schedule, data)
    
    # if infeasible, return large obj_val since we are minimizing
    if room_schedule is None or not all(constraints.room_feasible(room_schedule, data).values()):
        #print constraints.room_feasible(room_schedule, data)
        return None, None, None, sys.maxint

    # evaluate combined objectives
    obj_val = room_value - gamma * time_value
        
    return room_schedule, y_binary, color_schedule, obj_val


def optimize(meta_heuristic, data, epochs=10, gamma = 1, annealing_iterations = 1000, annealing_beta_0 = 10, lazy_threshold = 0.2, verbose = False, log_history = False, debug=False):
    
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

        #print "Building Colorings"
        # Generate colourings
        colorings = meta_heuristic.generate_colorings()
        #print "OK"
        
        ## evaluate all colorings
        for ind, coloring in enumerate(colorings):
            
            # evaluate heuristic
            xs[ind], ys[ind], color_schedules[ind], obj_vals[ind] = heuristic(coloring, data, gamma = gamma, max_iter = annealing_iterations, beta_0 = annealing_beta_0)
            
        # filter infeasibles
        values = filter(lambda x: x[1] < sys.maxint, enumerate(obj_vals.values()))
        
        # check feasibility
        if len(values) == 0:
            #print "infeasible"
            if log_history:
                tools.log_epoch(logger, epoch, obj_val = obj_val, n_feasible = 0.0) 
            continue
        #else: print "feasibile"
        
        # search for best coloring
        best_index, best_value = min( values, key = lambda x: x[1] )

        if log_history:
            worst_index, worst_value = max( values, key = lambda x: x[1] )
            tools.log_epoch(logger, epoch, obj_val = obj_val, best_value=best_value, n_feasible = 1.0 * len(values) / len(colorings))#, mean_value=np.mean(map(lambda x:x[1],values)), worst_value=worst_value, ) 
                      
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