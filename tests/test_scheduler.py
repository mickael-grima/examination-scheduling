#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
paths = os.getcwd().split('/')
path = ''
for p in paths:
    path += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(path)

import unittest

import random as rd
from heuristics.generate_starting_solution import generate_starting_solution_by_maximal_time_slot_filling
from heuristics.AC import AC
import heuristics.examination_scheduler as scheduler
from heuristics import tools
from model.instance import build_smart_random, build_small_input, build_random_data
import heuristics.schedule_times as schedule_times
from heuristics.ColorGraph import ColorGraph
from heuristics.MetaHeuristic import *

from utils.tools import transform_variables
from model.constraints_handler import (
    test_conflicts,
    test_enough_seat,
    test_one_exam_per_period,
    test_one_exam_period_room
)

from heuristics.examination_scheduler import *
from heuristics.MetaHeuristic import *
    
def get_data_for_tests(n, r, p, prob_conflicts, seed):
    rd.seed(seed)
    return build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    
def test_heuristic(n = 15, r = 5, p = 15, prob_conflicts = 0.6, seed = 42):
    
    print "Testing heuristics"
    
    data = get_data_for_tests(n, r, p, prob_conflicts, seed)
    
    coloring = get_coloring(data['conflicts'])
    print "VALUE:", heuristic(coloring, data, gamma = 0.01)[2]
    
    
def test_meta_heuristic(Heuristic, data, epochs = 50, annealing_iterations = 500, do_plot=False):
    
    #print "Testing meta heuristic"
    
    t = time()
    x, y, v, logger = optimize(Heuristic, data, epochs = epochs, gamma = 0.1, annealing_iterations = annealing_iterations, verbose = False, log_history = True)
    print "Time:", time()-t
    print "VALUE:", v
    
    # TODO: DEBUG Worst value 
    if do_plot:
        import matplotlib.pyplot as plt
        for key in logger:
            print key
            values = logger[key].values()
            values = filter(lambda x: x < sys.maxint, values)
            #print ", ".join(map(lambda x: "%0.2f" %x, values))
                
            plt.clf()
            plt.plot(values)
            plt.ylabel(key)
            plt.savefig("%s/heuristics/plots/%s.jpg" %(PROJECT_PATH, key))
    
    
def test_optimize_dummy(n = 15, r = 6, p = 15, prob_conflicts = 0.6, seed = 42):
    ''' 
        Test optimize with dummy meta heuristic 
    '''
    class TestHeuristic(MetaHeuristic):
        def __init__(self, data):
            MetaHeuristic.__init__(self, data)
        def generate_colorings(self):
            conflicts = self.data['conflicts']
            return [ get_coloring(conflicts) ]
        def update(self, values, best_index = None, time_slots=None):
            #print "Do nothing. Value is", values[best_index]
            pass
    
    print "Dummy Heuristic"
    data = get_data_for_tests(n, r, p, prob_conflicts, seed)
    
    T = TestHeuristic(data)
    test_meta_heuristic(T, data, epochs = 100, annealing_iterations = 300)
        
    
def test_random_advance(n = 45, r = 11, p = 12, prob_conflicts = 0.3, seed = 42):
    
    print "Advanced Random Heuristic"
    data = get_data_for_tests(n, r, p, prob_conflicts, seed)
    
    T = RandomHeuristicAdvanced(data, n_colorings = 2)
    test_meta_heuristic(T, data, epochs = 100, annealing_iterations = 300)
      
      
def test_random(n = 45, r = 11, p = 12, prob_conflicts = 0.3, seed = 42):
    
    print "Random Heuristic"
    data = get_data_for_tests(n, r, p, prob_conflicts, seed)
    
    T = RandomHeuristic(data, n_colorings = 2)
    test_meta_heuristic(T, data, epochs = 100, annealing_iterations = 300)
    
    
def test_ant_colony(n = 15, r = 5, p = 15, prob_conflicts = 0.6, seed = 42):
    
    print "Ant Colony"
    data = get_data_for_tests(n, r, p, prob_conflicts, seed)
    
    T = AC(data, num_ants = 20)
    test_meta_heuristic(T, data, epochs = 100, annealing_iterations = 500)
    
        
if __name__ == '__main__':
    
    n = 15
    r = 5 
    p = 15
    prob = 0.6
    seed = 42
    
    test_heuristic(n,r,p,prob,seed)
    test_optimize_dummy(n,r,p,prob,seed)
    test_random(n,r,p,prob,seed)
    test_random_advance(n,r,p,prob,seed)
    #test_ant_colony(n,r,p,prob,seed) 