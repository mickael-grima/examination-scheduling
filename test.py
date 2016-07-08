from multiprocessing import Pool

def f(x):
    return len(x)

from heuristics.ConstrainedColorGraph import ConstrainedColorGraph

if __name__ == '__main__':
    
    from inputData import examination_data
    data = examination_data.read_data(semester = "15W")
    
    graph = ConstrainedColorGraph(n_colours = data['p'])
    graph.build_graph(data['n'], data['conflicts'])  
    for i in range(data['n']):
        for j in data['conflicts'][i]:
            assert (i,j) in graph.graph.edges() or (j,i) in graph.graph.edges(), (i, j, graph.graph.edges())
        