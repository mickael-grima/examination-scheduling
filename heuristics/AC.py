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
import networkx as nx



from model.instance import force_data_format

from heuristics.best_time_schedule import best_time_schedule, easy_time_schedule
from heuristics.schedule_rooms import schedule_rooms

from model.objectives import obj1, obj2

from booth.colouring import ColorGraph
from heuristics.graph_coloring import greedy_coloring



#
# TODO: MICKAEL
#



class AC:
    '''
        Optimize the examination scheduling problem using ant colony optimisation.
        
        data:        dictionary containing all relevant data
        gamma:       weighting factor for objectives
        
        returns x_ik y_il, objVal
    '''
    def __init__(self, data, gamma = 1.0):
        self.data = data
        self.gamma = gamma
        self.traces = [ 1.0*c/len(c) for c in data['conflicts'] if type(c) == list and len(c) > 0]
        
    def optimize(self, num_ants=50, epochs=100, reinitialize=False):
        
        # TODO: Initialise using meaningful values
        # ...
        #
        x, y, objVal = None, None, 1e10
        
        for epoch in range(epochs):
            
            xs = dict()
            ys = dict()
            objVals = dict()
            
            # Generate colourings
            colorings = self.generate_colorings(num_ants)
            
            # evaluate all colorings
            for col in range(len(colorings)):
                xs[col], ys[col], objVals[col] = self.heuristic(colorings[col])
                
            # search for best coloring
            values = [objVals[col] for col in range(len(colorings))]
            best_index = max(range(len(values)), key = lambda i : values[i])
            
            # TODO: Update pheromone traces
            # ...
            #
            
            # save best value so far.. MINIMIZATION
            if values[best_index] < objVal:
                x, y, objVal = xs[best_index], ys[best_index], values[best_index]
            
        return x, y, objVal
    
    
    def generate_colorings(self, num_ants):
        
        # TODO: Construct Graph from Conflicts matrix
        G = ColorGraph()
        
        # get connected components 
        components = nx.connected_component_subgraphs(G.graph)
        
        colorings = []
        for i in range(self.data['n']):
            
            
            # TODO: Generate visiting schemes
            # ...
            visiting_scheme = np.random.shuffle(np.arange(self.data['n'])) 
            
            # TODO: Consider components for ants. If the graph is not connected, then the ants have to also consider all other components
            
            # feed visiting scheme to greedy graph coloring
            coloring = greedy_coloring( self.data, visiting_scheme )
            colorings.append( coloring )
        return colorings
    
    
    def heuristic(self, coloring):
        
        # create preliminary feasible time schedule
        y = easy_time_schedule(coloring, self.data['h'])
        
        # create room plan for the fixed exams
        x = schedule_rooms(self.data, y)
        
        # if infeasible, return large objVal
        if x is None:
            return None, None, 1e10
        
        # create time schedule permuting the time solts for each coloring
        y = best_time_schedule(coloring, self.data['h'])
        
        # evaluate combined objectives
        objVal = obj1(self.data, x) - self.gamma * obj2(self.data, y)
        
        return x, y, objVal
    

if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed) 

    # TODO: Construct meaningful tests
    num_ants = 10
    ac = AC(data)
    colorings = ac.generate_colorings(num_ants)
    print ac.heuristic(colorings[0])
    print (ac.optimize(num_ants))[2]
    print (ac.optimize(num_ants))[2]
    
    
    
