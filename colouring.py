import networkx as nx
import random as rd
import numpy as np
import os 

import matplotlib
matplotlib.use('Agg') # for not popping up windows
import matplotlib.pyplot as plt

# names for saving
directory = "plots/"
name = "graphcolouring"
if not os.path.exists(directory):
    os.makedirs(directory)


# number of nodes
n = 16
G = nx.Graph()

# construct random node-node-incidence matrix
rands = np.matrix([[rd.randint(0,2) < 1 for i in range(n) ] for j in range(n)])

# make the matrix symmetric
for i in range(n):
    rands[i,i] = True 
    for j in range(i+1,n):
        rands[j,i] = rands[i,j]

# make edges 
for i in range(n):
    for j in range(i+1,n):
        if(rands[i,j]):
            G.add_edge(i,j)

all_colours = ["blue", "red", "yellow", "purple", "orange", "green", "grey", "cyan"]
m = len(all_colours)

# print start configuration
colours = ["white"] * n
nx.draw_shell(G, node_color = colours)
plt.savefig(directory + name + "000.jpg")
    
# graph colouring greedy algorithm with degree heuristic
degree = [ rands[i,range(n)].sum() - 1 for i in range(n) ]

# sort by degree
sl = sorted( zip(degree, range(n)))
lookup_order = [ x[1] for x in sl ]

# revert??
lookup_order = reversed(lookup_order)

def check_neighbours(node, matrix, colour, colours):
    n = np.shape(matrix)[0]
    assert(len(colours) >= n)
    assert(node < n)
    assert(n >= 0)
    
    for j in range(n):
        if matrix[i,j] & (colours[j] == colour):
            return(False)
    return(True)
        
counter = 1
for i in lookup_order:
    for col in all_colours:
        if check_neighbours(i, rands, col, colours):
            colours[i] = col
            nx.draw_shell(G, node_color = colours)
            filename = directory + name
            if(counter < 10) :
                filename = filename + '00'
            elif(counter < 100) :
                filename = filename + '0'
            plt.savefig(filename + '%d.jpg' % (counter))
            counter += 1
            break

print(colours)

# convert to animation
os.system("convert -delay 70 -loop 0 plots/*jpg animated.gif")