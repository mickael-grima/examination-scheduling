import numpy as np
import networkx as nx



from model.instance import force_data_format

from heuristics.best_time_schedule import best_time_schedule
from heuristics.schedule_rooms import schedule_rooms

from model.objectives import obj1, obj2

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
        self.traces = [ 1.0*c/len(c) for c in data['conflicts']]
        
        
    def optimize(self, num_ants=50, epochs=100, reinitialize=False):
        
        # TODO: Initialise using meaningful values
        # ...
        #
        x, y, objval = None, None, 1e10
        
        for epoch in epochs:
            
            xs = {}
            ys = {}
            objVals = {}
            
            # Generate colourings
            colorings = self.generate_colorings(num_ants)
            
            # evaluate all colorings
            for col in colorings:
                xs[col], ys[col], objVals[col] = heuristic(col)
            
            # search for best coloring
            values = [objVals[col] for col in colorings]
            best_index = max(range(len(values)), key = lambda i : values[i])
            
            # TODO: Update pheromone traces
            # ...
            #
            
            # save best value so far.. MINIMIZATION
            if values[best_index] < objVal:
                x, y = xs[colorings[best_index]], ys[colorings[best_index]]
                objVal = values[best_index]
            
        return x, y, objVal
    
    
    def generate_colorings(self, num_ants):
        
        # TODO: Generate visiting schemes and colorings using greedy algorithm
        # ...
        colorings = []
        for i in range(self.data['n']):
            visiting_scheme = np.random.shuffle(np.arange(self.data['n'])) 
            coloring = greedy_coloring( visiting_scheme )
            colorings.append( coloring )
        return colorings
    
    
    def heuristic(self, coloring):
        
        # create time schedule permuting the time solts for each coloring
        y = best_time_schedule(coloring, self.data['h'])
        
        # create room plan for the fixed exams
        x = schedule_rooms(self.data, y)
        
        # evaluate combined objectives
        objVal = obj1(self.data, x) - gamma * obj(self.data, y)
        
        return x, y, objVal
    
    

if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)    test_compare()

    # TODO: Construct meaningful tests
    num_ants = 10
    ac = AC(data)
    colorings = ac.generate_colorings(num_ants)
    print colorings
    print heuristic(colorings[0])
    print ac.opimize(num_ants)
    print ac.opimize(num_ants)
    
    
    
