import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)


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
    
    return y


def easy_time_schedule(coloring, h):
    '''
        create time schedule permuting the time solts for each coloring
    '''
    
    # TODO: Initialise using meaningful values
    # ...
    print(coloring)
    n = len(coloring)
    p = len(h)
    y = {}
    for i in range(n):
        for l in range(p):
            y[i,l] = 0.0
    
    # TODO: Calculate best time schedule using simulated annealing
    
    return y 

if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    # TODO: Construct test case which schedules colorings