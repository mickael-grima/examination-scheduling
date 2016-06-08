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
# TODO: Currently works only if n > p!!! Change
# TODO: n = 4, p = 6, seed = 37800
# 

def obj2(times, exam_colors, conflicts):
    exam_times = [ times[exam_colors[i]] for i in exam_colors ]
    return sum([ min( [abs(exam_times[i] - exam_times[j]) for j in conflicts[i]] ) for i in exam_colors if len(conflicts[i]) > 0 ])
    
    
def obj3(color_schedule, exam_colors, exam_color_conflicts):
    # TODO: Can this even be speeded up?
    # TODO: If only colors can be considered, speed up about 10x!!!!
    # TODO: Dont do this everytime ( swap, track changes ) 
    #d_n = [ 0 ] * len(exam_colors) 
    #for i in exam_colors:
        #if len(exam_color_conflicts[i]) > 0:
            #d_n[i] = min( [abs(times[exam_colors[i]] - times[j]) for j in exam_color_conflicts[i]] )
    d_n = [ min( [abs(color_schedule[exam_colors[i]] - color_schedule[j]) for j in exam_color_conflicts[i]] ) for i in exam_colors if len(exam_color_conflicts[i]) > 0]
    return sum(d_n)

  
def simulated_annealing(exam_colors, data, beta_0 = 0.3, color_schedule = None, max_iter = 1e4, log = False, log_hist=False):
    '''
        Simulated annealing
        TODO: Description
    '''
    h = data['h']
    conflicts = data['conflicts']
    color_exams = swap_color_dictionary(exam_colors)
    
    assert list(exam_colors) == sorted(exam_colors), "Error: Dictionary keys need to be sorted!!"
    assert len(color_exams) < sorted(exam_colors), "Error: Dictionary keys need to be sorted!!"
    assert type(exam_colors) == dict, "ERROR: coloring needs to be a dictionary!"
    assert type(data) == dict, "ERROR: data needs to be a dictionary!"
    assert color_schedule is None or type(color_schedule) == list, "ERROR: color_schedule needs to be either None or a list!"
    
    # for an exam i and a color c count the number of conflicts between them
    exam_color_conflicts = [ set(exam_colors[j] for j in conflicts[i]) for i in exam_colors ]
    
    n_exams = len(exam_colors)
    colors = sorted(color_exams)
    n_colors = len(color_exams)
        
    assert n_colors <= len(h), "Currently only tables with less colors than timeslots are plannable" 
    
    # the state space for each coloring, calculated from the 
    # TODO: Implement in data and here!
    statespace = [ h ] * n_colors
    
    # initialize the time slots randomly
    # TODO: Careful! Does not consider the statespace so far! Might be infeasible
    if color_schedule is None:
        color_schedule = rd.sample( h, n_colors )
    
    # initialization and parameters simulated annealing
    beta = beta_0
    schedule = lambda t: beta_0 * np.log(1+np.log(1+t))
    #schedule = lambda t: beta_0 * np.log(1+t)
    
    # best values found so far
    best_color_schedule = deepcopy(color_schedule)
    best_value = obj3(color_schedule, exam_colors, exam_color_conflicts)
    
    # initialize loop
    iteration = 0
    counter = 0
    value = best_value
    old_value = best_value
    if log_hist:
        history = []
        best_history = []
    accepted = 0
    
    while iteration < max_iter:
        iteration += 1
        counter += 1
            
        beta = schedule(counter)
        if log:
            print("Iteration: %d" %iteration)
        if log:
            print color_schedule
        
        '''
            make proposal
        '''
        
        # 1. choose random color and eligible time slot
        color = rd.choice(colors)
        old_slot = color_schedule[color]
        color2 = None
        new_slot = rd.choice(statespace[color])
        while new_slot == old_slot:
            new_slot = rd.choice([ state for state in statespace[color] if state != old_slot ])
        # 2. find color if the slot is already taken. If so, swap them
        try: 
            color2 = color_schedule.index(new_slot)
        except:
            pass
        if log:
            print color
            print color2
        
        color_schedule[color] = new_slot
        if color2 is not None:
            color_schedule[color2] = old_slot
            
        if log:
            print color_schedule
        
        
        assert len(set(color_schedule)) == len(color_schedule), "time table needs to be uniquely determined!" 
        
        '''
            get objective value
        '''
        value = obj3(color_schedule, exam_colors, exam_color_conflicts)
        
        if log:
            print "Obj: %0.2f" % value
        '''
            acceptance step
        '''
        if log:
            print np.exp(-beta * (value - old_value))
        
        # exp(+ beta) because of maximization!!!
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
                best_color_schedule = deepcopy(color_schedule)
                
        else:
            # reject: swap back
            color_schedule[color] = old_slot
            if color2 is not None:
                color_schedule[color2] = new_slot

    if log_hist:
        print "Beta(end):", beta
        print "Opt hist:", best_history
        import matplotlib.pyplot as plt
        plt.plot(history)
        plt.ylabel('obj values')
        plt.savefig("plots/annealing.jpg")
        print "annealing history plot in plots/annealing.jpg"
        
    return best_color_schedule, best_value


def schedule_times(coloring, data, beta_0 = 0.3, max_iter = 1e4, n_chains = 1, n_restarts = 1):
    '''
        Schedule times using simulated annealing
        TODO: Description
    '''
    color_schedules = []
    values = []
    for chain in range(n_chains):
        color_schedule = None
        for restart in range(n_restarts):
            color_schedule, value = simulated_annealing(coloring, data, beta_0 = beta_0, max_iter = max_iter, color_schedule = color_schedule)
        color_schedules.append(deepcopy(color_schedule))
        values.append(value)
    
    best_index, best_value = max( enumerate(values), key = lambda x : x[1] )
    
    return color_schedules[best_index], best_value
    

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
    max_iter = 1e4
    beta_0 = 0.4
    print "Start beta: %f" %beta_0
    print "Iterations: %d" %max_iter
    
    rd.seed(420)
    log_hist = True
    
    # run annealing
    from time import time
    t1 = time()
    times, v1 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    times, v2 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, color_schedule= times, log_hist=log_hist)
    t1 = (time() - t1)*1.0
    rt1 = t1/max_iter
    print "Time: %0.3f" %t1, "Values:", v1, v2
    
    