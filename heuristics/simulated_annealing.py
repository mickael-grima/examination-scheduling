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

import networkx as nx

from model.instance import build_random_data

from copy import deepcopy




#
# TODO: ROLAND
#

def swap_color_dictionary(dic):
    out = defaultdict(set)
    for k, v in dic.items():
         out[v].add(k)

    for v in out:
        out[v]=list(out[v])     
    return dict(out)

    
def to_binary(time_table, n, p):
    y = defaultdict(int)
    for color in time_table:
        for i in time_table:
            y[i,time_table[i]] = 1.0
        
def get_coloring(conflicts):
    # greedy coloring
    graph = nx.Graph()
    for c in conflicts:
        for d in conflicts[c]:
            graph.add_edge(c, d)
    return nx.coloring.greedy_color(graph)
    
    
def obj2(times, exam_colors, conflicts):
    # TODO: Dont do this everytime ( swap, track changes ) 
    exam_times = [ times[exam_colors[i]] for i in exam_colors ]
    return sum([ min( [abs(exam_times[i] - exam_times[j]) for j in conflicts[i]] ) for i in exam_colors if len(conflicts[i]) > 0 ])
    
    
def obj3(times, exam_colors, color_conflicts):
    # TODO: Can this even be speeded up?
    # TODO: If only colors can be considered, speed up about 10x!!!!
    return sum([ min( [abs(times[exam_colors[i]] - times[j]) for j in color_conflicts[i]] ) for i in exam_colors if len(color_conflicts[i]) > 0 ])
  
def simulated_annealing(exam_colors, data, beta_0 = 0.01, times = None, max_iter = 1e4, log = False, log_hist=False):
    
    h = data['h']
    conflicts = data['conflicts']
    color_exams = swap_color_dictionary(exam_colors)
    assert list(exam_colors) == sorted(exam_colors), "Error: Dictionary keys need to be sorted!!"
    
    # for an exam i and a color c count the number of conflicts between them
    color_conflicts = [ set(exam_colors[j] for j in conflicts[i]) for i in exam_colors ]
    
    n = len(exam_colors)
    p = len(h)
    c = len(color_exams)
    n_colors = len(set(color_exams))
    colors = sorted(color_exams)
        
    assert n_colors <= p, "Currently only tables with less colors than timeslots are plannable" 
    
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
    best_value = obj3(times, exam_colors, color_conflicts)
    # initialize loop
    iteration = 0
    counter = 0
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
        
        #value = obj2(times, exam_colors, conflicts)
        value = obj3(times, exam_colors, color_conflicts)
        if log:
            print "Obj: %0.2f" % value
        '''
            acceptance step
        '''
        if log:
            print np.exp(-beta * (value - old_value))
        
        if rd.uniform(0,1) <= np.exp(-beta * (value - old_value)):
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

    

def test_objectives():
    
    rd.seed(42)
    n = 300
    r = 20
    p = 20
    prob_conflicts = 0.2
    
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = get_coloring(conflicts)
    n_colors = len(set(exam_colors[k] for k in exam_colors))
    
    times, value = simulated_annealing(exam_colors, data, max_iter = 100)
    
    # exams per color
    color_exams = swap_color_dictionary(exam_colors)
    
    # for an exam i and a color c count the number of conflicts between them
    color_conflicts = [ set(exam_colors[j] for j in conflicts[i]) for i in exam_colors ]
    
    assert obj2(times, exam_colors, conflicts) == obj3(times, exam_colors, color_conflicts), "ERROR: OBJECTIVES DIFFER!"
    print "OBJECTIVE TEST OK"



from time import time
if __name__ == '__main__':
    
    #test_objectives()
    #exit(0);
    
    
    rd.seed(42)
    n = 1500
    r = 70
    p = 70
    prob_conflicts = 0.2
    
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = get_coloring(conflicts)
    n_colors = len(set(exam_colors[k] for k in exam_colors))
    
    beta_0 = 1e-3
    log_hist = False
    
    max_iter = 1e1
    print max_iter
    rd.seed(420)
    t1 = time()
    times, v1 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    t1 = (time() - t1)*1.0
    rt1 = t1/max_iter
    
    #print t1
    
    max_iter = 1e2
    print max_iter
    rd.seed(420)
    t2 = time()
    times, v2 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    t2 = (time() - t2)*1.0
    rt2 = t2/max_iter
    
    #print t2
    
    max_iter = 1e2
    print max_iter
    rd.seed(420)
    t3 = time()
    times, v3 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    times, v3 = simulated_annealing(exam_colors, data, times = times, beta_0 = beta_0, max_iter = max_iter, log_hist=log_hist)
    t3 = (time() - t3)*1.0
    rt3 = t3/max_iter/2.
    
    print t1, t2, t3
    print rt1, rt2, rt3
    print v1, v2, v3