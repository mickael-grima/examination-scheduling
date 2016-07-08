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

import numpy as np

from inputData import examination_data
from heuristics import tools

from evaluation.objectives import obj_time, obj_room, obj_time_y

import model.constraints_handler as constraints
    
def get_moses_representation(data, gamma=1.0, verbose = False):
    
    semester = data['data_version']
    assert semester in ['15W', '16S']
    
    n, r, p = data['n'], data['r'], data['p']
    if verbose: print n, r, p
    
    h = data['h']
    c = data['c']
    s = data['s']
    conflicts = data['conflicts']
    
    # load exam names
    exams = data['exam_names']
    # for each exam the time
    result_times = data['result_times']
    result_dates = data['result_dates']
    
    # for each exam the room
    result_rooms = data['result_rooms']
    
    # for each room index the name
    room_names = data['room_names']
    
    locking_times = data['locking_times']
    
    y = defaultdict(int)
    for i, exam in enumerate(exams):
        l = h.index(result_times[exam])
        y[i,l] = 1.0
    
    x = defaultdict(int)
    for i, exam in enumerate(exams):
        for room in result_rooms[exam]:
            k = room_names.index(room)
            x[i,k] = 1.0
            
    #print constraints.is_feasible(x, y, data)
    
    S = 0.0
    for i in range(n):
        for l in range(p):
            if y[i, l] == 1.0:
                S += sum([y[j, l] for j in conflicts[i]])
    print "Number of conflicts:", S
    
    too_large = 0
    for i in range(n):
        exam_sum = sum( c[k]*x[i,k] for k in range(r) )
        if exam_sum < s[i]:
            too_large += 1
            
    print "Exceeding room capacities ", too_large, "times"
    
    locked_rooms = 0
    for k in range(r):
        for l in locking_times[k]:
            if sum( x[i,k] * y[i,l] for i in range(n) ) == 1 and data['T'][k][l] == 0:
                locked_rooms += 1
                
    print "Locked rooms:", locked_rooms
    
    
    #count_illegal_planned = 0
    #for i, exam in enumerate(exams):
        #for k in range(r):
            #for l in range(p):
                #if x[i,k] * y[i,l] == 1:
                    #if data['T'][k][l] == 0:
                        #count_illegal_planned += 1
                        ##print exam
                        ##print room_names[k], result_dates[exam], data['s'][i]
                        
                    ##print room_names[k], locking_times[k]
                    ##assert data['T'][k][l] == 1, 
    #print "illegal rooms:", count_illegal_planned # = 1
    
    #from inputData.examination_data import read_students
    #import re
    #presem = "14W" if semester == "15W" else "15S"
    ## load number of students registered for each exam
    #exam_students = read_students(presem)
    ##print exam_students
    
    #print "overestimates"
    #overestimates = []
    #overestimates_pre = []
    #for i, exam in enumerate(exams):
        #cap_planned = sum( c[k] for k in range(r) if x[i,k] == 1 )
        #exam = re.sub("\s+\d+\/\d+\/\d+", "", exam)
        #reg_presem = exam_students[exam] if exam in exam_students else "?"
        #overestimates.append(cap_planned - s[i])
        #if reg_presem != "?": overestimates_pre.append(cap_planned - reg_presem)
    #print "mean overestimation of capacities", np.mean(overestimates)
    #print "mean overestimation of capacities", np.mean(overestimates_pre)
    
        
    
    
    times = [result_times[exam] for exam in exams]
    #print obj_time(times, data)
    v = obj_room(x) - gamma * obj_time(times, data)
    
    return x, y, v

    
if __name__ == '__main__':
    
    gamma = 1.0
    
    data = examination_data.load_data(dataset = "1", threshold = 0, verbose = True)
    
    x, y, v = get_moses_representation(data, gamma=gamma, verbose=True)
    times = { i: data['h'][l] for (i,l) in y if y[i,l] == 1 }
    print "ROOM_OBJ:", obj_room(x)
    print "TIME_OBJ:", obj_time_y(y, data)
    print "VALUE:", v
    
    
    
    # get rooms for which we dont have data
    #if False:
        
        #print "Rooms of which we have data:"
        #print sorted(room_names)
        #print "Rooms in moses:"
        #r1 = set([ room for rooms in result_rooms.values() for room in rooms ])
        #print sorted(r1)
        #print "Rooms of which we don't have data:"
        #r2 = set(room_names)
        #print sorted([r for r in r1 if r not in r2])
        
    
    