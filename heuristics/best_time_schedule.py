import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)

import random as rd

#
# TODO: ROLAND
#


def best_time_schedule(coloring, h):
    '''
        create time schedule permuting the time solts for each coloring
    '''
    
    # TODO: Initialise using meaningful values
    # ...
    n = len(coloring)
    p = len(h)
    y = {}
    for i in range(n):
        for l in range(p):
            y[i,l] = 0.0
    
    
    # TODO: Calculate best time schedule using simulated annealing
    
    # TODO: Consider locked rooms and times constraints
    
    return y


def easy_time_schedule(coloring, h, possible_time_slots = None, max_it = 1e3):
    '''
        create time schedule permuting the time solts for each coloring
    '''
    
    assert(len(coloring) <= len(h), "Currently only tables with less colors than timeslots are plannable")
    # TODO: Initialise using meaningful values
    # ...
    n = len(coloring)
    p = len(h)
    y = {}
    for i in range(n):
        for l in range(p):
            y[i,l] = 0.0
    
    # default value for possible time slots (compiled from constraints)
    if possible_time_slots is None:
        possible_time_slots = [ h ] * n
    
    # construct initial time table
    time_table = range(len(coloring))
    
    beta_0 = 0.1
    beta = beta_0
    cooling_schedule = lambda t: beta_0 * log(t)
    converged = lambda x: x < 1e-6
    while counter < max_it and !converged(beta):
        counter += 1
        beta = cooling_schedule(counter)
        
        # choose random color
        i = rd.randint(n)
        # choose eligible new time slot for color i
        j = rd.choose( possible_time_slots[i] )
        # if slot is taken, swap
        
        
        
    
    # TODO: Calculate simple time schedule
    
    # TODO: Consider locked rooms and times constraints
    
    return y 


def test_time_schedule(n, r, p):
    #coloring = 
    pass


def swop_color_dictionary(dic):
    out = collections.defaultdict(set)
    for k, v in dic.items():
         out[v].add(k)

    for v in out:
        out[v]=list(out[v])     
    return dict(out)

if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    # TODO: Construct test case which schedules colorings