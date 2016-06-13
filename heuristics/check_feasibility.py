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
from heuristics.tools import to_binary, get_coloring, swap_color_dictionary
from heuristics.schedule_rooms import schedule_rooms_in_period, schedule_greedy


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
                if schedule_greedy(color_exams[color], period, data) is not None:
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



