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

# plotting device 
def plot_graph(graph, colours, counter, directory, name):
    nx.draw_shell(graph, node_color = colours)
    filename = directory + name
    if(counter < 10) :
        filename = filename + '00'
    elif(counter < 100) :
        filename = filename + '0'
    plt.savefig(filename + '%d.jpg' % (counter))
            
            
# fix total number of nodes
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


all_colours = ["blue", "red", "yellow", "cyan", "orange", "green", "purple", "grey"]
m = len(all_colours)

# print start configuration
colours = ["white"] * n
plot_graph(G, colours, 0, directory, name)
    
# graph colouring greedy algorithm with degree heuristic
# see here: https://en.wikipedia.org/wiki/Greedy_coloring
revert = False

# sort by degree
degree = [ rands[i,range(n)].sum() - 1 for i in range(n) ]
sl = sorted( zip(degree, range(n)))
lookup_order = [ x[1] for x in sl ]
if revert:
    lookup_order = reversed(lookup_order)

# the function which checks if the colour has already been used for the neighbouring nodes
def check_neighbours(graph, node, colour, colours):
    for j in [x[1] for x in graph.edges(node)]:
        if colours[j] == colour:
            return(False)
    return(True)
        
# start greedy algorithm
counter = 1
for i in lookup_order:
    for col in all_colours:
        if check_neighbours(G, i, col, colours):
            colours[i] = col
            plot_graph(G, colours, counter, directory, name)
            counter += 1
            break

# convert to animation
os.system("convert -delay 70 -loop 0 plots/*jpg animated.gif")