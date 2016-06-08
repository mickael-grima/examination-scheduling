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

import networkx as nx

from model.instance import build_random_data

from copy import deepcopy




#
# TODO: ROLAND
#



def intersect(set1, set2):
    '''
        If the two sets intersect, return True
    '''
    for elem in set1:
        if elem in set2:
            return True
    return False


# for the color c get the conflicting color with the minimum time distance
def get_neighbor(c, times, color_conflicts):
    if len(color_conflicts[c]) == 0:
        return c
    return color_conflicts[c][np.argmin( [ abs(times[c] - times[d]) for d in color_conflicts[c] ] )]


# get a list of neighboring color nodes    
def get_color_neighbors(color_exams, times, color_conflicts):

    # TODO: for d in color_conflicts[c]
    # TODO: Find left and find right
    
    # assuming no conflicting colors are at the same time
    neighbor = [0]*len(times)
    s_times = sorted(enumerate(a), key= lambda x:x[1])
    for c in range(len(times)):
        index, value = s_times[c]
        if i == 0:
            neighbor[index] = s_times[1][0]
        elif i == len(times)-1:
            neighbor[index] = s_times[len(times)-2][0]
        elif abs(s_times[c-1][1] - value) < abs(s_times[c+1][1] - value):
            neighbor[index] = s_times[c-1][0]
        else:
            neighbor[index] = s_times[c+1][0]
    
    print neighbor
    print [ get_neighbor(c, times, color_conflicts) for c in color_exams ]

    return [ get_neighbor(c, times, color_conflicts) for c in color_exams ]
    
# get the colors which changed their min distance if one color is changed without swap
def get_changed_colors(c, times, new_h, color_neighbors, color_conflicts):
    change_colors = []
    for d in range(len(color_neighbors)):
        if color_neighbors[d] == c:
            change_colors.append(d)
    print change_colors
    old_h = times[c]
    times[c] = new_h
    new_neighbor = get_neighbor(c, times, color_conflicts)
    
    

def get_color_conflicts(color_exams, conflicts):
    # get a list of exam conflicts between colors
    color_conflicts = defaultdict(list)
    for c in color_exams:
        for d in color_exams:
            # for each color c check all other colors if there exists at least one conflict
            for i in color_exams[c]:
                if intersect( conflicts[i], color_exams[d] ):
                    color_conflicts[c].append(d)
                    break
    return color_conflicts


def obj4(times, exam_colors, color_exams, color_conflicts):
    # TODO: Can this even be speeded up?
    # TODO: If only colors can be considered, speed up about 10x!!!!
    
    # neighboring distance
    # TODO
    color_conflicts = get_color_conflicts(color_exams, conflicts)
    print color_conflicts
    color_neighbors = get_color_neighbors(color_exams, times, color_conflicts)
    
    
    d_n = [ abs(times[exam_colors[i]] - times[color_neighbors[exam_colors[i]]]) for i in exam_colors ]
    
    print times
    print d_n
    # 1.Fall
    
    return sum(d_n)
  
    
  
def to_binary(time_table, n, p):
    y = defaultdict(int)
    for color in time_table:
        for i in time_table:
            y[i,time_table[i]] = 1.0
            
    

    
def test_color_conflicts():
    # TODO!
    pass
    
    
    
    