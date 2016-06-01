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

class simple_AC(AC):
    '''
        Optimize the examination scheduling problem using shuffling of exam lists.
        
        data:        dictionary containing all relevant data
        gamma:       weighting factor for objectives
        
        returns x_ik y_il, objVal
    '''

    def generate_colorings(self, num_ants):
        
        # TODO: Generate colourings
        # ...
        colorings = []
        for i in range(self.data['n']):
            visiting_scheme = np.random.shuffle(np.arange(self.data['n'])) 
            coloring = greedy_coloring( self.data, visiting_scheme )
            colorings.append( coloring )
        
        return colorings
    

if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed) 

    num_ants = 10
    ac = simple_AC(data)
    colorings = ac.generate_colorings(num_ants)
    print colorings
    