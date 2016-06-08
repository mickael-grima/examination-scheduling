#!/usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import division

import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)

from time import time
import random 

from GurobiModel.GurobiLinear_v_1 import build_model as build_linear_model_1
from GurobiModel.GurobiLinear_v_2_Q import build_model as build_linear_model_2
from GurobiModel.GurobiLinear_v_3 import build_model as build_linear_model_3
from GurobiModel.GurobiLinear_v_4_Cliques import build_model as build_linear_model_4
from GurobiModel.GurobiLinear_v_5_changed_obj import build_model as build_linear_model_5
from GurobiModel.GurobiLinear_v_6_removed_c6 import build_model as build_linear_model_6
from GurobiModel.GurobiLinear_v_8_removed_obj import build_model as build_linear_model_8

from model.instance import build_smart_random


def compare(data):
    """ we compare for some problems how many time we need to solve each problem
    """
    # Select models to compare
    problems = {
         'Linear Advanced removed obj': build_linear_model_8,
    #     'Linear Advanced removed c6': build_linear_model_6,
    #    'Linear Advanced changed obj': build_linear_model_5,
    #    'Linear Advanced': build_linear_model_3,
    #    'Linear Advanced Cliques': build_linear_model_4,    
    #  'GurobiQ_neu': build_nonlinear_model
    }

    times = dict()

    objectives = dict()

    for prob_name in problems:
        print(prob_name)
        # Build selected model
        random.seed(42)

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


def test_compare():
    n = 1500
    r = 65
    p = 60
    tseed = 295

    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)
    time, objectives = compare(data)

    print("")
    print("n: %s" % (n))
    print("r: %s" % (r))
    print("p: %s" % (p))
    print("seed: %s" % (tseed))
    print("Percentage conflicts: %s" % (sum( sum(data['conflicts'][i]) for i in range(n))/(2*n*(n-1))))
    print("")
    for key in time:
        print key
        print("time:")
        print(time[key])
        print("value:")
        print(objectives[key])
        print("")


if __name__ == '__main__':
    test_compare()
