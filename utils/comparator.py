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
from model.linear_one_variable_problem import LinearOneVariableProblem
from model.cuting_plane_problem import CutingPlaneProblem

from GurobiModel import (
    GurobiLinear_v_1 as gl1,
    GurobiLinear_v_2_Q as gl2,
    GurobiLinear_v_3 as gl3,
    GurobiLinear_v_4_Cliques as gl4,
    GurobiLinear_v_5_changed_obj as gl5,
    GurobiLinear_v_6_removed_c6 as gl6,
    GurobiLinear_v_7_new_obj as gl7
)

from heuristics import examination_scheduler as main_heuristic
from heuristics import generate_starting_solution as greedy_heuristic
from heuristics import groups_heuristic
from heuristics.AC import AC

import time
from tools import update_variable, transform_variables
from model.objectif_handler import main_obj
from model.constraints_handler import is_feasible

RESULTS_FILE = '%sutils/data/performance'
MODELS = {  # model from folder GurobiModel
    'GurobiLinear_v_1': gl1.build_model,
    'GurobiLinear_v_2_Q': gl2.build_model,
    'GurobiLinear_v_3': gl3.build_model,
    'GurobiLinear_v_4_Cliques': gl4.build_model,
    'GurobiLinear_v_5_changed_obj': gl5.build_model,
    'GurobiLinear_v_6_removed_c6': gl6.build_model,
    'GurobiLinear_v_7_new_obj': gl7.build_model,
    'LinearProblem': LinearProblem,
    'LinearOneVariableProblem': LinearOneVariableProblem,
    'CutingPlaneProblem': CutingPlaneProblem
}
HEURISTICS = {  # heuristics
    'main_heuristic': main_heuristic,
    'greedy_heuristic': greedy_heuristic,
    'groups_heuristic': groups_heuristic
}


def call_heuristic(problem_name, data, **kwards):
    if problem_name == 'main_heuristic':
        x, y, _ = main_heuristic.optimize(AC(data, gamma=kwards.get('gamma', 1.0), num_ants=kwards.get('num_ants', 10)),
                                          data, epochs=kwards.get('epochs', 10),
                                          gamma=kwards.get('gamma', 1.0),
                                          annealing_iterations=kwards.get('annealing_iterations', 1000),
                                          lazy_threshold=kwards.get('lazy_threshold', 0.2),
                                          verbose=kwards.get('verbose', False),
                                          log_history=kwards.get('log_history', False))
    elif problem_name == 'greedy_heuristic':
        x, y = greedy_heuristic.generate_starting_solution_by_maximal_time_slot_filling(data)
    elif problem_name == 'groups_heuristic':
        x, y = groups_heuristic.optimize(data, kwards.get('gamma', 1.0))
    else:
        x, y = {}, {}
    return x, y


def compute_performance(problem_name, data, with_test=False, **kwards):
    """ @param problem: name of the problem, can be:
        part of:
            PROBLEMS = {
                'GurobiLinear_v_1': gl1.build_model,
                'GurobiLinear_v_2_Q': gl2.build_model
            }
        @param data: data
        for variables x, y: compute the time needed to solve the problem, and the value we get
    """
    # compute some numbers about data
    conflicts_average = 0  # conflicts average: average over the line of 1's number
    opening_average = 0  # average over the room's available timeslots

    # How much time to solve the problem ?
    if problem_name in MODELS:
        problem = MODELS[problem_name](data)
        t_start = time.time()
        problem.optimize()
        delta_t = time.time() - t_start
        x, y = update_variable(problem)

    elif problem_name in HEURISTICS:
        t_start = time.time()
        x, y = call_heuristic(problem_name, data, epochs=kwards.get('epochs', 10),
                              gamma=kwards.get('gamma', 1.0),
                              annealing_iterations=kwards.get('annealing_iterations', 1000),
                              lazy_threshold=kwards.get('lazy_threshold', 0.2),
                              verbose=kwards.get('verbose', False),
                              log_history=kwards.get('log_history', False),
                              num_ants=kwards.get('num_ants', 10))
        delta_t = time.time() - t_start
        x, y = transform_variables(x, y)

    else:
        raise Exception("compute_performance: problem's name %s is not an existing problem" % problem_name)

    # Test if the constraints are fullfilled
    if with_test:
        constraints_test = is_feasible(x, y, data)
        test_result = 'FAILED' if [value for value in constraints_test.itervalues() if value] else 'SUCCEED'
    else:
        test_result = 'NOT TESTED'

    # What is the objectif
    obj = main_obj(x, y, data, gamma=kwards.get('gamma', 1.0))

    # Write know the performance to the file
    with open(RESULTS_FILE, 'ab') as src:
        src.write('-------------------------------------\n')
        src.write('@@@ GENERAL @@@\n')
        src.write('Problem: %s\n' % problem_name)
        src.write('Date: %s\n' % time.strftime('%d/%m/%Y"'))
        src.write('\n')
        src.write('@@@ DATA @@@\n')
        src.write('dimensions: n=%s, p=%s, r=%s\n' % (data['n'], data['p'], data['r']))
        src.write('conflicts average per exam: %s\n' % conflicts_average)
        src.write('opening hours average per room: %s\n' % opening_average)
        src.write('\n')
        src.write('Test result: %s\n' % test_result)
        if test_result == 'FAILED':
            src.write('Cause of failure: %s' % ', '.join([cstr for cstr, v in constraints_test.iteritems() if v]))
        src.write('\n')
        src.write('@@@ PERFORMANCE @@@\n')
        src.write('Running time: %s\n' % delta_t)
        src.write('Objective value: %s\n' % obj)
        src.write('-------------------------------------\n\n')
