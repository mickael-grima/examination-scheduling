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
import random as rd
from collections import defaultdict

from inputData import examination_data
from heuristics.MetaHeuristic import RandomHeuristic, RandomHeuristicAdvanced, AnotherRandomHeuristic
import heuristics.schedule_exams as scheduler
from heuristics.johnson import Johnson
from heuristics.AC import AC
import heuristics.tools as tools

from evaluation.objectives import obj_time, obj_room, obj

from evaluation.moses import get_moses_representation
from heuristics.johnson import Johnson
import pickle

import evaluation.tools as eval_tools

if __name__ == '__main__':
    
    gamma = 1.0
    epochs = 20
    n_colorings = 8
    annealing_iterations = 4000
    annealing_beta_0 = 10
    
    dataset = 2
    
    try:
        data = pickle.load(file=open("%sinputData/data_%s.pickle" %(PROJECT_PATH, dataset), "r"))
    except:
        data = examination_data.load_data(dataset = dataset, threshold = 0, verbose = True)
        pickle.dump(data, file=open("%sinputData/data_%s.pickle" %(PROJECT_PATH, dataset), "w+"))
    
    n, r, p = data['n'], data['r'], data['p']
    print n, r, p
    
    if dataset == 2:
        Heuristic = AnotherRandomHeuristic(data, n_colorings = n_colorings)
    else:
        #Heuristic = RandomHeuristicAdvanced(data, n_colorings = n_colorings)
        #Heuristic = Johnson(data, n_colorings = n_colorings, n_colors = data['p']); epochs = 1
        Heuristic = AC(data, num_ants = n_colorings)
        
    
    # run options
    debug = True
    verbose = False
    parallel =  True
    #rd.seed(42)
    
    
    t = time()
    x, y, v, logger = scheduler.optimize(Heuristic, data, epochs = epochs, gamma = gamma, annealing_iterations = annealing_iterations, annealing_beta_0 = annealing_beta_0, verbose = verbose, log_history = True, debug=debug, parallel=parallel)
    print "\nTime:", time()-t
    if y is None:
        print "INFEASIBLE!!"
        exit(0)
    times = { i: data['h'][l] for (i,l) in y if y[i,l] == 1 }
    
    print "ROOM_OBJ:", obj_room(x)
    print "TIME_OBJ:", obj_time(times, data)
    print "VALUE:", obj(x, y, data, gamma=gamma)
    
    eval_tools.write_result(x, y, data, prob_name = "AnotherRandom")
    
    print "\nMoses result:"
    x, y, v = get_moses_representation(data, gamma=gamma, verbose=False)
    times = { i: data['h'][l] for (i,l) in y if y[i,l] == 1 }
    print "ROOM_OBJ:", obj_room(x)
    print "TIME_OBJ:", obj_time(times, data)
    print "VALUE:", obj(x, y, data, gamma=gamma)
    