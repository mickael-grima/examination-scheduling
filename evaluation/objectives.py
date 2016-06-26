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





def obj_room(x):
    if x is None: 
        return sys.maxint

    return sum( x[key] for key in x ) 


def obj_time(times, data, h_max = None):
    
    if times is None:
        return 0.
    
    conflicts = data['conflicts']
    h = data['h']
    
    distance_sum = 0.0
    for i in range(data['n']):
        if len(conflicts[i]) > 0:
            distance_sum += min( [abs(times[i] - times[j]) for j in conflicts[i]] ) 
    
    if h_max is not None:
        return 1.0*distance_sum/h_max
    else:
        return distance_sum
    

