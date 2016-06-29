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

import numpy as np

def obj_room(x):
    if x is None: 
        return sys.maxint

    return sum( x[key] for key in x ) 


def obj_time(times, data):
    if times is None:
        return 0.
    
    conflicts = data['conflicts']
    K = data['K']
    
    distance_sum = 0.0
    distances = []
    n_students = 0.0
    for i in range(data['n']):
        if len(conflicts[i]) > 0:
            d_i = [abs(times[i] - times[j]) for j in conflicts[i]]
            js = [ j for j, d in enumerate(d_i) if d == min(d_i) ]
            if K is not None:
                for j in js:
                    distance_sum += d_i[j] * K[i, j]
                    n_students += K[i,j]
            else:
                j = js[0]
                distance_sum += d_i[j]
                distances.append(d_i[j])
    
    if K is not None:
        return distance_sum/n_students
    
    return np.mean(distances)
    