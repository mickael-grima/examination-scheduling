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

# this script produce instances:
#   - we get it from files
#   - we produce it randomly
#   - or we find simple specific instance
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
        similarp = data.get('similarp', [[-1] for l in range(p)])
        similare = data.get('similare', [[-1] for i in range(n)])
        similarr = data.get('similarr', [[-1] for k in range(r)])

        exam_names = data.get('exam_names', '')
        exam_times = data.get('exam_times', '')
        exam_rooms = data.get('exam_rooms', '')
        room_names = data.get('room_names', '')
        campus_ids = data.get('campus_ids', '')

        Q = data.get('Q', None)
        conflicts = data.get('conflicts', defaultdict(list))

        assert Q is not None or len(conflicts) > 0

        if len(conflicts) == 0:  # build conflicts from Q
            for i in range(n):
                for j in range(i + 1, n):
                    if Q[i][j] == 1 or Q[j][i] == 1:
                        if j not in conflicts[i]:
                            conflicts[i].append(j)
                        if i not in conflicts[j]:
                            conflicts[j].append(i)
        else:    # make sure the conflicts are symmetric!
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
            'location': location,
            'similarp': similarp,
            'similare': similare,
            'similarr': similarr,
            'exam_names': exam_names,
            'exam_times': exam_times,
            'exam_rooms': exam_rooms,
            'room_names': room_names,
            'campus_ids': campus_ids,
        }
        return res
    return correct_format
