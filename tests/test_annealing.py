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
import heuristics.schedule_times as schedule_times

def SA_test_objectives(n = 30, r = 20, p = 20, prob_conflicts = 0.2, seed = 42):

    rd.seed(seed)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = tools.get_coloring(conflicts)
    n_colors = len(set(exam_colors[k] for k in exam_colors))
    color_schedule, value = schedule_times.simulated_annealing(exam_colors, data, max_iter = 100)
    
    # exams per color
    color_exams = tools.swap_color_dictionary(exam_colors)
    
    # for an exam i and a color c set if there is a conflicts between them
    exam_color_conflicts = { i: set(exam_colors[j] for j in conflicts[i]) for i in exam_colors }
    # for each color c get all colors d where there exists a conflict
    color_conflicts = schedule_times.get_color_conflicts(color_exams, exam_colors, conflicts)
    
    for i in exam_colors:
        print i, exam_color_conflicts[i], color_conflicts[exam_colors[i]]
        
    #compare obj2 and obj3
    for i in exam_colors:
        #print "Exam", i
        assert (len(conflicts[i]) > 0) == (len(color_conflicts[i]) > 0)
        if len(conflicts[i]) > 0:
            a = min( [abs(color_schedule[exam_colors[i]] - color_schedule[exam_colors[j]]) for j in conflicts[i]] )
            b = min( [abs(color_schedule[exam_colors[i]] - color_schedule[d]) for d in color_conflicts[i]] )
            assert a == b
    
    print n_colors
    #print conflicts
    #print exam_colors
    d_n, ov2 = schedule_times.obj2(color_schedule, exam_colors, conflicts)
    d_n, ov3 = schedule_times.obj3(color_schedule, exam_colors, color_conflicts)
    d_n, ov4 = schedule_times.obj4(color_schedule, exam_colors, color_conflicts)
    
    
    
    # 1. choose random color and eligible time slot
    print color_schedule
    color = 1
    old_slot = color_schedule[color]
    new_slot = 7
    
    ## get indices of changes (Important: do this before the actual changes!)
    #change_colors = [c for c in range(len(color_schedule))]#
    #change_colors = improve_annealing.get_changed_colors(color, None, color_exams, color_conflicts, log = False)
        
    #print color_schedule
    #print change_colors
    ## actually perform changes
    #color_schedule[color] = new_slot
    #print color_schedule
    
    #for col in change_colors:
        #print "exams", color_exams[col]
        
    #print color_conflicts[exam_colors[11]]
    #print range(len(exam_colors))
    #print d_n
    #d_n, value = schedule_times.obj4(color_schedule, exam_colors, color_conflicts, d_n = d_n, change_colors = change_colors)
    #print d_n
    #d_n, val = schedule_times.obj3(color_schedule, exam_colors, color_conflicts)
    #print d_n
    #print value, val
    assert ov2 == ov3, "ERROR: OBJECTIVES 2 and 3 DIFFER! %0.2f VS %0.2f" %(ov2, ov3)
    assert ov3 == ov4, "ERROR: OBJECTIVES 3 and 4 DIFFER! %0.2f VS %0.2f" %(ov3, ov4)
    assert ov2 == ov4, "ERROR: OBJECTIVES 2 and 4 DIFFER! %0.2f VS %0.2f" %(ov2, ov4)
    #assert val == value
    print "OBJECTIVE TEST OK"


def SA_benchmark_annealing(n = 25, r = 6, p = 30, prob_conflicts = 0.2, seed = 420):
    
    print "BENCHMARK ANNEALING"
    from time import time
    rd.seed(seed)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = get_coloring(conflicts)
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



def test_changed_colors(seed=42):
    
    # create data
    rd.seed(seed)
    
    n = 30
    h = [2*i for i in range(n)]
    color_schedule = [54, 44, 14, 4, 34, 32, 58, 0]
    n_colors = len(color_schedule)
    
    print color_schedule
    i = 1
    new_value = 18#rd.choice([hi for hi in h if hi not in color_schedule])
    print i, new_value, get_changed_colors(color_schedule, i, new_value)

    j = rd.randint(0, n_colors-1)
    while j == i:
        j = rd.randint(0, n_colors-1)
    print i, j, get_changed_colors(color_schedule, i, color_schedule[j])
    tmp = color_schedule[i]
    color_schedule[i] = color_schedule[j] 
    color_schedule[j] = tmp
    print color_schedule



if __name__ == '__main__':
    SA_test_objectives()
    #SA_benchmark_annealing()
