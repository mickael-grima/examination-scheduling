import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)


import networkx as nx
from booth.colouring import ColorGraph

def greedy_coloring(data, visiting_scheme):
    
    # TODO: Implement greedy graph coloring algorithm which uses room capacities as boundary conditions
    
    # TODO: Use ColoGraph API for this, please. Might come in handy!
    
    coloring = range(data['n'])
    return coloring 