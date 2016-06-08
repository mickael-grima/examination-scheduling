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


def swap_color_dictionary(dic):
    '''
        swap dict
        @Input: Dictionary {exam: color, }
        @Output: Dictionary {color: [exam1, exam2,...], }
    '''
    out = defaultdict(set)
    for k, v in dic.items():
         out[v].add(k)

    for v in out:
        out[v]=list(out[v])     
    return dict(out)


def get_coloring(conflicts):
    '''
        Generate greedy coloring
        @Input: Conflicts lists
        @Output: A feasible coloring
    '''
    graph = nx.Graph()
    for c in conflicts:
        for d in conflicts[c]:
            graph.add_edge(c, d)
    return nx.coloring.greedy_color(graph)
        
