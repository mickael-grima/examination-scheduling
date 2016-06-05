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
import itertools
#from booth.colouring import ColorGraph

def greedy_coloring(data, G, visiting_scheme):
    
    # TODO: Implement greedy graph coloring algorithm which uses room capacities as boundary conditions
    
    # TODO: Use ColoGraph API for this, please. Might come in handy!
    
    # TODO: Consider constraints for feasible rooms
    
    coloring = {}

    for node in visiting_scheme:
    	neighbour_coloring = set()

    	for neighbour in G.neighbors_iter(node):
    		if neighbour in coloring:
    			neighbour_coloring.add(coloring[neighbour])

    	for color in itertools.count():
    		if color not in neighbour_coloring:
    			break

    	coloring[node] = color

    return coloring 


if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed) 

    G = nx.Graph()
    G.add_nodes_from([0,1,2,3,4,5,6,7,8,9])
    G.add_edges_from([(1,2),(1,3),(2,4),(2,3),(3,5),(5,6),(1,6),(3,6)])

    visiting_scheme=[1,2,3,4,5,6,0,7,8,9]

    coloring = greedy_coloring(data, G, visiting_scheme)
    print coloring
    