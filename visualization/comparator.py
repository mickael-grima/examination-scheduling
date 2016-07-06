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

from argparse import ArgumentParser
import logging

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

from heuristics import schedule_exams as main_heuristic
from heuristics import generate_starting_solution as greedy_heuristic
from heuristics import groups_heuristic
from heuristics.AC import AC

import time
from utils.tools import update_variable, transform_variables
from evaluation.objectives import obj as main_obj
from model.constraints_handler import is_feasible
from model.instance import build_smart_random
from inputData import examination_data

from heuristics.johnson import Johnson


RESULTS_FILE = '%svisualization/data/performance' % PROJECT_PATH
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
    'main_heuristic_AC': main_heuristic,
    'main_heuristic_johnson': main_heuristic,
    'greedy_heuristic': greedy_heuristic,
    'groups_heuristic': groups_heuristic
}
LIST_MODELS = [m for m in MODELS.iterkeys()] + [m for m in HEURISTICS.iterkeys()]


def call_heuristic(problem_name, data, **kwards):
    if problem_name == 'main_heuristic_AC':
        x, y, _, _ = main_heuristic.optimize(AC(data, gamma=kwards.get('gamma', 1.0),
                                             num_ants=kwards.get('num_ants', 10)),
                                             data, epochs=kwards.get('epochs', 10),
                                             gamma=kwards.get('gamma', 1.0),
                                             annealing_iterations=kwards.get('annealing_iterations', 1000),
                                             lazy_threshold=kwards.get('lazy_threshold', 1.0),
                                             verbose=kwards.get('verbose', False),
                                             log_history=kwards.get('log_history', False),
                                             parallel=kwards.get('parallel', False))
    elif problem_name == 'main_heuristic_johnson':
        x, y, _, _ = main_heuristic.optimize(Johnson(data, n_colorings=kwards.get('num_ants', 10), n_colors=data['p']),
                                             data, epochs=1, gamma=kwards.get('gamma', 1.0),
                                             annealing_iterations=kwards.get('annealing_iterations', 1000),
                                             lazy_threshold=kwards.get('lazy_threshold', 1.0),
                                             verbose=kwards.get('verbose', False),
                                             log_history=kwards.get('log_history', False),
                                             parallel=kwards.get('parallel', False))
    elif problem_name == 'greedy_heuristic':
        x, y = greedy_heuristic.generate_starting_solution_by_maximal_time_slot_filling(data)
    elif problem_name == 'groups_heuristic':
        x, y = groups_heuristic.optimize(data, kwards.get('gamma', 1.0))
    else:
        x, y = {}, {}
    return x, y


def compute_performance(problem_name, data, with_test=True, **kwards):
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
    # conflicts average: average over the line of 1's number
    if len(data['conflicts']) == 0 or sum(len(tab) for tab in data['conflicts'].itervalues()) == 0:
        logging.warning('compute_performance: no conflicts found')
        conflicts_average = 'NaN'
    else:
        conflicts_average = sum(len(tab) for tab in data['conflicts'].itervalues()) / float(len(data['conflicts']))
    # average over the room's available timeslots
    opening_average = sum(sum(tab) for tab in data['T']) / float(len(data['T']))

    # How much time to solve the problem ?
    if problem_name in MODELS:
        problem = MODELS[problem_name](data)
        t_start = time.time()
        problem.optimize()
        delta_t = time.time() - t_start
        x, y = update_variable(problem, n=data['n'], r=data['r'], p=data['p'])

    elif problem_name in HEURISTICS:
        t_start = time.time()
        x, y = call_heuristic(problem_name, data, epochs=kwards.get('epochs', 10),
                              gamma=kwards.get('gamma', 1.0),
                              annealing_iterations=kwards.get('annealing_iterations', 1000),
                              lazy_threshold=kwards.get('lazy_threshold', 0.2),
                              verbose=kwards.get('verbose', False),
                              log_history=kwards.get('log_history', False),
                              num_ants=kwards.get('num_ants', 10),
                              parallel=kwards.get('parallel', False))
        delta_t = time.time() - t_start
        x, y = transform_variables(x, y, n=data['n'], r=data['r'], p=data['p'])

    else:
        raise Exception("compute_performance: problem's name %s is not an existing problem" % problem_name)

    # Test if the constraints are fullfilled
    if with_test:
        constraints_test = is_feasible(x, y, data)
        test_result = 'FAILED' if [value for value in constraints_test.itervalues() if not value] else 'SUCCEED'
    else:
        test_result = 'NOT TESTED'

    # What is the objectif
    obj = main_obj(x, y, data, gamma=kwards.get('gamma', 1.0))

    # Write know the performance to the file
    with open(RESULTS_FILE, 'ab') as src:
        src.write('-------------------------------------\n')
        src.write('@@@ GENERAL @@@\n')
        src.write('Problem: %s\n' % problem_name)
        src.write('Date: %s\n' % time.strftime('%d/%m/%Y - %H:%M:%S'))
        src.write('\n')
        src.write('@@@ DATA @@@\n')
        src.write('dimensions: n=%s, p=%s, r=%s\n' % (data['n'], data['p'], data['r']))
        src.write('conflicts average per exam: %s\n' % conflicts_average)
        src.write('opening hours average per room: %s\n' % opening_average)
        src.write('\n')
        src.write('@@@ PARAMETER @@@\n')
        src.write('gamma = %s\n' % kwards.get('gamma', 1.0))
        src.write('annealing iterations = %s\n' % kwards.get('annealing_iterations', 1000))
        src.write('number of ants = %s\n' % kwards.get('num_ants', 10))
        src.write('epochs = %s\n' % kwards.get('epochs', 10))
        src.write('\n')
        src.write('@@@ TEST @@@\n')
        src.write('Test result: %s\n' % test_result)
        if test_result == 'FAILED':
            src.write('Cause of failure: %s\n' % ', '.join([cstr for cstr, v in constraints_test.iteritems() if not v]))
        src.write('\n')
        src.write('@@@ PERFORMANCE @@@\n')
        src.write('Running time: %s\n' % delta_t)
        src.write('Objective value: %s\n' % obj)
        src.write('-------------------------------------\n\n')

    return x, y


def main():
    p = ArgumentParser()
    p.add_argument('-m', '--mode', required=True,
                   help='<Required> give the name of the problem/heuristics to perform.'
                   'The name are %s. The rank could also be given'
                   % str({i: LIST_MODELS[i] for i in range(len(LIST_MODELS))}))
    p.add_argument('-n', '--n', default=0, help='<Default: 0> number of exams')
    p.add_argument('-r', '--r', default=0, help='<Default: 0> number of rooms')
    p.add_argument('-p', '--p', default=0, help='<Default: 0> number of timeslots')
    p.add_argument('-t', '--type', default='real', help='<Default: real> wich kind of data do we use: real or smart')
    args = p.parse_args()

    # data = build_smart_random(n=int(args.n), r=int(args.r), p=int(args.p))
    if args.type == 'smart':
        data = build_smart_random(n=int(args.n), r=int(args.r), p=int(args.p), tseed=1)
    elif args.type == 'real':
        data = examination_data.read_data(semester="15W")
    else:
        logging.warning("%s doesn't exist")
        return
    if args.mode.isdigit():
        compute_performance(LIST_MODELS[int(args.mode)], data, with_test=True)
    else:
        compute_performance(args.mode, data, with_test=True)


def compare_gamma(data_type='real', **dimensions):
    if data_type == 'real':
        data = examination_data.read_data(semester="15W")
    elif data_type == 'random':
        data = build_smart_random(n=dimensions.get('n') or 0.0,
                                  r=dimensions.get('r') or 0.0,
                                  p=dimensions.get('p') or 0.0)
    print "Start compare_gamma:"
    for gamma in [0.1, 0.5, 1.0, 10.0]:
        print "AC, gamma=%s" % gamma
        compute_performance('main_heuristic_AC', data, gamma=gamma,
                            annealing_iterations=1000, num_ants=20,
                            epochs=20, parallel=False)
        print "Johnson, gamma=%s" % gamma
        compute_performance('main_heuristic_johnson', data, gamma=gamma,
                            annealing_iterations=1000, num_ants=20, parallel=False)


def compare_AC_johnson_performance(data_type='real', **dimensions):
    if data_type == 'real':
        data = examination_data.read_data(semester="15W")
    elif data_type == 'random':
        data = build_smart_random(n=dimensions.get('n') or 0.0,
                                  r=dimensions.get('r') or 0.0,
                                  p=dimensions.get('p') or 0.0)
    print "Start compare_AC_johnson_performance:"
    for num_ants in [5, 10, 20]:
        print '@@@ num_ants=%s' % num_ants
        for epochs in [1, 5, 10, 20]:
            for _ in range(10):
                print "AC, epoch=%s" % epochs
                try:
                    compute_performance('main_heuristic_AC', data, gamma=1.0,
                                        annealing_iterations=1000, num_ants=num_ants,
                                        epochs=epochs, parallel=False, verbose=True)
                except Exception as e:
                    logging.warning('compare_AC_johnson_performance: %s' % str(e))
                    continue
        for _ in range(10):
            print "Johnson"
            try:
                compute_performance('main_heuristic_johnson', data, gamma=1.0,
                                    annealing_iterations=1000, num_ants=num_ants,
                                    parallel=False)
            except Exception as e:
                logging.warning('compare_AC_johnson_performance: %s' % str(e))
                continue


if __name__ == '__main__':
    # compare_gamma(data_type='random', n=785, p=173, r=62)
    compare_AC_johnson_performance(data_type='real')
    # main()
