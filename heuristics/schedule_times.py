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
from heuristics.schedule_rooms import schedule_rooms_in_period, schedule_greedy
from heuristics import improve_annealing 
#
# Responsible team member: ROLAND
#
# TODO: Currently works only if n > p!!! Change
# TODO: n = 4, p = 6, seed = 37800
# 

def obj2(color_schedule, exam_colors, conflicts, h_max = None):
    
    # sum min distance to neighboring conflict nodes
    
    d_n = [ 0 ] * len(exam_colors) 
    for i in exam_colors:
        if len(conflicts[i]) > 0:
            d_n[i] = min( [abs(color_schedule[exam_colors[i]] - color_schedule[exam_colors[j]]) for j in conflicts[i]] )
    
    if h_max is not None:
        return d_n, 1.0*sum(d_n)/h_max
    else:
        return d_n, sum(d_n)
    
    
def obj3(color_schedule, exam_colors, color_conflicts, h_max = None):
    
    # sum min distance to neighboring color nodes
    
    d_n = [ 0 ] * len(exam_colors) 
    for i in exam_colors:
        if len(color_conflicts[i]) > 0:
            d_n[i] = min( [abs(color_schedule[exam_colors[i]] - color_schedule[d]) for d in color_conflicts[i]] )
    
    if h_max is not None:
        return d_n, 1.0*sum(d_n)/h_max
    else:
        return d_n, sum(d_n)


def obj4(color_schedule, exam_colors, color_conflicts, h_max = None, d_n = None, change_colors = None):
    
    # sum min distance only consider changed colors!
    
    if d_n is None or change_colors is None:
        return obj3(color_schedule, exam_colors, color_conflicts, h_max = None)
    
    #print change_colors
    for i in exam_colors:    
        if exam_colors[i] in change_colors:
            if len(color_conflicts[exam_colors[i]]) > 0:    
                d_n[i] = min( [abs(color_schedule[exam_colors[i]] - color_schedule[j]) for j in color_conflicts[exam_colors[i]]] )
    
    if h_max is not None:
        return d_n, 1.0*sum(d_n)/h_max
    else:
        return d_n, sum(d_n)


def simulated_annealing(exam_colors, data, beta_0 = 0.3, statespace = None, color_schedule = None, color_exams = None, max_iter = 1e4, log = False, log_hist=False, debug = False):
    '''
        Simulated annealing
        TODO: Description
        @Param statespace: dictionary with list of possible states for each color
        
        Pseudocode:
        1. choose random color and eligible time slot
        2. find color if the slot is already taken. If so, swap them
        3. calculate objective
        4. accept proposal? If not, revert swap
    '''
    
    h = data['h']
    h_max = max(h)
    conflicts = data['conflicts']
    n_exams = len(exam_colors)
    colors = sorted(set(exam_colors.values()))
    n_colors = len(colors)
    
    if debug:
        assert list(exam_colors) == sorted(exam_colors), "Error: Dictionary keys need to be sorted!!"
        assert type(exam_colors) == dict, "ERROR: coloring needs to be a dictionary!"
        assert type(data) == dict, "ERROR: data needs to be a dictionary!"
        assert color_schedule is None or type(color_schedule) == list, "ERROR: color_schedule needs to be either None or a list!"
        assert n_colors <= len(h), "Currently only tables with less colors than timeslots are plannable" 
        if statespace is not None:
            for color in color_exams:
                assert len(statespace[color]) > 1, "Error: statespace needs to contain more than one state for each colors!"
                for slot in statespace[color]:
                    assert schedule_greedy(color_exams[color], h.index(slot), data, verbose = False) is not None
        for exam in exam_colors:
            assert (exam_colors[exam] >= 0) and (exam_colors[exam] <= n_colors), "Error: Colors need to be in range 0, n_colors"
                
    if color_exams is None:
        color_exams = swap_color_dictionary(exam_colors)
    
    # get conflicts of colors
    color_conflicts = improve_annealing.get_color_conflicts(color_exams, exam_colors, conflicts)
    
    # the state space for each coloring, calculated from the 
    # TODO: Implement in data and here!
    if statespace is None:
        statespace = { color: h for color in colors }
    
    # initialize the time slots randomly
    # (TODO: Careful! Does not consider the statespace so far! Might be infeasible)
    if color_schedule is None:
        infeasible = True
        while infeasible:
            color_schedule = rd.sample( h, n_colors )
            infeasible = False
            for color in statespace:
                if color_schedule[color] not in statespace[color]:
                    if log: print "Infeasible start point"
                    infeasible = True
                    break
            
    
    # best values found so far
    best_color_schedule = deepcopy(color_schedule)
    d_n, best_value = obj4(color_schedule, exam_colors, color_conflicts, h_max)
    
    # initialization and parameters simulated annealing
    beta = beta_0
    schedule = lambda t: beta_0 * np.log(1+np.log(1+t))
    #schedule = lambda t: beta_0 * np.log(1+t)
    
    # initialize loop
    iteration = 0
    value = best_value
    old_value = best_value
    if log_hist:
        history = []
        best_history = []
    accepted = 0
    best_value_duration = 0
    
    while iteration < max_iter:
        
        iteration += 1
        beta = schedule(iteration)
        
        if log:
            print("Iteration: %d" %iteration)
            print color_schedule
        
        '''
            make proposal
        '''

        # loop until feasible
        feasible = False
        count_feas = 0
        while not feasible:
                
            color = rd.choice(colors)
            old_slot = color_schedule[color]
            new_slot = rd.choice(statespace[color])
            while new_slot == old_slot:
                new_slot = rd.choice(statespace[color])
                
            color2 = None
            try: 
                color2 = color_schedule.index(new_slot)
            except:
                pass
            
            if color2 is None:
                feasible = True # due to definition of statespace
            elif old_slot in statespace[color2]:
                feasible = True # due to definition of statespace
            count_feas += 1
            
        if log and count_feas > 1: print "while", count_feas
            
        # get indices of changes (Important: do this before the actual changes!)
        change_colors = None
        change_colors = improve_annealing.get_changed_colors(color_schedule, color, new_slot)
        
        # actually perform changes
        color_schedule[color] = new_slot
        if color2 is not None:
            color_schedule[color2] = old_slot
            
        if log:
            print color
            print color2
            print color_schedule
        #print color_schedule
        #print color_exams
        
        assert len(set(color_schedule)) == len(color_schedule), "time table needs to be uniquely determined!" 
        
        '''
            get objective value
        '''
        d_n, value = obj4(color_schedule, exam_colors, color_conflicts, h_max = h_max, d_n = d_n, change_colors = change_colors)
        
        
        '''
            acceptance step
        '''
        
        if log:
            print "Obj: %0.2f" % value
            print np.exp(-beta * (value - old_value))
        
        # exp(+ beta) because of maximization!!!
        if rd.uniform(0,1) <= np.exp( beta * (value - old_value) ):
            accepted += 1
            old_value = value
            
            if log_hist:
                history.append(value)
                
            best_value_duration += 1
            
            # save value if better than best
            if value > best_value:
                best_value = value
                best_color_schedule = deepcopy(color_schedule)
                best_value_duration = 0
    
                if log:
                    print("better!")
                if log_hist:
                    best_history.append(value)
                
            # TODO: best value is attained 50% of the time, stop optimizing
            #if iteration > 0.3*max_iter and 1.0*best_value_duration/iteration > 0.5:
                ##print "Wuhu!", iteration
                #break
    
        else:
            # reject: revert state change, swap back
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


def build_statespace(color_exams, data):
    
    h = data['h']
    
    statespace = { color: [] for color in color_exams }
    
    if 'similar_periods' not in data:
        for color in color_exams:
            for period, time in enumerate(h):
                if schedule_greedy(color_exams[color], period, data) is not None:
                    statespace[color].append(time)
            if len(statespace[color]) == 0:
                return None
    else:
        similar_periods = data['similar_periods']
        
        for color in color_exams:
            
            periods = range(data['p'])
            while len(periods) > 0:
                period = periods[0]
                feasible = schedule_greedy(color_exams[color], period, data) is not None
                if feasible:
                    statespace[color].append(h[period])
                        
                for period2 in similar_periods[period]:
                    if period2 != period and feasible:
                        statespace[color].append(h[period2])
                    periods.remove(period2)
            
            if len(statespace[color]) == 0:
                return None
    
    return statespace

def schedule_times(coloring, data, beta_0 = 0.3, max_iter = 1e4, n_chains = 1, n_restarts = 1, check_feasibility=True):
    '''
        Schedule times using simulated annealing
        TODO: Description
    '''
    
    # build statespace
    statespace = None
    color_exams = swap_color_dictionary(coloring)
    
    # TODO TEST SCHEDULER WITH check_feasibility RETURNS WORS RESULT THEN WITHOUT!!!

    if check_feasibility:
        #print "building statespace"
        statespace = build_statespace(color_exams, data)
        if statespace is None:
            print "infeasible color"
            return None, None
        
    color_schedules = []
    values = []
    for chain in range(n_chains):
        color_schedule = None
        for restart in range(n_restarts):
            color_schedule, value = simulated_annealing(coloring, data, beta_0 = beta_0, max_iter = max_iter, statespace = statespace, color_exams=color_exams, color_schedule = color_schedule)
        color_schedules.append(deepcopy(color_schedule))
        values.append(value)
    
    best_index, best_value = max( enumerate(values), key = lambda x : x[1] )
    
    return color_schedules[best_index], best_value
    

if __name__ == '__main__':
    
    n = 1500
    r = 60
    p = 60
    
    prob_conflicts = 0.15
    
    rd.seed(42)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = get_coloring(conflicts)
    n_colors = len(set(exam_colors[k] for k in exam_colors))
    print n_colors
    
    # annealing params
    max_iter = 1000
    beta_0 = 0.4
    print "Start beta: %f" %beta_0
    print "Iterations: %d" %max_iter
    
    rd.seed(420)
    log_hist = True
    
    # run annealing
    from time import time
    t1 = time()
    times, v1 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    #times, v2 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, color_schedule= times, log_hist=log_hist)
    t1 = (time() - t1)*1.0
    rt1 = t1/max_iter
    print "Time: %0.3f" %t1, "Values:", v1
    
    