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
#
# Responsible team member: ROLAND
#
# TODO: Currently works only if n > p!!! Change
# TODO: n = 4, p = 6, seed = 37800
# 

def get_changing_colors(color_schedule, color1, color2):
    
    changed = set()
    changed.add(color1)
    if color2 is not None:
        changed.add(color2)
    return changed

def obj2(color_schedule, exam_colors, conflicts, h_max = None):
    
    # sum min distance to neighboring conflict nodes
    
    c_n = [exam_colors[exam] for exam in exam_colors]
    d_n = [ 0 ] * len(exam_colors) 
    for exam in exam_colors:
        if len(conflicts[exam]) > 0:
            c_n[exam] = np.argmin( [abs(color_schedule[exam_colors[exam]] - color_schedule[exam_colors[j]]) for j in conflicts[exam]] )
            d_n[exam] = color_schedule[c_n[exam]]
    if h_max is not None:
        return c_n, d_n, 1.0*sum(d_n)/h_max
    else:
        return c_n, d_n, sum(d_n)
    
    
def obj3(color_schedule, exam_colors, color_conflicts, h_max = None):
    
    # sum min distance to neighboring color nodes
    #for exam in exam_colors:
        #print exam
        #print color_conflicts[exam]
    distance_sum = 0.0
    d_n = [ 0 ] * len(exam_colors)
    for exam in exam_colors:
        if len(color_conflicts[exam]) > 0:
            distance_sum += min( [abs(color_schedule[exam_colors[exam]] - color_schedule[d]) for d in color_conflicts[exam]] ) 
            d_n[exam] = min( [abs(color_schedule[exam_colors[exam]] - color_schedule[d]) for d in color_conflicts[exam]] ) 
    
    if h_max is not None:
        return d_n, 1.0*distance_sum/h_max
    else:
        return d_n, distance_sum

def obj3_optimized(color_schedule, exam_colors, color_conflicts, h_max = None):
    
    # sum min distance to neighboring color nodes
    distance_sum = 0.0
    for exam in exam_colors:
        if len(color_conflicts[exam]) > 0:
            hi = color_schedule[exam_colors[exam]]
            distance_sum += min( [abs(hi - color_schedule[d]) for d in color_conflicts[exam]] ) 
    
    if h_max is not None:
        return 1.0*distance_sum/h_max
    else:
        return distance_sum


def obj4(color_schedule, exam_colors, color_exams, color_conflicts, h_max = None, c_n = None, d_n = None, change_colors = None):
    
    # sum min distance only consider changed colors!
    
    if d_n is None or change_colors is None:
        return obj3(color_schedule, exam_colors, color_conflicts, h_max = h_max)
    
    exams = set()    
        
    for exam in exam_colors:
        # exam changes
        if exam_colors[exam] in change_colors:
         #   print exam
            exams.add(exam)
            continue
        # conflicting exam changes
        for color in color_exams:
            if color in color_conflicts[exam]:
          #      print "---> ", exam
                exams.add(exam)
                break
            
    print len(exams), len(exam_colors)
    
    for exam in exams:
        if len(color_conflicts[exam]) > 0:
            mindex = np.argmin([abs(color_schedule[exam_colors[exam]] - color_schedule[d]) for d in color_conflicts[exam]])
            color = color_conflicts[exam][mindex]
            
            d_n[exam] = abs(color_schedule[exam_colors[exam]] - color_schedule[color])
            assert d_n[exam] == min( [abs(color_schedule[exam_colors[exam]] - color_schedule[d]) for d in color_conflicts[exam]] )
            d_n[exam] = min( [abs(color_schedule[exam_colors[exam]] - color_schedule[d]) for d in color_conflicts[exam]] )
       
        
    if h_max is not None:
        return d_n, 1.0*sum(d_n)/h_max
    else:
        return d_n, sum(d_n)


def is_feasible(color_schedule, statespace):
    '''
        For a given color_schedule check if it is feasible in the given statespace
    '''
    for color in statespace:
        if color_schedule[color] not in statespace[color]:
            return False
    return True
    
    
 
def make_proposal(color_schedule, statespace, n_colors, log=False):
    '''
        Make a proposal for the simulated annealing.
        This loops until a feasible solution is found.
        Feasibility is determined using the statespace.
    '''

    feasible = False
    count_feas = 0
    
    # loop until feasible
    while not feasible:
        
        # draw color to change
        color = rd.randint(0, n_colors-1)
        old_slot = color_schedule[color]
        
        # draw new time slot
        new_slot = rd.choice(statespace[color])
        while new_slot == old_slot:
            new_slot = rd.choice(statespace[color])
            
        # determine if we need to swap colors
        color2 = None
        try: 
            color2 = color_schedule.index(new_slot)
            if old_slot in statespace[color2]:
                feasible = True # due to definition of statespace
        except: # new_slot not found in color_schedule
            feasible = True # due to definition of statespace
        
        count_feas += 1
        
    if log and count_feas > 1: print "while", count_feas
    
    return color, new_slot, color2, old_slot



def get_color_conflicts(color_exams, exam_colors, conflicts):
    '''
        For each exam, get a list of colors with conflicting exams in them
    '''
    # TODO: TEST!

    color_conflicts = defaultdict(list)
    for i in exam_colors:
        color_conflicts[i] = sorted(set( exam_colors[j] for j in conflicts[i] ))
    return color_conflicts        
        
        

def simulated_annealing(exam_colors, data, beta_0 = 0.3, max_iter = 1e4, lazy_threshold = 0.2, statespace = None, color_schedule = None, color_exams = None, log = False, log_hist=False, debug = False):
    '''
        Simulated annealing
        @Param exam_colors: coloring of conflict graph
        @Param data: data dictionary 
        @Param statespace: dictionary with list of possible states for each color
        @Param beta_0: Start of cooling schedule
        @Param max_iter: Number of annealing iterations to perform
        @Param lazy_threshold: Check if the best solution so far has changed much. If set to 1, no lazy evaluation is performed.
        @Param statespace: For each color, which slots are eligible?
        @Param color_schedule: Starting solution (if infeasible, random generation)
        @Param color_exams: A dict with a list of exams for each color
        @Param log: General logging messages
        @Param log_hist: Record all values for performance plotting
        @PAram debug: Do asserts or not?
        
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
    n_colors = len(set(exam_colors.values()))
    
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
                
                
    # for each color get list of exams
    if color_exams is None:
        color_exams = swap_color_dictionary(exam_colors)
    
    # get conflicts of colors
    color_conflicts = get_color_conflicts(color_exams, exam_colors, conflicts)
    
    # the state space for each coloring, calculated from the 
    if statespace is None:
        statespace = { color: h for color in color_exams }
    
    # initialize the time slots randomly
    if color_schedule is None:
        color_schedule = rd.sample( h, n_colors )
        
    # assert a feasible schedule
    while not is_feasible(color_schedule, statespace):
        color_schedule = rd.sample( h, n_colors )
            
            
    # best values found so far
    best_color_schedule = deepcopy(color_schedule)
    d_n, best_value = obj3(color_schedule, exam_colors, color_conflicts, h_max=h_max)
    best_value = obj3_optimized(color_schedule, exam_colors, color_conflicts, h_max=h_max)
    
    # initialization and parameters simulated annealing
    beta = beta_0
    #schedule = lambda t: beta_0 * np.log(1+np.log(1+t))
    schedule = lambda t: beta_0 * np.log(1+t)
    
    # initialize loop
    iteration = 0
    value = best_value
    old_value = best_value
    if log_hist:
        history = []
        best_history = []
        acceptance_rates = []
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

        # get colors to change and their slot values
        color, new_slot, color2, old_slot = make_proposal(color_schedule, statespace, n_colors, log=False)
        if log: print color, new_slot, color2, old_slot
        changed = get_changing_colors(color_schedule, color, color2)
        
        # perform changes to color_schedule
        color_schedule[color] = new_slot
        if color2 is not None:
            color_schedule[color2] = old_slot
        
        if log: print color, color2, color_schedule
            
        if debug: assert len(set(color_schedule)) == len(color_schedule), "time table needs to be uniquely determined!" 
        
        '''
            get objective value
        '''
        
        #d_n_tmp1, value1 = obj4(color_schedule, exam_colors, color_exams, color_conflicts, h_max = h_max, d_n = d_n, change_colors=changed)
        #d_n_tmp, value = obj3(color_schedule, exam_colors, color_conflicts, h_max = h_max)
        value = obj3_optimized(color_schedule, exam_colors, color_conflicts, h_max=h_max)
        #print value1, value
        #assert value == value1
        '''
            acceptance step.
            exp(+ beta) because of maximization!
        '''
        
        if log:
            print "Obj: %0.2f" % value
            print np.exp(-beta * (value - old_value))
        
        if rd.uniform(0,1) <= np.exp( beta * (value - old_value) ):
            
            if log: print "Accepted"
            
            accepted += 1
            old_value = value
            #d_n = d_n_tmp
            # save value if better than best
        
            if value > best_value:
                best_value = value
                best_color_schedule = deepcopy(color_schedule)
                best_value_duration = 0
    
                if log:
                    print("better!")
                
        else:
            # reject: revert state change, swap back
            color_schedule[color] = old_slot
            if color2 is not None:
                color_schedule[color2] = new_slot
                
        best_value_duration += 1
        if log_hist:
            history.append(value)
            best_history.append(best_value)
            acceptance_rates.append(accepted/float(iteration))
        
        if log: print best_value_duration/float(max_iter)
        # TODO: best value is attained 50% of the time, stop optimizing
        if log_hist and best_value_duration/float(max_iter) > lazy_threshold:
            if log: print "Wuhu!", iteration
            break


    if log_hist:
        print "End beta:", beta
        print "iterations:", iteration
        print "acceptance rate:", accepted/float(iteration)
        #print "Opt hist:", best_history
        
        import matplotlib.pyplot as plt
        plt.clf()
        plt.plot(history)
        plt.ylabel('obj values')
        plt.savefig("%sheuristics/plots/annealing.jpg"%PROJECT_PATH)
        
        plt.clf()
        plt.plot(best_history)
        plt.ylabel('best history')
        plt.savefig("%sheuristics/plots/annealing_best.jpg"%PROJECT_PATH)
        
        plt.clf()
        plt.plot(acceptance_rates)
        plt.ylabel('best history')
        plt.savefig("%sheuristics/plots/annealing_rate_accept.jpg"%PROJECT_PATH)
        #print "annealing history plot in plots/annealing.jpg"
       
    return best_color_schedule, best_value



def build_statespace(color_exams, data):
    '''
        Build statespace by checking feasibility for every color and every possible time slot.
        If the similar_periods field is present in the data, this is spead up by considering duplicate times slots.
    '''
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



def schedule_times(coloring, data, beta_0 = 10, max_iter = 1000, n_chains = 1, n_restarts = 1, check_feasibility=False):
    '''
        Schedule times using simulated annealing
        TODO: Description
    '''
    
    # build statespace
    statespace = None
    color_exams = swap_color_dictionary(coloring)
    
    if check_feasibility:
        print "building statespace"
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
    
    rd.seed(4200)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob_conflicts, build_Q = False)
    
    conflicts = data['conflicts']
    exam_colors = get_coloring(conflicts)
    n_colors = len(set(exam_colors[k] for k in exam_colors))
    print "Colors:", n_colors
    
    # annealing params
    max_iter = 1000
    beta_0 = 10
    print "Start beta: %f" %beta_0
    print "Iterations: %d" %max_iter
    
    rd.seed(420)
    
    # run annealing
    from time import time
    n_runs = 1
    t1 = time()
    for i in range(n_runs):
        times, v1 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, log_hist=(i == 0), log=False)
    #times, v2 = simulated_annealing(exam_colors, data, beta_0 = beta_0, max_iter = max_iter, color_schedule= times, log_hist=log_hist)
    t1 = (time() - t1)*1.0/n_runs
    rt1 = t1/max_iter
    print "Time: %0.3f" %t1, "Value:", v1
    
    