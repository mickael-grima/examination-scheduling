#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)

from time import time
from collections import defaultdict

from inputData import examination_data
from heuristics import tools

from heuristics.schedule_rooms import obj1

def obj_time(times, data, h_max = None):
    
    conflicts = data['conflicts']
    h = data['h']
    
    distance_sum = 0.0
    for i in range(n):
        if len(conflicts[i]) > 0:
            distance_sum += min( [abs(times[i] - times[j]) for j in conflicts[i]] ) 
    
    if h_max is not None:
        return 1.0*distance_sum/h_max
    else:
        return distance_sum
    



if __name__ == '__main__':
    
    gamma = 1.0
    
    data = examination_data.read_data(threshold = 0)
    
    data['similar_periods'] = tools.get_similar_periods(data)
    
    n, r, p = data['n'], data['r'], data['p']
    print n, r, p
    
    exam_times = data['exam_times']
    exam_rooms = data['exam_rooms']
    room_names = data['room_names']
    h = data['h']
    x = defaultdict(int)
    y = defaultdict(int)
    for i, exam in enumerate(exam_times):
        l = h.index(exam_times[exam])
        y[i,l] = 1.0
    
    #for room in exam_rooms.values():
        #assert room in room_names.values()
    
    
    rooms_in_moses = set()
    
    illicit_rooms = set()
    penalty = 0
    
    print "Rooms of which we have data:"
    print sorted(room_names.values())
    for i, exam in enumerate(exam_rooms):
        for room in exam_rooms[exam]:
            rooms_in_moses.add(room)
            if room in room_names.values():
                k = room_names.values().index(room)
                x[i,l] = 1.0
            else:
                illicit_rooms.add(room)
                penalty += 1
    print "Rooms in moses:"
    print sorted(rooms_in_moses)
    
    print "Rooms of which we don't have data:"
    print sorted(illicit_rooms)
    
    r1 = set([ room for rooms in exam_rooms.values() for room in rooms ])
    r2 = set(room_names.values())
    print sorted([r for r in r1 if r not in r2])
    
    v = obj1(x) + penalty - gamma * obj_time(exam_times.values(), data, h_max = max(h))
    
    print "VALUE:", v
    