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
    #SA_benchmark_annealing()
    
    
    n = 10
    r = 10
    p = 5
    prob_conflicts = 0.2
    tseed = 200
    from time import time
    from model.instance import build_smart_random
    from heuristics.johnson import Johnson
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    js = Johnson(data, n_colorings = 1, n_colors = p)
    colorings = js.generate_colorings()
    print colorings
    coloring = colorings[0]

    conflicts = data['conflicts']
    coloring = tools.get_coloring(conflicts)

    n_colors = len(set(coloring[k] for k in coloring))
    print n_colors

    beta_0 = 0.1
    log_hist = True
    print log_hist
    max_iter = 6000
    print max_iter
    rd.seed(tseed)
    t1 = time()
    times, v1 = schedule_times.simulated_annealing(coloring, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist, lazy_threshold=1.0)
    t1 = (time() - t1)*1.0
    print t1
    print v1


