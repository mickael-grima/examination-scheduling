


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
    x = {0 for i in range(n) for l in range(r)}
    
    # TODO: Maybe use Mickaels heuristic to find a start solution
    
    # TODO: Solve ILP
    
    # return best room schedule
    return x





if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)    test_compare()

    # TODO: Construct valuable test case which constructs a feasible y
    
    
    