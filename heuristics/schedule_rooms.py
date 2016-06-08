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
from schedule_times import simulated_annealing

#
# Responsible team member: MAX
#


def obj1(x):
    '''
        Room objective
    '''
    # TODO: Can we just sum over whole x?
    return sum( x[key] for key in x ) 


def schedule_rooms(coloring, color_schedule, data):
    
    # get exams for each color
    color_exams = swap_color_dictionary(coloring)

    periods = [data['h'].index(color) for color in color_schedule]
    
    for color in color_exams:
        
        # TODO Combine x values!!!!!!!!
        # Stop if schedulre_rooms_in_period returns NONE,
        # return NONE in this function if one of the x is NONE
        x = defaultdict(int)
        z = defaultdict(int)
        x = schedule_rooms_in_period(color_exams[color], periods[color], data)
        if x == None:
            return None
        else:
            z.update(x) 

    

    # for i in range(data['n']):
    #     for j in range(data['r']):
    #         print "%s,%s :  %s" %(i,j,z[i,j])
    
    obj_val = obj1(x)
    return z , obj_val

def schedule_rooms_in_period(exams_to_schedule, period, data):
    '''
        schedule_rooms needs to be called for every single period
        schedule_rooms tries to schedule a given set of exams which are written in the same period on the rooms avialable for the given period
    '''
    
    # TODO: Initialise using meaningful values
    # ...


    n = len(exams_to_schedule)
    r = data['r']
    c = data['c']
    T = data['T']
    s = data['s']
    z = {}

    model = Model("RoomPlanner")

    # z[i,k] = if exam i is written in room k
    for k in range(r):
        if T[k][period] == 1:
            for i in exams_to_schedule:
                z[i,k] = model.addVar(vtype=GRB.BINARY, name="z_%s_%s" % (i,k))

    model.update()

    # Building constraints...    
    
    # c1: seats for all students
    for i in exams_to_schedule:
        model.addConstr( quicksum([ z[i, k] * c[k] for k in range(r) for l in range(p) if T[k][period] == 1 ]) >= s[i], "c1")
    
    # c2: only one exam per room
    for k in range(r):
            if T[k][period] == 1:
                model.addConstr( quicksum([ z[i, k] for i in exams_to_schedule  ]) <= 1, "c2")    

    # objective: minimize number of used rooms
    obj1 = quicksum([ z[i,k] for i,k in itertools.product(exams_to_schedule, range(r)) if T[k][period] == 1 ]) 

    model.setObjective( obj1, GRB.MINIMIZE)
    
    model.optimize()


    # return best room schedule
    try:       
        z=defaultdict(int)
        for k in range(r):
            if T[k][period] == 1:
                for i in exams_to_schedule:
                    v = model.getVarByName("z_%s_%s" % (i,k)) 
                    z[i,k]  = v.x    
        return z
    except GurobiError:
        return None




if __name__ == '__main__':
    
    n = 7
    r = 10
    p = 6
    tseed = 37800

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed) 

    coloring = get_coloring(data['conflicts'])

    color_schedule, value = simulated_annealing(coloring, data, max_iter = 100)

    schedule_rooms(coloring, color_schedule, data)

    #schedule_rooms_in_period([i for i in range(n)], 0, data)
    
    
    