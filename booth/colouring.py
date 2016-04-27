import networkx as nx
import random as rd
import os, glob
from time import time
import pickle as pk
from argparse import ArgumentParser

import matplotlib
matplotlib.use('Agg')  # for not popping up windows
import matplotlib.pyplot as plt

all_colours = ["blue", "red", "yellow", "purple", "orange", "green", "grey", "cyan", "pink", "black"]
m = len(all_colours)


class ColorGraph(object):
    def __init__(self):
        self.DIRECTORY = "plots/"
        self.plotname = "graphcolouring"
        self.ALL_COLOURS = [str(i) for i in range(20)]

        self.graph = nx.Graph()
        self.colours = {}
        self.revert = True

        if not os.path.exists(self.DIRECTORY):
            os.makedirs(self.DIRECTORY)

        # clear plot directory
        for f in glob.glob(self.DIRECTORY + "*"):
            os.remove(f)

    def add_node(self, node):
        self.graph.add_node(node)
        self.colours.setdefault(node, 'white')

    def add_edge(self, node1, node2):
        self.graph.add_edge(node1, node2)
        self.colours.setdefault(node1, 'white')
        self.colours.setdefault(node2, 'white')

    def reset_colours(self):
        for col in self.colours:
            self.colours[col] = 'white'

    def update_color(self, node, color):
        if self.colours.get(node) is None:
            return False
        self.colours[node] = color
        return True

    def get_degree(self):
        """ return a dictionnary {node: degree}
        """
        degree = {node: len(self.graph.neighbors(node)) for node in self.graph.nodes()}
        return degree

    def get_chromatic_number(self):
        """ return the number of colours used
        """
        return len(set([self.colours[x] for x in self.colours]))

    def check_neighbours(self, node, colour):
        if colour in [self.colours[x[1]] for x in self.graph.edges(node)]:
            return(False)
        return(True)

    def draw(self, save=False, with_labels=False, ind=0):
        colours = [colour for _, colour in self.colours.iteritems()]
        nx.draw_shell(self.graph, node_color=colours, with_labels=with_labels)
        if save:
            filename = self.DIRECTORY + self.plotname
            if(ind < 10):
                filename = filename + '00'
            elif(ind < 100):
                filename = filename + '0'
            plt.savefig("%s%d.jpg" % (filename, ind))

    def draw_calendar(self, save=False, ind=0):
        counter_colors = {color: 0 for color in all_colours}
        fig, ax = plt.subplots()
        for node in self.graph.nodes():
            color_ind = [i for i in range(len(all_colours)) if all_colours[i] == self.colours[node]][0]
            ax.bar(color_ind * 100, 40, width=100, bottom=counter_colors[self.colours[node]] * 50,
                   color=self.colours[node])
            counter_colors[self.colours[node]] += 1
        if save:
            fig.savefig("%scalendar.jpg" % self.DIRECTORY)
        else:
            plt.show()
        if save:
            filename = self.DIRECTORY + 'calendar'
            if(ind < 10):
                filename = filename + '00'
            elif(ind < 100):
                filename = filename + '0'
            plt.savefig("%s%d.jpg" % (filename, ind))

    def get_calendar_simulation_files(self, save=False):
        """ @param history: dictionnary of key: value. key = step, value = list of colours
            if save,we save the different steps in self.DIRECTORY
        """
        for step, colours in self.history.iteritems():
            self.colours = colours
            self.draw_calendar(save=True, ind=step)

    def reinitialized(self):
        """ reinitialized all colour to 'white'
        """
        self.colours = {node: 'white' for node in self.colours.iterkeys()}

    def build_rand_graph(self, nb_nodes=16, probability=0.5):
        # construct random node-node-incidence matrix
        rands = [rd.random() < probability for i in range(int(1 + 0.5 * nb_nodes * (nb_nodes - 1)))]

        # make edges
        counter = 0
        for i in range(nb_nodes):
            self.add_node(i)
            for j in range(i + 1, nb_nodes):
                if(rands[counter]):
                    self.add_edge(i, j)
                counter += 1

    def build_sudoku_graph(self, nb_nodes=16):
        if nb_nodes != 16:
            print("Sorry, currently only 4x4 sudoku is supported!")
            nb_nodes = 16

        for i in range(4):
            for j in range(4):
                for k in range(4):
                    self.add_edge(i * 4 + j, i * 4 + k)
                    self.add_edge(i * 4 + j, k * 4 + j)
        self.add_edge(0 * 4, (1) * 4 + 1)
        self.add_edge(1 * 4, (0) * 4 + 1)
        self.add_edge(0*4+2, (1)*4+3)
        self.add_edge(1*4+2, (0)*4+3)
        self.add_edge(2*4, (3)*4+1)
        self.add_edge(3*4, (2)*4+1)
        self.add_edge(2*4+2, (3)*4+3)
        self.add_edge(3*4+2, (2)*4+3)

    def color_node(self, node):
        """ Check the colors of the neighbors, and color the node with a different color
        """
        for col in all_colours:
            if self.check_neighbours(node, col):
                self.colours[node] = col
                break

    def color_graph(self, save=False):
        degree = self.get_degree()

        # sort by degree
        sl = sorted([(dg, node) for node, dg in degree.iteritems()])
        lookup_order = [x[1] for x in sl]
        if self.revert:
            lookup_order = reversed(lookup_order)

        fig, ax = plt.subplots()

        counter = 1
        for node in lookup_order:

            # respect initial condition
            if self.colours[node] != 'white':
                continue

            self.color_node(node)

            # Save the pictures
            if save:
                self.draw(save=save, ind=counter)
            counter += 1

        if save:
            self.draw(save=True, ind=counter)

        return self.colours

    def color_graph_rand(self, save=False):
        """ @ param max_room: max number of room. If -1 then we can take as many rooms as we want
        We color the graph choosing randomly a node at each step
        """
        degree = self.get_degree()
        # sort by degree
        sl = sorted([(dg, node) for node, dg in degree.iteritems()])
        lookup_order = [x[1] for x in sl]
        degree = [x[0] for x in sl]
        # revert??
        lookup_order = list(reversed(lookup_order))

        if save:
            fig, ax = plt.subplots()

        while lookup_order:
            rand, n, ind = rd.randint(0, sum(degree)), 0, 0
            while ind < len(degree):
                n += degree[ind]
                if n >= rand:
                    break
                ind += 1
            counter, node = 1, lookup_order[ind]
            self.color_node(node)
            # Save the pictures
            if save:
                self.draw(save=save, ind=counter)
            counter += 1
            del lookup_order[ind]
            del degree[ind]

        return self.colours

    def color_graph_rand_iter(self, max_room=-1, it=10, save=False):
        """ @ param max_room: max number of room. If -1 then we can take as many rooms as we want
        We color the graph choosing randomly a node at each step
        We do the coloration it times, and we keep the graph wich has not more rooms than max_room, and with
        the minimum number of color
        """
        colours, min_chromatic_number = {}, []
        for i in range(it):
            self.reset_colours()
            cols = self.color_graph_rand(save=save)
            max_ind_set = max([len([node for node, colour in cols.iteritems() if colour == col])
                              for col in all_colours])
            nb_color = len(set([color for node, color in cols.iteritems()]))
            min_chromatic_number.append(len(set([color for node, color in colours.iteritems()])))
            # If too many rooms
            if max_room >= 0 and max_ind_set > max_room:
                continue
            # If the number of periods is larger
            if colours and nb_color >= len(set([color for node, color in colours.iteritems()])):
                continue
            colours = cols
        self.colours = colours
        return colours


def find_bad_greedy_algorithm_graph(nb_it=50):
    graphs = {}  # key = nb_node, value = graph
    node_min, node_max = 5, 20
    print "----------- Start ---------------"
    t = time()
    for n in range(node_min, node_max + 1):
        diff = 0
        print "Number of nodes: %s" % n
        for it in range(nb_it):
            G = ColorGraph()
            G.build_rand_graph(nb_nodes=n, probability=0.3)
            # greedy algorithm
            G.color_graph(save=False)
            n_greedy = G.get_chromatic_number()
            # rand algorithm
            G.reset_colours()
            G.color_graph_rand_iter(it=20, save=False)
            n_rand = G.get_chromatic_number()
            # We compare the solutions
            delta_n = n_greedy - n_rand
            if delta_n > diff:
                diff = delta_n
                graphs[n] = (G, diff)
    print "Job completed after %s sec" % (time() - t)
    print "----------- Done ---------------"
    pk.dump(graphs, open('files/relevant_graphs', 'wb'))
    return graphs


def test():
    colouring_file_test = True

    if colouring_file_test:
        n = 16

        G = ColorGraph()
        G.build_sudoku_graph()
        G.draw(save=True, ind=0)
        G.color_graph(save=True)
        print(G.get_chromatic_number())

        G = ColorGraph()
        G.revert = False
        G.build_rand_graph(nb_nodes=n)
        G.color_graph(save=True)
        print(G.get_chromatic_number())

        G.draw_calendar(save=True)

        # convert to animation
        import time
        time.sleep(1)  # delays for 5 seconds
        os.system("convert -delay 70 -loop 0 plots/*jpg animated.gif")

        print(G.colours)

        # G = ColorGraph()
        # G.build_rand_graph(nb_nodes=50, probability=0.95)
        # G.color_graph_rand_iter(it=100)
        # G.reset_colours()
        # G.color_graph()
        # print G.get_chromatic_number()


def main():
    p = ArgumentParser()
    p.add_argument('-i', '--it', required=True, type=int,
                   help='<Required> enter the number of iterations you want to do for each number of nodes')
    args = p.parse_args()

    find_bad_greedy_algorithm_graph(nb_it=args.it)

if __name__ == '__main__':
    main()
