#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this script produce instances: 
#   - we get it from files
#   - we produce it randomly
#   - or we find simple specific instance

import random as rd
import numpy as np
from load_rooms import get_random_room_capacity


def force_data_format(func):
    """ decorator that force the format of data
    """
    def correct_format(**kwards):
        data = func(**kwards)
        # Q has to be symetric
        Q = data.get('Q', [])
        for i in range(len(Q)):
            for j in range(i):
                Q[i][j] = Q[j][i]
            Q[i][i] = 0
        res = {
            'n': data.get('n', 0),
            'r': data.get('r', 0),
            'p': data.get('p', 0),
            'Q': Q,
            'T': data.get('T', []),
            's': data.get('s', []),
            'c': data.get('c', []),
            'h': data.get('h', [])
        }
        return res
    return correct_format


@force_data_format
def build_random_data(**kwards):
    """ @param n, r, p: number of exams, rooms, periods
    """
    n, r, p = kwards.get('n', 0), kwards.get('r', 0), kwards.get('p', 0)
    conflicts = kwards.get('conflicts', 0.5)
    data = {'n': n, 'r': r, 'p': p}
    # we generate a random number of student between 5 and 10 per exam
    data['s'] = [ int(5 + 6 * rd.random()) for i in range(n)]
    # the room has a capacity between 5 and 20
    data['c'] = [ int(5 + 16 * rd.random()) for k in range(r)]
    # hours between starting day and starting periods are fixed equal to 2
    data['h'] = [ 2*l for l in range(p)]
    # conflicts: 0.75 chance to have a conflict between 2 exams
    data['Q'] = [[ 1*(rd.random()<=conflicts) for j in range(n)] for i in range(n)]
    # opening rooms: 3/4 chance that a room open to a given period
    data['T'] = [[ 1*(rd.random()<=0.75) for l in range(p)] for k in range(r)]
    return data


@force_data_format
def build_simple_data(**kwards):
    data = {
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
    return data


@force_data_format
def build_smart_random(**kwards):
    """ Generate smart random data
        kwards = {'n': , 'r': ,'p': , 'tseed':, 'w': }
            w = where (01    = Innenstadt, 
                       02    = Garching, 
                       02-81 = Hochbrueck) 

    """
    np.random.seed(kwards.get('tseed', 1))
    n, r, p, w = kwards.get('n', 0), kwards.get('r', 0), kwards.get('p', 0), kwards.get('w', ["01", "02", "02-81"])
    data = {'n': n, 'r': r, 'p': p}

    #create possible number of participants, increase probability that number of participants is between 150 and 300
    num = [i for i in range(10,901)]
    for times in range(1500):
        num.extend([int(i) for i in range(10,150)])
    for times in range(500):
        num.extend([int(i) for i in range(150,301)])

    # get number of students participating
    data['s'] = np.random.choice(num,n)
    # get room capacity from real data
    data['c'] = get_random_room_capacity(r,w)
    #create a conflict by probybility 1/5
    data['Q'] = [[1 if rd.random() < 0 else 0 for j in range(n)] for i in range(n)]
    #close some rooms by probability 1/10
    data['T'] = [[1 if rd.random() > 0.1 else 0 for l in range(p)] for k in range(r)]
    #Hours between periods
    data['h'] = [2 for l in range(p)]


    return data

