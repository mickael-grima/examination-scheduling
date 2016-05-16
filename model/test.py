#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import random
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
    
    # Select models to compare
    problems = {
                'GurobiLinear': build_linear_model,
#                'GurobiQ_neu': build_nonlinear_model, 
 #               'non_linear_problem': NonLinearProblem, 
                }
    
    times =  dict()
    objectives = dict()
    
    for prob_name in problems:
        
        print(prob_name)
        
        # Build selected model
        problem = problems[prob_name](data)
        
        # Optimize selected model
        t = time()
        problem.optimize()
        times[prob_name] = time() - t
        
        # Save objective value
        try:
            objectives[prob_name] = problem.objVal
        except:
            objectives[prob_name] = 0
            
    return times, objectives


if __name__ == '__main__':
    
    n = 20
    r = 9
    p = 3
    
    random.seed(42)
    
    data = build_random_data(n=n, r=r, p=p, conflicts=0.5)
    
    time, objectives = compare(data)
    
    print("")
    for key in time:
        print key
        print("time:")
        print(time[key])
        print("value:")
        print(objectives[key])
        print("")