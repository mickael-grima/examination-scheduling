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
from heuristics import schedule_times 
from evaluation import objectives

def test_objectives(n = 30, r = 20, p = 20, prob_conflicts = 0.2, seed = 42):

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
    
    #for i in exam_colors:
        #print i, exam_color_conflicts[i], color_conflicts[exam_colors[i]]
        
    #compare obj2 and obj3
    for i in exam_colors:
        #print "Exam", i
        assert (len(conflicts[i]) > 0) == (len(color_conflicts[i]) > 0)
        if len(conflicts[i]) > 0:
            a = min( [abs(color_schedule[exam_colors[i]] - color_schedule[exam_colors[j]]) for j in conflicts[i]] )
            b = min( [abs(color_schedule[exam_colors[i]] - color_schedule[d]) for d in color_conflicts[i]] )
            assert a == b
    
    
    print n_colors
    
    # true objective
    times = [ color_schedule[exam_colors[exam]] for exam in exam_colors ]
    ov = objectives.obj_time(times, data)
    print ov 
    
    #optimized objective
    ov3 = schedule_times.obj3(color_schedule, exam_colors, color_conflicts)
    
    # 1. choose random color and eligible time slot
    print color_schedule
    color = 1
    old_slot = color_schedule[color]
    new_slot = 7
    
    assert ov == ov3, "ERROR: OBJECTIVES time and 3 DIFFER! %0.2f VS %0.2f" %(ov2, ov3)
    #assert ov3 == ov4, "ERROR: OBJECTIVES 3 and 4 DIFFER! %0.2f VS %0.2f" %(ov3, ov4)
    #assert val == value
    print "OBJECTIVE TEST OK"


if __name__ == '__main__':
    test_objectives()
    