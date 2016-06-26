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
    h = data['h']
    
    n, r, p = data['n'], data['r'], data['p']
    print n, r, p
    
    # for each exam the time
    exam_times = data['exam_times']
    # for each exam the room
    exam_rooms = data['exam_rooms']
    # for each room index the name
    room_names = data['room_names']
    
    y = defaultdict(int)
    for i, exam in enumerate(exam_times):
        l = h.index(exam_times[exam])
        y[i,l] = 1.0
    
    x = defaultdict(int)
    Tcount = 0
    exam_count = 0
    for i, exam in enumerate(exam_rooms):
        # if exam is plannable with our data, set variable
        if all(room in room_names.values() for room in exam_rooms[exam]):
            for room in exam_rooms[exam]:
                k = room_names.values().index(room)
                x[i,l] = 1.0
        # otherwise lock the corresponding room
        else:
            exam_count += 1
            for room in exam_rooms[exam]:
                Tcount += 1
                if room in room_names.values():
                    k = room_names.values().index(room)
                    l = h.index(exam_times[exam])
                    data['T'][k][l] = 0.0
          
    print Tcount, exam_count
    v = obj1(x) - gamma * obj_time(exam_times.values(), data, h_max = max(h))
    print "VALUE:", v
    
    if False:
        
        print "Rooms of which we have data:"
        print sorted(room_names.values())
        print "Rooms in moses:"
        r1 = set([ room for rooms in exam_rooms.values() for room in rooms ])
        print sorted(r1)
        print "Rooms of which we don't have data:"
        r2 = set(room_names.values())
        print sorted([r for r in r1 if r not in r2])
        
        