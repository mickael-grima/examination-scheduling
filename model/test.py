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

from GurobiModel.GurobiQ_neu import build_model as build_nonlinear_model
from GurobiModel.GurobiLinear import build_model as build_linear_model

from model.linear_problem import LinearProblem
from model.non_linear_problem import NonLinearProblem

from model.instance import build_random_data
from model.instance import build_smart_random
from time import time

def compare(data):
    """ we compare for some problems how many time we need to solve each problem
    """
    problems = {
#                '1': NonLinearProblem, 
                '2': build_nonlinear_model, 
                '3': build_linear_model
                }
    
    times =  dict()
    objectives = dict()
    for prob_name in problems:
        print(prob_name)
        model = problems[prob_name](data)
        
        t = time()
        model.optimize()
        times[prob_name] = time() - t
        try:
            objectives[prob_name] = model.objVal
        except:
            objectives[prob_name] = 0
    return times, objectives


if __name__ == '__main__':
    
    n = 10
    r = 15
    p = 20
    tseed = 545
    
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)
    time, objectives = compare(data)
    
    print "Number of exams"
    print data['n']
    print "\n"
    print "Number of rooms"
    print data['r']
    print "\n"
    print "Number of Periods"
    print data['p']
    print "\n"
    print "Number of Capacity"
    print data['c']
    print "\n"
    print "Number of Sudents"
    print data['s']
    print "\n"
    print "Number of Conflicts"
    print data['Q']
    print "\n"

    print("")
    for key in time:
        print key
        print("time:")
        print(time[key])
        print("value:")
        print(objectives[key])
        print("")