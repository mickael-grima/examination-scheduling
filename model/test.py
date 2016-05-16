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
from time import time

def compare(data):
    """ we compare for some problems how many time we need to solve each problem
    """
    problems = {
            #    'linear': LinearProblem(data), 
                'non_linear': build_nonlinear_model(data), 
                'linear_one_variable': build_linear_model(data)
                }
    
    times =  dict()
    objectives = dict()
    for prob_name in problems:
        print(prob_name)
        model = problems[prob_name]
        
        t = time()
        model.optimize()
        times[prob_name] = time() - t
        
        objectives[prob_name] = model.objVal
        
    return times, objectives


if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 4
    
    data = build_random_data(n=n, r=r, p=p)
    time, objectives = compare(data)
    
    print("")
    for key in time:
        print key
        print("time:")
        print(time[key])
        print("value:")
        print(objectives[key])
        print("")
