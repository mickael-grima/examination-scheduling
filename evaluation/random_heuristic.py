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

from time import time
from collections import defaultdict

from inputData import examination_data
from heuristics.MetaHeuristic import RandomHeuristic, RandomHeuristicAdvanced
import heuristics.schedule_exams as scheduler
from heuristics.johnson import Johnson
from heuristics.AC import AC
import heuristics.tools as tools

from evaluation.objectives import obj_time, obj_room

from evaluation.moses import get_moses_representation

if __name__ == '__main__':
    
    gamma = 1.0
    n_colorings = 4
    epochs = 10
    annealing_iterations = 2000
    
    data = examination_data.read_data(semester = "15W", threshold = 0)
    data['similar_periods'] = tools.get_similar_periods(data)
    
    n, r, p = data['n'], data['r'], data['p']
    print n, r, p
    
    Heuristic = RandomHeuristicAdvanced(data, n_colorings = n_colorings)
   # Heuristic = AC(data, num_ants = n_colorings)
    
    t = time()
    x, y, v, logger = scheduler.optimize(Heuristic, data, epochs = epochs, gamma = gamma, annealing_iterations = annealing_iterations, annealing_beta_0 = 100, verbose = True, log_history = True, debug=False)
    print "Time:", time()-t
    
    print "ROOM_OBJ:", obj_room(x)
    print "TIME_OBJ:", obj_time(y, data, h_max = max(data['h']))
    print "VALUE:", v
    
    print "Moses result:"
    x, y, v = get_moses_representation(data, gamma=gamma, verbose=True)
    print "ROOM_OBJ:", obj_room(x)
    print "TIME_OBJ:", obj_time(y, data, h_max = max(data['h']))
    print "VALUE:", v
    
    
    
    #for key in logger:
        #print key
        #print logger[key]