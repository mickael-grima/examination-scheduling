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

from GurobiModel.GurobiQ_v_2 import build_model as build_nonlinear_model
from GurobiModel.GurobiLinear_v_1 import build_model as build_linear_model_1
from GurobiModel.GurobiLinear_v_2_Q import build_model as build_linear_model_2
from GurobiModel.GurobiLinear_v_3 import build_model as build_linear_model_3
from GurobiModel.GurobiLinear_v_4_Cliques import build_model as build_linear_model_4

from model.linear_problem import LinearProblem
from model.non_linear_problem import NonLinearProblem

from model.instance import build_random_data
from model.instance import build_smart_random
from time import time


def compare(data):
    """ we compare for some problems how many time we need to solve each problem
    """
    # Select models to compare
    problems = {
        'Linear Advanced': build_linear_model_3,
        'Linear CliqueCut': build_linear_model_3,
    #    'GurobiQ_neu': build_nonlinear_model
    }

    times = dict()
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


def test_compare():
    n = 50
    r = 50
    p = 30
    tseed = 774032

    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)
    time, objectives = compare(data)

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
