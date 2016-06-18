#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this script produce instances:
#   - we get it from files
#   - we produce it randomly
#   - or we find simple specific instance

import random as rd
import numpy as np
# from load_rooms import get_random_room_capacity
from collections import defaultdict


def force_data_format(func):
    """ decorator that force the format of data
    """
    def correct_format(**kwards):
        data = func(**kwards)

        n = data.get('n', 0)
        r = data.get('r', 0)
        p = data.get('p', 0)
        w = data.get('w', [["0"] for i in range(n)])
        location = data.get('location', ["0" for k in range(r)])

        Q = data.get('Q')
        conflicts = data.get('conflicts', defaultdict(list))

        if not conflicts:
            conflicts = {}
            for i in range(n):
                conflicts[i] = [j for j in range(n) if Q[i][j]]

        # make sure the conflicts are symmetric!
        for k in conflicts:
            if len(conflicts[k]) > 0:
                assert max(conflicts[k]) < n
            for l in conflicts[k]:
                if k not in conflicts[l]:
                    conflicts[l] += [k]
            conflicts[k] = sorted(conflicts[k])

        # conflicts matrix dense format (dont build if option is set)
        if 'build_Q' in data and not data['build_Q']:
            Q = None
        else:
            if not Q:
                Q = [[1 * (j in conflicts[i] or i in conflicts[j]) for j in range(n)] for i in range(n)]
            else:
                for i in range(n):
                    Q[i][i] = 0
                for i in range(n):
                    for j in range(i + 1, n):
                        Q[j][i] = Q[i][j]

        # locking times sparse and dense format
        locking_times = data.get('locking_times', {})
        if locking_times:
            T = [[1 * (l not in locking_times[k]) for l in range(p)] for k in range(r)]
        else:
            T = data.get('T', [])

        res = {
            'n': n,
            'r': r,
            'p': p,
            'Q': Q,
            'T': T,
            'conflicts': conflicts,
            'locking_times': locking_times,
            's': list(data.get('s', [])),
            'c': list(data.get('c', [])),
            'h': list(data.get('h', [])),
            'w': w,
            'location' : location
        }
        return res
    return correct_format


@force_data_format
def build_random_data(**kwards):
    """ @param n, r, p: number of exams, rooms, periods
    """
    n, r, p = kwards.get('n', 0), kwards.get('r', 0), kwards.get('p', 0)
    prob_conflicts = kwards.get('prob_conflicts', 0.5)
    build_Q = kwards.get('build_Q', True)

    data = {'n': n, 'r': r, 'p': p}
    # we generate a random number of student between 5 and 10 per exam
    data['s'] = [int(5 + 6 * rd.random()) for i in range(n)]
    # the room has a capacity between 5 and 20
    data['c'] = [int(5 + 16 * rd.random()) for k in range(r)]
    # hours between starting day and starting periods are fixed equal to 2
    data['h'] = [2 * l for l in range(p)]

    data['build_Q'] = build_Q

    # conflicts is a list containing a list of conflicts for each index i
    data['conflicts'] = defaultdict(list)
    for i in range(n):
        data['conflicts'][i] = [j for j in range(i + 1, n) if rd.random() <= prob_conflicts]

    # locking time is a list for each room k with locking times
    data['locking_times'] = defaultdict(list)
    for k in range(r):
        data['locking_times'][k] = [l for l in range(p) if rd.random() <= 0.1]

    return data


@force_data_format
def build_small_input():
    small_input = {
        'n': 5,  # 5 exams
        'r': 3,  # 3 rooms
        'p': 3,  # 3 periods
        's': [5, 3, 4, 2, 1],  # number of students per exams
        'c': [5, 4, 1],  # number os seats per rooms
        'Q': [[0, 0, 0, 1, 1],
              [0, 0, 0, 1, 0],
              [0, 0, 0, 1, 1],
              [1, 1, 1, 0, 1],
              [1, 0, 1, 1, 0]],  # Conflicts matrix
        'T': [[1, 0, 1],
              [1, 1, 0],
              [1, 1, 0]],  # Opening times for rooms
        'h': [0, 2, 4]  # number of hours before period
    }
    return small_input


@force_data_format
def build_simple_data(**kwards):
    data = {
        'n': 5,  # 5 exams
        'r': 3,  # 3 rooms
        'p': 3,  # 3 periods
        's': [5, 3, 4, 2, 1],  # number of students per exams
        'c': [5, 4, 1],  # number os seats per rooms
        'conflicts': {0: [3, 4], 1: [3], 2: [0, 1, 2, 4], 3: [0, 2, 3], 4: []},  # Conflicts
        'locking_times': {0: [1], 1: [2], 2: [2]},  # locking times for rooms
        'h': [0, 2, 4]  # number of hours before period
    }
    return data


@force_data_format
def build_smart_random(**kwards):
    """ Generate smart random data
        kwards = {'n': , 'r': ,'p': , 'tseed':, 'w': }
            w = where (0    = not defined
            		   1    = Innenstadt,
                       2    = Garching,
                       3	= Hochbrueck,)

    """
    np.random.seed(kwards.get('tseed', 1))
    rd.seed(kwards.get('tseed', 1))
    n, r, p, w = kwards.get('n', 0), kwards.get('r', 0), kwards.get('p', 0), kwards.get('w', ["1", "2", "3", "4", "5", "6", "7"])
    data = {'n': n, 'r': r, 'p': p}

    #create possible number of participants, increase probability that number of participants is between 150 and 300
    num = [i for i in range(10,901)]
    for times in range(1500):
        num.extend([int(i) for i in range(10,150)])
    for times in range(500):
        num.extend([int(i) for i in range(150,301)])

    # get number of students participating
    data['s'] = np.random.choice(num, n)

    # get room capacity from real data
    data['c'] = np.random.choice(num, r)
    data['c'] = sorted(data['c'], reverse=True)

    if kwards.get('locations') == True:
    	data['w'] = np.random.choice([["1"], ["2"], ["3"], ["2","3"], ["1","2"], ["1","3"], ["1","2","3"]], n , p=[0.2, 0.1, 0.05, 0.05, 0, 0, 0.6])
    	data['location'] = np.random.choice(["1", "2", "3"], r , p=[0.6, 0.35, 0.05])
    
    # hours between starting day and starting periods are fixed equal to 2
    data['h'] = [ 2*l for l in range(p)]
    
    # create a conflict by probybility 1/5
    data['conflicts'] = defaultdict(list)
    for i in range(n):
        data['conflicts'][i] = [ j for j in range(i+1,n) if rd.random() <= 0.1 ]
    
    #close some rooms by probability 1/10
    data['locking_times'] = defaultdict(list)
    for k in range(r):
        data['locking_times'][k] = [ l for l in range(p) if rd.random() <= 0.1 ]
    
    return data

@force_data_format
def build_real_data():
	read_real_data()

   
    return data
