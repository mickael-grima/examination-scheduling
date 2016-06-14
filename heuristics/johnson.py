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

from operator import itemgetter

from ConstrainedColorGraph import ConstrainedColorGraph
# from heuristics.AC import AC
# from heuristics.graph_coloring import greedy_coloring


#
# TODO: ALEX
#

class Johnson:
    
    def __init__(self, data,n_colorings=50):
        self.data = data
        self.n_colorings = n_colorings
        self.graph = ConstrainedColorGraph()
        self.graph.build_graph(self.data['n'], self.data['conflicts'])

    def generate_colorings(self):
        # Generate colourings using Johnson's rule: 
        # Order the exams by alpha*s_i + conf_numb

        colorings = []

        for i in range(self.n_colorings):
            # reset node ordering and coloring
            nodes = self.graph.nodes()
            self.graph.reset_colours()

            # set parameter alpha = {0.01,0.02, ... ,0.5} and compute exam value for ordering
            alpha = (i+1)*0.01
            vals = [alpha*d for d in data['s']]

            # sort nodes by vals
            nodes = [elmts[0] for elmts in sorted(zip(nodes, vals), key=itemgetter(1), reverse=True)]

            # compute coloring
            for node in nodes:
                self.graph.color_node(node, data=self.data, check_constraints = False)
            colorings.append({n: c for n, c in self.graph.colours.iteritems()}) 

        return colorings

    def update(self, values, best_index = None):
        # no update necessary yet as of now
        pass
        

if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed) 

    num_ants = 10
    js = Johnson(data)
    colorings = js.generate_colorings()
    # print colorings
    