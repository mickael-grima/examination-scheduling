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
    
from heuristics.tools import get_similar_periods
def test_meta_heuristic(Heuristic, data, epochs = 50, annealing_iterations = 500, do_plot=True):
    
    t = time()
    x, y, v, logger = optimize(Heuristic, data, epochs = epochs, gamma = 0.1, annealing_iterations = annealing_iterations, verbose = False, log_history = True)
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
    
    
def test_optimize_dummy(n = 15, r = 6, p = 15, prob_conflicts = 0.6, epochs = 100, annealing_iterations = 500, seed = 42):
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
    test_meta_heuristic(T, data, epochs = epochs, annealing_iterations = annealing_iterations)
        
    
      
def test_random(n = 45, r = 11, p = 12, prob_conflicts = 0.3, epochs = 100, annealing_iterations = 500, seed = 42):
    
    print "Random Heuristic"
    data = get_data_for_tests(n, r, p, prob_conflicts, seed)
    
    T = RandomHeuristic(data, n_colorings = 30)
    test_meta_heuristic(T, data, epochs = epochs, annealing_iterations = annealing_iterations)
    
    
def test_random_advance(n = 45, r = 11, p = 12, prob_conflicts = 0.3, epochs = 100, annealing_iterations = 500, seed = 42):
    
    print "Advanced Random Heuristic"
    data = get_data_for_tests(n, r, p, prob_conflicts, seed)
    
    T = RandomHeuristicAdvanced(data, n_colorings = 2)
    test_meta_heuristic(T, data, epochs = epochs, annealing_iterations = annealing_iterations)
      
      
def test_SA(n = 45, r = 11, p = 12, prob_conflicts = 0.3, epochs = 100, annealing_iterations = 500, seed = 42):
    
    print "Simulated Annealing Random Heuristic"
    print "Does not work?"
    data = get_data_for_tests(n, r, p, prob_conflicts, seed)
    
    T = SAHeuristic(data, n_colorings = 2)
    test_meta_heuristic(T, data, epochs = epochs, annealing_iterations = annealing_iterations)
      
      
def test_ant_colony(n = 15, r = 5, p = 15, prob_conflicts = 0.6, epochs = 100, annealing_iterations = 500, seed = 42):
    
    print "Ant Colony"
    data = get_data_for_tests(n, r, p, prob_conflicts, seed)
    
    T = AC(data, num_ants = 30)
    test_meta_heuristic(T, data, epochs = epochs, annealing_iterations = annealing_iterations)
    
        
if __name__ == '__main__':
    
    epochs = 20
    annealing_iterations = 500
    
    n = 15
    r = 13
    p = 8
    prob = 0.3
    seed = 9464
    
    n = 30
    r = 10
    p = 100
    prob = 0.2
    
    #n = 150
    #r = 130
    #p = 80
    #prob = 0.3
    #seed = 42
    
    #n = 300
    #r = 260
    #p = 160
    #prob = 0.3
    #seed = 42
    
    
    #test_heuristic(n,r,p,prob,seed)
    #test_optimize_dummy(n,r,p,prob,seed)
    test_random(n,r,p,prob,epochs, annealing_iterations, seed)
    #test_SA(n,r,p,prob,epochs, annealing_iterations, seed)
    #test_random_advance(n,r,p,prob, epochs, annealing_iterations,seed)
    test_ant_colony(n,r,p,prob, epochs, annealing_iterations,seed) 