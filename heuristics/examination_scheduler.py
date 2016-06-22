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

from heuristics import schedule_exams


def heuristic(coloring, data, gamma = 1, max_iter = 100, beta_0 = 10, debug=False):
    print "The examination_schduler is deprecated.. Use schedule_exams instead!"
    return schedule_exams.heuristic(coloring, data, gamma=gamma, max_iter=max_iter, beta_0=beta_0, debug=debug)


def optimize(meta_heuristic, data, epochs=10, gamma = 1, annealing_iterations = 1000, annealing_beta_0 = 10, lazy_threshold = 0.2, verbose = False, log_history = False):
    
    print "The examination_schduler is deprecated.. Use schedule_exams instead!"
    return schedule_exams.optimize(meta_heuristic, data, epochs=epochs, gamma=gamma, annealing_iterations=annealing_iterations, annealing_beta_0=annealing_beta_0, lazy_threshold=lazy_threshold, verbose=verbose, log_history=log_history)
        
if __name__ == '__main__':
    
    print "The examination_schduler is deprecated.. Use schedule_exams instead!"
    