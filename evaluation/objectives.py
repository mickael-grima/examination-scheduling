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

    return sum(x[key] for key in x)


def obj_time(times, data):
    if times is None:
        return 0.

    conflicts = data['conflicts']
    
    distances = []
    for i in range(data['n']):
        if len(conflicts[i]) > 0:
            d_i = [abs(times[i] - times[j]) for j in conflicts[i]]
            j = np.argmin(d_i)
            distances.append(d_i[j])

    return np.mean(distances)


def obj(x, y, data, gamma=1.0):
    times = {i: data['h'][l] for i in range(data['n']) for l in range(data['p']) if (y.get(i, l) or 0.0) == 1.0}
    return obj_room(x) - gamma * obj_time(times, data)
