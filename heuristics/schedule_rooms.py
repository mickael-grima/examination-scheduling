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
import timeit
#
# Responsible team member: MAX
#



def schedule_greedy(exams_to_schedule, period, data, verbose = False):
    '''
        Schedule rooms in greedy fashion:
        1. Sort all exams and all rooms descending in the size of the students
        2. Give the largest exam the largest room
        3. If there are students left to be scheduled, insert the remaining ones in the listed in order
        4. repeat until all exams are planned
    '''

    s = data['s']
    c = data['c']
    students = [ s[i] for i in exams_to_schedule ]
    rooms = [ k for k in range(data['r']) if data['T'][k][period] == 1 ]
    capacities = [ c[k] for k in rooms ]
    
    if len(rooms) < len(exams_to_schedule):
        return None
    
    if verbose:
        print exams_to_schedule
        print students
        print rooms
        print capacities
    
    # sort students 
    stud_perm = sorted( zip(exams_to_schedule, students), key=lambda x:-x[1] )
    room_perm = sorted( zip(rooms, capacities), key=lambda x:-x[1] )

    exams = [ ex[0] for ex in stud_perm ]
    sizes = [ ex[1] for ex in stud_perm ]
    
    if verbose:
        print stud_perm
        print room_perm
    
    exams_to_rooms = defaultdict(list)
    index = 0
    while( len(exams) > 0 ):
        
        exam = exams[index]
        size = sizes[index]
        
        # check feasibility
        if len(room_perm) == 0:
            if verbose: print "Infeasible!"
            return None
        
        # assign exams greedily
        # TODO: Maybe it would make sense to not use the largest available room because
        # TODO: this increases the risk of difficult rearrangements
        exams_to_rooms[exam] += [room_perm[0][0]]
        if size > room_perm[0][1]:
            sizes[index] -= room_perm[0][1]
            # resort
            # TODO: Das geht auch klueger!
            stud_perm = sorted(zip(exams, sizes), key=lambda x:-x[1])
            exams = [ ex[0] for ex in stud_perm ]
            sizes = [ ex[1] for ex in stud_perm ]
        else:
            exams.pop(0)
            sizes.pop(0)
        room_perm.pop(0)
    
    if verbose:
        for key in exams_to_rooms:
            print key, exams_to_rooms[key]
    
    return exams_to_rooms
    
    
    

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
    
    z = defaultdict(int)
    
    for color in color_exams:
        #print "COLOR", color
        
        # Stop if schedulre_rooms_in_period returns NONE,
        # return NONE in this function if one of the x is NONE
    
        x = defaultdict(int)
        
        x = schedule_rooms_in_period(color_exams[color], periods[color], data)
        #print "SOL"
        #for key in x:
        #    print key, x[key]
        if x == None:
            return None, sys.maxint
        else:
            z.update(x) 

    

    # for i in range(data['n']):
    #     for j in range(data['r']):
    #         print "%s,%s :  %s" %(i,j,z[i,j])
    
    obj_val = obj1(z)
    return z , obj_val


def schedule_rooms_in_period(exams_to_schedule, period, data, verbose = False):
    #print period
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
        #print k, period
        if T[k][period] == 1:
            for i in exams_to_schedule:
                z[i,k] = model.addVar(vtype=GRB.BINARY, name="z_%s_%s" % (i,k))

    model.update()

    # Building constraints...    
    
    # c1: seats for all students
    for i in exams_to_schedule:
        model.addConstr( quicksum([ z[i, k] * c[k] for k in range(r) if T[k][period] == 1 ]) >= s[i], "c1")
    
    # c2: only one exam per room
    for k in range(r):
            if T[k][period] == 1:
                model.addConstr( quicksum([ z[i, k] for i in exams_to_schedule  ]) <= 1, "c2")    

    # objective: minimize number of used rooms
    obj1 = quicksum([ z[i,k] for i,k in itertools.product(exams_to_schedule, range(r)) if T[k][period] == 1 ]) 

    model.setObjective( obj1, GRB.MINIMIZE)
    
    if not verbose:
        model.params.OutputFlag = 0
    
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
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed, build_Q=False) 

    coloring = get_coloring(data['conflicts'])

    #color_schedule, value = simulated_annealing(coloring, data, max_iter = 100)

    #schedule_rooms(coloring, color_schedule, data)

    #schedule_rooms_in_period([i for i in range(n)], 0, data)
    
    
    
