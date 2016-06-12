import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)


import itertools
from gurobipy import Model, quicksum, GRB, GurobiError
from heuristics.tools import swap_color_dictionary, get_coloring
from collections import defaultdict
from heuristics.schedule_times import simulated_annealing
from heuristics.schedule_rooms import schedule_rooms, schedule_rooms_in_period, schedule_greedy

from time import time
if __name__ == '__main__':
    
    n = 100
    r = 30
    p = 30
    tseed = 37800

    from model.instance import build_random_data
    import random as rd
    
    n = 1000
    r = 600
    p = 60
    
    prob_conflicts = 0.15
    
    rd.seed(42)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    coloring = get_coloring(data['conflicts'])

    color_schedule, value = simulated_annealing(coloring, data, max_iter = 10)

    #schedule_rooms(coloring, color_schedule, data)

    data['T'][3][0] = 0 
    
    exams = [i for i in range(n) if i%2 == 0]
    #print exams
    print "Greedy"
    t = time()
    xg = schedule_greedy(exams, 0, data, verbose = False)
    print time() - t
    #print xg
    print sum( len(xg[exam]) for exam in xg)
    
    print "ILP"
    t = time()
    x = schedule_rooms_in_period(exams, 0, data)
    print time() - t
    if x is None:
        print x
    else:
        roomcount = 0
        for key in x:
            if x[key] == 1:
                roomcount += 1
        print roomcount
