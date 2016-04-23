import networkx as nx
import random as rd

# number of nodes
n = 10
G = nx.Graph()
rands = [ rd.randint(0,2) < 1 for i in range(n**2) ]

for i in range(n):
    for j in range(i,n):
        rands[i*n + j-i] = rands[i*n + j]
        if(rands[i*n + j]):
            G.add_edge(i,j)


import matplotlib
# dont show plots, save them 
matplotlib.use('Agg')
import matplotlib.pyplot as plt

all_colours = ["red", "blue", "green", "yellow", "purple", "orange", "grey", "cyan"]
m = len(all_colours)

colours = ["white"] * n
print(colours)
nx.draw_shell(G, node_color = colours)
plt.savefig('plots/myfig000.jpg')
    
for i in range(0,n):
    colours[i] = all_colours[rd.randint(0,m-1)]
    nx.draw_shell(G, node_color = colours)
    filename = 'plots/myfig'
    if(i < 9) :
        filename = filename + '00'
    elif(i < 99) :
        filename = filename + '0'
    plt.savefig(filename + '%d.jpg' % (i+1))

# convert to animation
import imageio
import os 
os.system("convert -delay 70 -loop 0 plots/*jpg animated.gif")