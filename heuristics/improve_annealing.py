import copy
import random as rd
from collections import defaultdict


def get_color_conflicts(color_exams, exam_colors, conflicts):
    '''
        For each exam, get a list of colors with conflicting exams in them
    '''
    # TODO: TEST!

    color_conflicts = defaultdict(list)
    for i in exam_colors:
        color_conflicts[i] = sorted(set( exam_colors[j] for j in conflicts[i] ))
    return color_conflicts        
        
    
    
def get_change_indices(color_schedule, i):    
    '''
        Get slot indices where the min heuristic changes
    '''
    n_colors = len(color_schedule)
    assert i >= 0 and i < n_colors
    
    change = set()
    change.add(i)
    
    # permute to sorted element
    # TODO: Maybe implement myself using old color schdule?
    perm = sorted(enumerate(color_schedule), key=lambda x : x[1])
    
    if i == perm[0][0]:
        # i is the smallest element
        change.add(perm[1][0])
    elif i == perm[n_colors - 1][0]:
        # i is the largest element
        change.add(perm[n_colors-2][0])
    else:
        # find i position in sorted array
        j = 1
        while perm[j][0] != i and j < n_colors-2:
            j += 1
        
        # now we have perm[j][0] == i and perm[j][1] == color_schedule[i]
        assert perm[j][0] == i and perm[j][1] == color_schedule[i]
        
        # check next smallest element left
        if j == 1:
            # i is the second smallest element
            change.add(perm[0][0])
        else:
            # check if neghbor of the element left changed
            if abs(perm[j-1][1] - color_schedule[i]) <= abs(perm[j-1][1] - perm[j-2][1]):
                change.add(perm[j-1][0])
        
        # check next smallest element right
        if j == n_colors-2:
            # i is the second largest element
            change.add(perm[n_colors-1][0])
        else:
            # check if neghbor of the element right changed
            if abs(perm[j+1][1] - color_schedule[i]) <= abs(perm[j+1][1] - perm[j+2][1]):
                change.add(perm[j+1][0])
    
    return change


def get_changed_colors(color_schedule, i, new_value, color_conflicts=None, log = False):
    '''
        Calculate the indices of the nodes which are affected by annealing permutation.
        This is a result of the nearest neighbor heuristic.
    '''
    
    # get indices which change by the permutation
    change = get_change_indices(color_schedule, i)
        
    # the color is present -> Swap positions
    if new_value in color_schedule:
        j = color_schedule.index(new_value)
        change.update(get_change_indices(color_schedule, j))
    else:
        # new positions, external color:
        # set new color, get change, then revert to old color
        old_value = color_schedule[i]
        color_schedule[i] = new_value
        change.update(get_change_indices(color_schedule, i))
        color_schedule[i] = old_value
        
    if log:
        print color_schedule
        print i, new_value
        print change
            
    # TODO: add conflicts (deprecated?)
    if color_conflicts is not None:
        for i in copy.deepcopy(change):
            if len(color_conflicts[i]) > 0:
                change += color_conflicts[i]
                
    return sorted(change)




if __name__ == "__main__":
    # create data
    rd.seed(42)
    
    n = 30
    h = [2*i for i in range(n)]
    color_schedule = [54, 44, 14, 4, 34, 32, 58, 0]
    n_colors = len(color_schedule)
    
    print color_schedule
    
    print sorted(enumerate(color_schedule), key=lambda x : x[1])
    
    for i in range(n_colors):
        print i
        
        print get_change_indices(color_schedule, i)
        #print get_change_indices_old(color_schedule, i)
    
    print "_"
    
    i = 1
    new_value = 18 # rd.choice([hi for hi in h if hi not in color_schedule])
    get_changed_colors(color_schedule, i, new_value, log=True)

    j = rd.randint(0, n_colors-1)
    while j == i:
        j = rd.randint(0, n_colors-1)
    get_changed_colors(color_schedule, i, color_schedule[j], log = True)
    tmp = color_schedule[i]
    color_schedule[i] = color_schedule[j] 
    color_schedule[j] = tmp
    print color_schedule