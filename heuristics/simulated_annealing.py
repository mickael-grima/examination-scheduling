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

#
# TODO: ROLAND
#

def swop_color_dictionary(dic):
    out = collections.defaultdict(set)
    for k, v in dic.items():
         out[v].add(k)

    for v in out:
        out[v]=list(out[v])     
    return dict(out)

    
def obj2(times, conflicts):
    
    return sum( min( abs(times[i] - times[j]) for j in conflicts[i]) for i in range(len(times)) )
    
  
def simulated_annealing(exam_colors, data, beta_0 = 1, max_iter = 1):
    
    h = data['h']
    conflicts = data['conflicts']
    color_exams = swap_color_dictionary(exam_colors)
    
    n = len(exam_colors)
    p = len(h)
    c = len(color_exams)
    N = range(n)
        
    assert( n <= p, "Currently only tables with less colors than timeslots are plannable" )
    
    # the state space for each coloring, calculated from the 
    # TODO: Implement in data and here!
    statespace = [ h ] * n
    
    # initialize the time slots randomly
    # TODO: Careful! Does not consider the statespace so far! Might be infeasible
    times = rd.sample( h, n )
    
    # initialization and parameters simulated annealing
    schedule = lambda t: beta_0 * np.log(t)
    converged = lambda x: x > 1e3
    
    # best values found so far
    best_times = deepcopy(times)
    best_value = 1e10
    
    # initialize loop
    counter = 0
    
    while counter < max_it and !converged(beta):
        counter += 1
        beta = schedule(counter)
        
        '''
            make proposal
        '''
        
        # 1. choose random color and eligible time slot
        color = rd.choice(N)
        color2 = None
        old_slot = times[color]
        new_slot = rd.choice(statespace[color])
        
        # 2. find color if the slot is already taken. If so, swap them
        try: 
            times[times.index(new_slot)] = old_slot
        except:
            pass
        
        times[color] = new_slot
        
        assert( len(set(times)) == len(times), "time table needs to be uniquely determined!" )
        
        '''
            get objective value
        '''
        value = obj2(times, conflicts)
        
        '''
            acceptance step
        '''
        if rd.uniform(0,1) <= np.exp(-beta * value):
            # save value if best
            if objVal > objVal_tmp:
                best_value = value
                best_times[color] = new_slot
                if color2:
                    times[color2] = old_slot
        else:
            # reject: swap back
            times[color] = old_slot
            if color2:
                times[color2] = new_slot


def to_binary(time_table, n, p):
    y = defaultdict(int)
    for color in time_table:
    for i in time_table:
        y[i,time_table[i]] = 1.0
    
    

if __name__ == '__main__':
    
    rd.seed(42)
    n = 10
    r = 10
    p = 10
    n_colors = 5
    
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=0.75 )
    
    # random coloring
    exam_colors = { i: rd.randint(0,n_colors-1) for i in range(n) }
    simulated_annealing(exam_colors, data, beta_0 = 1)
    