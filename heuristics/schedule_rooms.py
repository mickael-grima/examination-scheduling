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
from heuristics.tools import swap_color_dictionary

def obj1(x, n, r):
    '''
        Room objective
    '''
    # TODO: Can we just sum over whole x?
    return sum( x[i,k] for i in range(n) for k in range(r) ) 


def schedule_rooms(coloring, time_schedule, data):
    
    if time_schedule is None:
        return None, None
    
    # get exams for each color
    color_exams = swap_color_dictionary(coloring)
    
    for color in color_exams:
        
        # TODO Combine x values!!!!!!!!
        # Stop if schedulre_rooms_in_period returns NONE,
        # return NONE in this function if one of the x is NONE
        x = {}

        time = time_schedule[color_exams[color]][0]
        x = schedule_rooms_in_period(data, color_exams[color], time)
        if x == None:
            return None
        else:
            z.update(x) 

        print z
    
    obj_val = obj1(x, data['n'], data['r'])
    return zgit , obj_val

def schedule_rooms_in_period(data, exams_to_schedule, period):
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
            if T[k][l] == 1:
                model.addConstr( quicksum([ z[i, k] for i in range(n)  ]) <= 1, "c2")    

    # objective: minimize number of used rooms
    obj1 = quicksum([ z[i,k] for i,k in itertools.product(range(n), range(r)) if T[k][l] == 1 ]) 

    model.setObjective( obj1, GRB.MINIMIZE)
    
    model.optimize()


    # return best room schedule
    try:       
        z={}
        for k in range(r):
            if T[k][period] == 1:
                for i in exams_to_schedule:
                    v = model.getVarByName("z_%s_%s" % (i,k)) 
                    z[i,k]  = v.x    
        return z
    except GurobiError:
        return None




if __name__ == '__main__':
    
    n = 55
    r = 64
    p = 1
    tseed = 457

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)  

    schedule_rooms_in_period(data, [i for i in range(n)], 0)
    
    
    