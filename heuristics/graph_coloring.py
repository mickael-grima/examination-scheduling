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
        #DONE
        #Might be worth in combining coloring with ordering

    
    # TODO: Use ColoGraph API for this, please. Might come in handy!
       #TO DISCUSS
    
    # TODO: Consider constraints for feasible rooms
        #Currrent heuristic
        #Maybe: Solving LP for chcking feasability


    
    # Dictionarry for final coloring
    coloring = {}

    # Keep track of the number of students that have to write in a given period/color for capacity checking
    total_students = {}
    total_rooms = {}

    capacity = sum(data['c'])
    print capacity

    for node in visiting_scheme:
        # Make sure he colors of all the neigbour are known
        neighbour_coloring = set()

        # Find all colorin in neighbourhood
        for neighbour in G.neighbors_iter(node):
            if neighbour in coloring:
                neighbour_coloring.add(coloring[neighbour])

        # Find first color that is not in neighbourhood and which would not exceed room capacity for a given period (by seats and number of room)
        for color in itertools.count():
            if color not in neighbour_coloring:
                if color in total_students:
                    if total_students[color] + data['s'][node] <= capacity and total_rooms[color] + 1 <= data['r']:
                        break
                else:
                    if data['s'][node] <= capacity:
                        break

        # Set found color
        coloring[node] = color

        # Update number of students in given period
        if color in total_students:
            total_students[color] += data['s'][node]
            total_rooms[color] += 1
        else:
            total_students[color] = data['s'][node]
            total_rooms[color] = 1
    
    print data['s']    
    print total_students
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
    #G.add_edges_from([(1,2),(1,3),(2,4),(2,3),(3,5),(5,6),(1,6),(3,6)])

    visiting_scheme=[1,2,3,4,5,6,0,7,8,9]

    coloring = greedy_coloring(data, G, visiting_scheme)
    print coloring   