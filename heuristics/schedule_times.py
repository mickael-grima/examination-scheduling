import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)

import numpy as np
import random as rd
from collections import defaultdict
from copy import deepcopy

from model.instance import build_random_data
from heuristics.tools import get_coloring, swap_color_dictionary


#
# Responsible team member: ROLAND
#

def obj2(times, exam_colors, conflicts):
    exam_times = [ times[exam_colors[i]] for i in exam_colors ]
    return sum([ min( [abs(exam_times[i] - exam_times[j]) for j in conflicts[i]] ) for i in exam_colors if len(conflicts[i]) > 0 ])
    
    
def obj3(times, exam_colors, exam_color_conflicts):
    # TODO: Can this even be speeded up?
    # TODO: If only colors can be considered, speed up about 10x!!!!
    # TODO: Dont do this everytime ( swap, track changes ) 
    #d_n = [ 0 ] * len(exam_colors) 
    #for i in exam_colors:
        #if len(exam_color_conflicts[i]) > 0:
            #d_n[i] = min( [abs(times[exam_colors[i]] - times[j]) for j in exam_color_conflicts[i]] )
    d_n = [ min( [abs(times[exam_colors[i]] - times[j]) for j in exam_color_conflicts[i]] ) for i in exam_colors if len(exam_color_conflicts[i]) > 0]
    return sum(d_n)

  
def simulated_annealing(exam_colors, data, beta_0 = 0.01, times = None, max_iter = 1e4, log = False, log_hist=False):
    
    h = data['h']
    conflicts = data['conflicts']
    color_exams = swap_color_dictionary(exam_colors)
    assert list(exam_colors) == sorted(exam_colors), "Error: Dictionary keys need to be sorted!!"
    
    # for an exam i and a color c count the number of conflicts between them
    exam_color_conflicts = [ set(exam_colors[j] for j in conflicts[i]) for i in exam_colors ]
    
    n_exams = len(exam_colors)
    colors = sorted(color_exams)
    n_colors = len(colors)
        
    assert n_colors <= len(h), "Currently only tables with less colors than timeslots are plannable" 
    
    # the state space for each coloring, calculated from the 
    # TODO: Implement in data and here!
    statespace = [ h ] * n_colors
    
    # initialize the time slots randomly
    # TODO: Careful! Does not consider the statespace so far! Might be infeasible
    if times is None:
        times = rd.sample( h, n_colors )
    
    # initialization and parameters simulated annealing
    beta = beta_0
    schedule = lambda t: beta_0 * np.log(1+np.log(1+t))
    converged = lambda x: x > 1e3
    
    # best values found so far
    best_times = deepcopy(times)
    best_value = obj3(times, exam_colors, exam_color_conflicts)
    
    # initialize loop
    iteration = 0
    counter = 0
    value = best_value
    old_value = best_value
    if log_hist:
        history = []
        best_history = []
    accepted = 0
    
    while iteration < max_iter and not converged(beta):
        iteration += 1
        counter += 1
            
        beta = schedule(counter)
        if log:
            print("Iteration: %d" %iteration)
        if log:
            print times
        
        '''
            make proposal
        '''
        
        # 1. choose random color and eligible time slot
        color = rd.choice(colors)
        old_slot = times[color]
        color2 = None
        new_slot = rd.choice(statespace[color])
        while new_slot == old_slot:
            new_slot = rd.choice([ state for state in statespace[color] if state != old_slot ])
        # 2. find color if the slot is already taken. If so, swap them
        try: 
            color2 = times.index(new_slot)
        except:
            pass
        if log:
            print color
            print color2
        
        times[color] = new_slot
        if color2 is not None:
            times[color2] = old_slot
            
        if log:
            print times
        
        
        assert len(set(times)) == len(times), "time table needs to be uniquely determined!" 
        
        '''
            get objective value
        '''
        value = obj3(times, exam_colors, exam_color_conflicts)
        
        if log:
            print "Obj: %0.2f" % value
        '''
            acceptance step
        '''
        if log:
            print np.exp(-beta * (value - old_value))
        
        # TODO: Check: + beta because of maximization!!!
        if rd.uniform(0,1) <= np.exp( beta * (value - old_value) ):
            old_value = value
            accepted += 1
            
            if log_hist:
                history.append(value)
                
            # save value if better than best
            if value > best_value:
                if log:
                    print("better!")
                if log_hist:
                    best_history.append(value)
                best_value = value
                best_times = deepcopy(times)
                
        else:
            # reject: swap back
            times[color] = old_slot
            if color2 is not None:
                times[color2] = new_slot

    if log_hist:
        print history
        print beta
        print best_history
        
    return best_times, best_value


def schedule_times(coloring, data, beta_0 = 0.01, max_iter = 1e4):
    '''
        Schedule times using simulated annealing
    '''
    color_schedule, value = simulated_annealing(coloring, data, beta_0 = beta_0, max_iter = max_iter, times = None, log = False, log_hist=False)
    times = [ color_schedule[coloring[i]] for i in coloring ]
    
    return times, value
    

if __name__ == '__main__':
    
    n = 25
    r = 6
    p = 30
    prob_conflicts = 0.6
    
    rd.seed(42)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = get_coloring(conflicts)
    n_colors = len(set(exam_colors[k] for k in exam_colors))
    print n_colors
    
    # annealing params
    beta_0 = 1e-3
    max_iter = 1e3
    print max_iter
    
    rd.seed(420)
    log_hist = False
    
    # run annealing
    from time import time
    t1 = time()
    times, v1 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    t1 = (time() - t1)*1.0
    rt1 = t1/max_iter
    print "%0.3f" %t1, v1
    
    