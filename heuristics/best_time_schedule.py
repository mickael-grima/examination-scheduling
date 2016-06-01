


#
# TODO: ROLAND
#


def best_time_schedule(coloring, h):
    '''
        create time schedule permuting the time solts for each coloring
    '''
    
    # TODO: Initialise using meaningful values
    # ...
    p = len(h)
    n = len(coloring[0])
    y = {0 for i in range(n) for l in range(p)}
    
    # TODO: Calculate best time schedule using simulated annealing
    
    return y



if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    # TODO: Construct test case which schedules colorings