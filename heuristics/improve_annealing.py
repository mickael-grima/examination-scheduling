import copy
import random as rd

# get changable colors
def get_change_indices(color_schedule, i):    
    srt = sorted(enumerate(color_schedule), key=lambda x : x[1])
    #print srt
    n_colors = len(color_schedule)
    j = 0
    change = [i]
    
    while j < n_colors:
        if j == 0 and srt[j][0] == i:
            change.append(srt[j+1][0])
        elif j == 0 and srt[j+1][0] == i:
            change.append(srt[j][0])
        if j == n_colors-1 and srt[j][0] == i:
            change.append(srt[j-1][0])
        elif j == n_colors-1 and srt[j-1][0] == i:
            change.append(srt[j][0])
        
        if j > 0 and j < n_colors-1 and srt[j][0] == i and abs(srt[j][1] - srt[j+1][1]) <= abs(srt[j][1] - srt[j-1][1]):
            change.append(srt[j+1][0])
        if j > 0 and j < n_colors-1 and srt[j][0] == i and abs(srt[j][1] - srt[j-1][1]) <= abs(srt[j][1] - srt[j+1][1]):
            change.append(srt[j-1][0])
        j += 1
    
    return list(set(change))


def get_changed_colors(color_schedule, i, new_value, color_conflicts, exact=True, log = False):
    '''
        Calculate the indices of the nodes which are affected by annealing permutation.
        This is a result of the nearest neighbor heuristic.
    '''
    swap = False
    if new_value in color_schedule:
        j = color_schedule.index(new_value)
        swap = True
    
    if not swap:
        # new positions, external color
        change = get_change_indices(color_schedule, i)
        if log:
            print i
            print color_schedule
            print change
            
        old_value = color_schedule[i]
        color_schedule[i] = new_value
        change += get_change_indices(color_schedule, i)
        color_schedule[i] = old_value
        if log:
            print new_value
            print color_schedule
            print change
    else:
        # new positions, external color
        change = get_change_indices(color_schedule, i)
        if log:
            print i
            print color_schedule
            print change
        change += get_change_indices(color_schedule, j)
        
        if log:
            
            tmp = color_schedule[i]
            color_schedule[i] = color_schedule[j] 
            color_schedule[j] = tmp
        
            print j
            print color_schedule
            print change
            
    # add conflicts
    if exact:
        for i in copy.deepcopy(change):
            if len(color_conflicts[i]) > 0:
                change += color_conflicts[i]
                
    return list(set(change))


if __name__ == "__main__":
    
    # create data
    rd.seed(42)
    n = 30
    
    h = [2*i for i in range(n)]
    color_schedule = [54, 44, 14, 4, 34, 32, 58, 0]
    n_colors = len(color_schedule)
    
    print color_schedule
    i = 1
    new_value = 18#rd.choice([hi for hi in h if hi not in color_schedule])
    print i, new_value, get_changed_colors(color_schedule, i, new_value)

    j = rd.randint(0, n_colors-1)
    while j == i:
        j = rd.randint(0, n_colors-1)
    print i, j, get_changed_colors(color_schedule, i, color_schedule[j])
    tmp = color_schedule[i]
    color_schedule[i] = color_schedule[j] 
    color_schedule[j] = tmp
    print color_schedule
