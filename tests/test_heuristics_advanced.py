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

import random as rd
from model.instance import build_random_data
from heuristics import tools
from heuristics.schedule_times import schedule_times

def SA_test_objectives(n = 30, r = 20, p = 20, prob_conflicts = 0.2, seed = 42):

    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = tools.get_coloring(conflicts)
    n_colors = len(set(exam_colors[k] for k in exam_colors))
    times, value = schedule_times.simulated_annealing(exam_colors, data, max_iter = 100)
    
    # exams per color
    color_exams = tools.swap_color_dictionary(exam_colors)
    
    # for an exam i and a color c count the number of conflicts between them
    exam_color_conflicts = [ set(exam_colors[j] for j in conflicts[i]) for i in exam_colors ]
    # for each color c get all colors d where there exists a conflict
    #color_conflicts = get_color_conflicts(color_exams, conflicts)
    
    print n_colors
    print conflicts
    print exam_colors
    ov2 = schedule_times.obj2(times, exam_colors, conflicts)
    ov3 = schedule_times.obj3(times, exam_colors, exam_color_conflicts)
    #ov4 = schedule_times.obj4(times, exam_colors, color_exams, color_conflicts)
    assert ov2 == ov3, "ERROR: OBJECTIVES 2 and 3 DIFFER! %0.2f VS %0.2f" %(ov2, ov3)
    #assert ov2 == ov4, "ERROR: OBJECTIVES 2 and 4 DIFFER! %0.2f VS %0.2f" %(ov2, ov4)
    print "OBJECTIVE TEST OK"


def SA_benchmark_annealing(n = 25, r = 6, p = 30, prob_conflicts = 0.2, seed = 420):
    
    from time import time
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = tools.get_coloring(conflicts)
    n_colors = len(set(exam_colors[k] for k in exam_colors))
    print n_colors
    
    beta_0 = 1e-3
    log_hist = False
    
    max_iter = 1e1
    print max_iter
    rd.seed(seed)
    t1 = time()
    times, v1 = schedule_times.simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    t1 = (time() - t1)*1.0
    rt1 = t1/max_iter
    
    #print t1
    
    max_iter = 1e2
    print max_iter
    rd.seed(seed)
    t2 = time()
    times, v2 = schedule_times.simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    t2 = (time() - t2)*1.0
    rt2 = t2/max_iter
    
    #print t2
    
    max_iter = 1e2
    print max_iter
    rd.seed(seed)
    t3 = time()
    times, v3 = schedule_times.simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    times, v3 = schedule_times.simulated_annealing(exam_colors, data, color_schedule = times, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    t3 = (time() - t3)*1.0
    rt3 = t3/max_iter/2.
    
    print t1, t2, t3
    print rt1, rt2, rt3
    print v1, v2, v3


if __name__ == '__main__':
    SA_test_objectives()
    SA_benchmark_annealing()
