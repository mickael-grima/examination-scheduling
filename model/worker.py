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
from instance import build_random_data
from time import time


def compare_time(data):
    """ we compare for some problems how many time we need to solve each problem
    """
    lprob = LinearProblem()
    nlprob = NonLinearProblem()
    loprob = LinearOneVariableProblem()
    times = {'linear': 0, 'non_linear': 0, 'linear_one_variable': 0}
    # linear problem
    t = time()
    lprob.build_problem(data)
    lprob.solve()
    times['linear'] = time() - t
    # non linear problem
    t = time()
    nlprob.build_problem(data)
    nlprob.solve()
    times['non_linear'] = time() - t
    # linear one variable problem
    t = time()
    loprob.build_problem(data)
    loprob.solve()
    times['linear_one_variable'] = time() - t

    return times


if __name__ == '__main__':
    data = build_random_data(n=10, r=6, p=8)
    print compare_time(data)
