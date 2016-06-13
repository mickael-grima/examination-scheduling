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
from gurobipy import Model, quicksum, GRB, GurobiError

from heuristics.AC import AC
from heuristics.schedule_times import schedule_times
from heuristics.schedule_rooms import schedule_rooms
from heuristics.tools import to_binary, get_coloring, swap_color_dictionary
from heuristics.schedule_rooms import schedule_rooms_in_period, schedule_greedy

# def compare_periods(data):

#     p = data['p']
#     r = data['r']
#     c = data['c']
#     T = data['T']


#     c_sum = {}
#     r_sum = {}
#     for l in range(p):
#         c_sum[l] = sum(c[k] for k in range(r) if T[k][l] == 1)
#         r_sum[l] = sum(1 for k in range(r) if T[k][l] == 1)

#     return c_sum, r_sum


def build_statespace(coloring, data):
    '''
        Build statespace by checking feasibility for every color and every possible time slot.
        If the similar_periods field is present in the data, this is spead up by considering duplicate times slots.
    '''
    h = data['h']
    
    # refactor dicts
    color_exams = swap_color_dictionary(coloring)
    
    # empty statespace -> init
    statespace = { color: [] for color in color_exams }
    
    if 'similar_periods' not in data:
        for color in color_exams:
            for period, time in enumerate(h):
                feasible = schedule_greedy(color_exams[color], period, data) is not None
                if feasible:
                    statespace[color].append(time)
            if len(statespace[color]) == 0:
                return None, None
    else:
        similar_periods = data['similar_periods']
        
        for color in color_exams:
            
            periods = range(data['p'])
            while len(periods) > 0:
                period = periods[0]
                feasible = schedule_greedy(color_exams[color], period, data) is not None
                if feasible:
                    statespace[color].append(h[period])
                        
                for period2 in similar_periods[period]:
                    if period2 != period and feasible:
                        statespace[color].append(h[period2])
                    periods.remove(period2)
            
            if len(statespace[color]) == 0:
                return None, None
    
    return statespace, color_exams


def check_feasability_ILP(exams_to_schedule, period, data, verbose = False):
    
    #More precise but by far to slow compared to heuristic

    n = len(exams_to_schedule)
    r = data['r']
    c = data['c']
    T = data['T']
    s = data['s']
    z = {}

    model = Model("RoomFeasability")

    # z[i,k] = if exam i is written in room k
    for k in range(r):
        #print k, period
        if T[k][period] == 1:
            for i in exams_to_schedule:
                z[i,k] = model.addVar(vtype=GRB.BINARY, name="z_%s_%s" % (i,k))

    model.update()

    # Building constraints...    
    
    # c1: seats for all students
    for i in exams_to_schedule:
        model.addConstr( quicksum([ z[i, k] * c[k] for k in range(r) if T[k][period] == 1 ]) >= s[i], "c1")
    
    # c2: only one exam per room
    for k in range(r):
            if T[k][period] == 1:
                model.addConstr( quicksum([ z[i, k] for i in exams_to_schedule  ]) <= 1, "c2")    


    model.setObjective(0, GRB.MINIMIZE)
    
    if not verbose:
        model.params.OutputFlag = 0
    model.params.heuristics = 0
    model.params.PrePasses = 1
    model.optimize()

    
    # return best room schedule
    try:         
        return model.objval
    except GurobiError:
        return None
