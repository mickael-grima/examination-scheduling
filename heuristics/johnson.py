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
import numpy as np

from heuristics.AC import AC
from heuristics.graph_coloring import greedy_coloring


#
# TODO: ALEX
#

class Johnson:
    
    def __init__(self, data):
        self.data = data
    def generate_colorings(self):
        # TODO: Generate colourings
        conflicts = self.data['conflicts']
        return [ get_coloring(conflicts) ]
    def update(self, values, best_index = None):
        #print "Do something. Value is", values[best_index]
        pass
        

if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed) 

    num_ants = 10
    ac = Johnson(data)
    colorings = ac.generate_colorings(num_ants)
    print colorings
    