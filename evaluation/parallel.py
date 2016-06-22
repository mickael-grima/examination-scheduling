
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

from heuristics.schedule_exams import optimize
from heuristics.MetaHeuristic import RandomHeuristicAdvanced
from model.instance import build_random_data    
    
from mpi4py import MPI

from evaluation.master_slave import master, slave


def get_data_for_tests(n, r, p, prob_conflicts, seed=None):
    if seed is not None:
        rd.seed(seed)
    return build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
      
      
def run(data, annealing_iterations=1000, epochs=1, n_colorings = 1):
    Heuristic = RandomHeuristicAdvanced(data, n_colorings = n_colorings)
    x, y, v, logger = optimize(Heuristic, data, epochs = epochs, gamma = 0.1, annealing_iterations = annealing_iterations, verbose = False, log_history = True)
    return x,y,v


if __name__=="__main__":

    
    ## Examination scheduling
    n = 15
    r = 6
    p = 15
    prob = 0.2
    
    n_jobs = 1000
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    status = MPI.Status()
    
    if rank == 0:
        rd.seed(42)
        data = get_data_for_tests(n, r, p, prob)
        xs, ys, vs = master(comm, size, status, data, n_jobs)
        print map(lambda x: "%0.2f"%x, filter(lambda x: x < sys.maxint, vs))
        best_index, best_value = min( enumerate(vs), key=lambda x:x[1] )
        print best_value
    else:
        run_function = lambda d: run(d, annealing_iterations=1000, epochs=1, n_colorings = 1)
        slave(comm, rank, size, status, run_function)
        