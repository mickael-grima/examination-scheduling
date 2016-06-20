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
import time

from operator import itemgetter

from ConstrainedColorGraph import ConstrainedColorGraph, EqualizedColorGraph
from heuristics.MetaHeuristic import MetaHeuristic
# from heuristics.graph_coloring import greedy_coloring

#
# TODO: ALEX
#

class Johnson(MetaHeuristic):
    
    def __init__(self, data, n_colorings=10, n_colors=2000):
        MetaHeuristic.__init__(self, data, n_colorings = n_colorings)
        self.graph = EqualizedColorGraph(n_colours = n_colors)
        self.graph.build_graph(self.data['n'], self.data['conflicts'])

    def generate_colorings(self):
        # Generate colourings using Johnson's rule: 
        # Order the exams by alpha*s_i + conf_num

        start_time = time.time()
        colorings = []
        conflicts = self.data['conflicts']

        # find number of conflicts for all exams
        conf_num = [0] * self.data['n']
        # go over conflict dictionary and save conflicts
        # Assumes symmetric conflict data
        for i in conflicts:
            conf_num[i] = len(conflicts[i])
            
        start = 0
        end = 0.5
        alpha = list(np.arange(start=start, stop=end, step = (end-start)/float(self.n_colorings)))
        for j in range(self.n_colorings):
            # reset node ordering and coloring
            nodes = self.graph.nodes()
            self.graph.reset_colours()

            # set parameter alpha and compute exam value for ordering
            vals = np.array(self.data['s'])*alpha[j] + np.array(conf_num)

            # sort nodes by vals
            nodes = [elmts[0] for elmts in sorted(zip(nodes, vals), key=itemgetter(1), reverse=True)]
            
            # compute coloring
            for node in nodes:
                self.graph.color_node(node, data=self.data, check_constraints = False)
            colorings.append({n: c for n, c in self.graph.colours.iteritems()}) 

        end_time = time.time()
        print(end_time - start_time)
        print len(colorings)
        return colorings
        
    def update(self, values, best_index = None, time_slots = None):
        # no update necessary yet as of now
        pass
        

if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 5
    tseed = 200

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed) 

    js = Johnson(data, n_colorings = 2, n_colors = p)
    colorings = js.generate_colorings()
    print colorings
    