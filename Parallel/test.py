
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

import unittest    
import sys
import cPickle as pick
import collections


import random as rd
from heuristics.generate_starting_solution import generate_starting_solution_by_maximal_time_slot_filling
from heuristics.AC import AC
import heuristics.examination_scheduler as scheduler
from heuristics import tools
from model.instance import build_smart_random, build_small_input, build_random_data
import heuristics.schedule_times as schedule_times
from heuristics.ColorGraph import ColorGraph
from heuristics.MetaHeuristic import *

from utils.tools import transform_variables
from model.constraints_handler import (
    test_conflicts,
    test_enough_seat,
    test_one_exam_per_period,
    test_one_exam_period_room
)

from heuristics.examination_scheduler import *
from heuristics.MetaHeuristic import *
    
    
from mpi4py import MPI
WORKTAG = 0
DIETAG = 1


def get_data_for_tests(n, r, p, prob_conflicts, seed=None):
    if seed is not None:
        rd.seed(seed)
    return build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
      
def run(data, epochs=1, annealing_iterations=500, n_colorings = 40):
    #t = time()
    Heuristic = RandomHeuristic(data, n_colorings = n_colorings)
    x, y, v, logger = optimize(Heuristic, data, epochs = epochs, gamma = 0.1, annealing_iterations = annealing_iterations, verbose = False, log_history = True)
    #print "Time:", time()-t
    #print "VALUE:", v    
    return x,y,v


def master(comm, size, status, data):
    #print "MASTER"
    
    xs = []
    ys = []
    vs = []
    pending = [False] * size
    jobs = range(n_jobs)
    
    for i in range(1, size): 
        
        if len(jobs) == 0:
            break
        job = jobs[0]
        jobs.pop(0)
        
        comm.send(obj = data, dest = i, tag = WORKTAG)
        pending[i] = True
    
    
    # kill slaves which are not used
    for i in range(1,size):
        if not pending[i]:
            comm.send(obj=None, dest=i, tag=DIETAG)
            
    # send jobs while there is work to do  
    while len(jobs) > 0 and any(pending):
        
        # print status
        print "Progress: %d percent" %((1 - 1.0*len(jobs)/n_jobs)*100)
        
        # receive results
        x, y, v = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        pending[status.Get_source()] = False
        xs.append(x)
        ys.append(y)
        vs.append(v)
        
        job = jobs[0]
        jobs.pop(0)
        
        comm.send(obj=None, dest=status.Get_source(), tag=WORKTAG)
        pending[status.Get_source()] = True
    
    # receive jobs
    for i in range(1,size):
        if not pending[i]:
            comm.send(obj=None, dest=i, tag=DIETAG)
            
        x, y, v = comm.recv(None, source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        pending[status.Get_source()] = False
        xs.append(x)
        ys.append(y)
        vs.append(v)
        
    # terminate slaves
    for i in range(1,size):
        comm.send(obj=None, dest=i, tag=DIETAG)
    
    print min(vs)
        
def slave(comm, rank, size, status):
    #print "SLAVE"
    data = None
    while 1:
        
        # receive
        if data is None:
            data = comm.recv(None, source=0, tag=MPI.ANY_TAG, status=status)
        else:
            msg = comm.recv(None, source=0, tag=MPI.ANY_TAG, status=status)
            if msg is not None:
                print "ERROR"
                break
            
        if status.Get_tag() == DIETAG: 
            break
        x, y, v = run(data)
        comm.send(obj=(x, y, v), dest=0)
    




if __name__=="__main__":

    
    ## Examination scheduling
    n = 15
    r = 6
    p = 15
    prob = 0.2
    
    n_jobs = 11
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    status = MPI.Status()
    
    if rank == 0:
        rd.seed(42)
        data = get_data_for_tests(n, r, p, prob)
        master(comm, size, status, data)
        
    else:
        slave(comm, rank, size, status)
        