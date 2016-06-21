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

from model.instance import force_data_format, build_random_data, build_real_data
import GurobiModel.GurobiLinear_v_8_removed_obj as gurobi
from gurobipy import GurobiError

from heuristics.AC import AC
from heuristics.schedule_times import schedule_times
from heuristics.schedule_rooms import schedule_rooms
from heuristics.tools import to_binary, get_coloring
from heuristics.check_feasibility import build_statespace
from heuristics.examination_scheduler import optimize

from model.constraints_handler import is_feasible


        
if __name__ == '__main__':
    
    print "Random Heuristic"
    data = build_real_data()
    
    exit(0)

    T = RandomHeuristic(data, n_colorings = 10)
    test_meta_heuristic(T, data, epochs = epochs, annealing_iterations = annealing_iterations)
    
    
    t = time()
    x, y, v, logger = optimize(Heuristic, data, epochs = epochs, gamma = 0.5, annealing_iterations = annealing_iterations, verbose = False, log_history = True)
    print "Time:", time()-t
    print "VALUE:", v
    if 'n_feasible' in logger:
        values = logger['n_feasible'].values()
        values = filter(lambda x: x < sys.maxint, values)
        print "mean(feasible):", np.mean(values)
        
    # TODO: DEBUG Worst value 
    if do_plot:
        import matplotlib.pyplot as plt
        for key in logger:
            if key == 'n_feasible':
                continue
            #print key
            values = logger[key].values()
            values = filter(lambda x: x < sys.maxint, values)
            #print np.mean(values)
            #print ", ".join(map(lambda x: "%0.2f" %x, values))
                
            plt.clf()
            plt.plot(values)
            plt.ylabel(key)
            try:
                plt.savefig("%s/heuristics/plots/%s.png" %(PROJECT_PATH, key))
            except:
                plt.savefig("%s\heuristics\plots\%s.png" %( PROJECT_PATH[:-1] , key))
    
    
    