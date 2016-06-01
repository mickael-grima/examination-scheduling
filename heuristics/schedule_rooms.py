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


def schedule_rooms(data, y):
    '''
        create optimal room plan for the fixed exams
    '''
    
    # TODO: Initialise using meaningful values
    # ...
    n = data['n']
    r = data['r']
    x = {}
    for i in range(n):
        for k in range(r):
            x[i,k] = 0.0
    
    # TODO: Maybe use Mickaels heuristic to find a start solution
    
    # TODO: Solve ILP
    infeasible = False
    
    # return best room schedule
    if infeasible:
        return None
    else:
        return x





if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)  

    # TODO: Construct valuable test case which constructs a feasible y
    
    
    