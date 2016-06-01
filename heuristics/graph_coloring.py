
import networkx as nx

def greedy_coloring(data, visiting_scheme):
    
    # TODO: Implement greedy graph coloring algorithm which uses room capacities as boundary conditions
    coloring = range(data['n'])
    return coloring 