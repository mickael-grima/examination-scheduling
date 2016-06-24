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

if __name__ == '__main__':
    
    
    gamma = 1.0
    n_colorings = 2
    epochs = 10
    annealing_iterations = 500
    
    data = examination_data.read_data(threshold = 0)
    
    data['similar_periods'] = tools.get_similar_periods(data)
    
    n, r, p = data['n'], data['r'], data['p']
    print n, r, p
    
    Heuristic = RandomHeuristicAdvanced(data, n_colorings = n_colorings)
    #Heuristic = RandomHeuristic(data, n_colorings = n_colorings)
    #Heuristic = Johnson(data, n_colorings = n_colorings, n_colors = data['p'])
    #Heuristic = RandomHeuristicAdvanced(data, n_colorings = n_colorings)
    #Heuristic = RandomHeuristic(data, n_colorings = n_colorings)
    #Heuristic = Johnson(data, n_colorings = n_colorings, n_colors = data['p'])
    #Heuristic = AC(data, num_ants = n_colorings)
    
    t = time()
    x, y, v, logger = scheduler.optimize(Heuristic, data, epochs = epochs, gamma = gamma, annealing_iterations = annealing_iterations, annealing_beta_0 = 100, verbose = True, log_history = True, debug=False)
    print "Time:", time()-t
    print "VALUE:", v
    #for key in logger:
        #print key
        #print logger[key]