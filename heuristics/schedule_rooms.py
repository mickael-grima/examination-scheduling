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
# TODO: MAX
#


def schedule_rooms(data, exams_to_schedule, period):
    '''
        schedule_rooms needs to be called for every single period
        schedule_rooms tries to schedule a given set of exams which are written in the same period on the rooms avialable for the given period
    '''
    
    # TODO: Initialise using meaningful values
    # ...


    n = length(exams_to_schedule)
    r = data['r']
    c = data['c']
    T = data['T']
    z = {}

    model = Model("RoomPlanner")

    # z[i,k] = if exam i is written in room k
    for k in range(r):
        if T[k][period] == 1:
            for i in range(n):
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
    
    # return best room schedule
    try:       
        z={}
        for i in range(n):
            for k in range(r):
                v = model.getVarByName("z_%s_%s")  % (i,k)
                z[i,k]  = v.x     
        return z
    except GurobiError:
        return None




if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)  

    # TODO: Construct valuable test case which constructs a feasible y
    
    
    