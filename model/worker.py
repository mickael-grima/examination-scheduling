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

from model.linear_problem import LinearProblem
from model.non_linear_problem import NonLinearProblem
from model.linear_one_variable_problem import LinearOneVariableProblem
from model.instance import build_random_data
from time import time


def compare_time(data):
    """ we compare for some problems how many time we need to solve each problem
    """
    problems = {
#                'linear': LinearProblem, 
                'non_linear': NonLinearProblem, 
                'linear_one_variable': LinearOneVariableProblem
                }
    times =  dict()
    for prob_name in problems:
        problem = problems[prob_name](data)
        t = time()
        problem.optimize()
        times[prob_name] = time() - t
        
        n, r, p = problem.dimensions['n'], problem.dimensions['r'], problem.dimensions['p']
        x = problem.vars['x']
        i = 1
        #for k in range(r):
            #for l in range(p):
                #print(x[i,k,l])
                
    return times


if __name__ == '__main__':
    data = build_random_data(n=200, r=30, p=30)
    print compare_time(data)
