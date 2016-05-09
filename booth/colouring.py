#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import random as rd
import glob
from time import time, strftime
import pickle as pk
from argparse import ArgumentParser
from copy import deepcopy
import gtk

import matplotlib
matplotlib.use('Agg')  # for not popping up windows
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

all_colours = ["#00B1EB", "#E51C39", "#FCEA10", "green", "red", "yellow", "cyan", "orange",
               "blue", "grey", "purple", "pink", "black"]
m = len(all_colours)

plt.axis('off')


def get_screen_size():
    """ return a tuple with the width and the length of the screen siye in inches
    """
    screen = gtk.Window().get_screen()
    resolution = screen.get_resolution()
    size = (screen.get_width(), screen.get_height())
    return size[0] / resolution, size[1] / resolution


class ColorGraph(object):
    def __init__(self):
        self.DIRECTORY = "%sbooth/plots/" % PROJECT_PATH
        self.plotname = "graphcolouring"
        self.ALL_COLOURS = [str(i) for i in range(20)]

        self.graph = nx.Graph()
        self.colours = {}
        self.revert = True
        self.history = {}

        if not os.path.exists(self.DIRECTORY):
            os.makedirs(self.DIRECTORY)

    def add_node(self, node):
        """ @param node: node
        Add node to self.graph
        """
        self.graph.add_node(node)
        self.colours.setdefault(node, 'white')

    def add_edge(self, node1, node2):
        self.graph.add_edge(node1, node2)
        self.colours.setdefault(node1, 'white')
        self.colours.setdefault(node2, 'white')

    def reset_history(self):
        """ reinitialized self.history to an empty dictionnary
        """
        self.history = {}

    def reset_colours(self):
        """ Reset all the colours to white
        """
        for col in self.colours:
            self.colours[col] = 'white'

    def reset(self):
        """ do both reset_colours and reset_history
        """
        self.reset_colours()
        self.reset_history()

    def reinitialize(self):
        """ reinitialize everything
        """
        self.reset()
        self.graph = nx.Graph()

    def update_color(self, node, color):
        """ @param node: node to consider in self.graph
            @param color: color to set to this node
            Set color to node in self.colours
        """
        if self.colours.get(node) is None:
            return False
        self.colours[node] = color
        return True

    def plot_history(self, save=True):
        for step in self.history:
            self.colours = self.history[step]
            self.draw(save=save, ind=step)

    def get_degree(self):
        """ return a dictionnary {node: degree}
        """
        degree = {node: len(self.graph.neighbors(node)) for node in self.graph.nodes()}
        return degree

    def get_chromatic_number(self):
        """ return the number of colours used
        """
        return len(set([self.colours[x] for x in self.colours]))

    def get_max_ind_set(self):
        """ for the given colouring give the maximum independant set size
        """
        cols = {colour: len([node for node in self.graph.nodes() if self.colours[node] == colour])
                for colour in set([col for _, col in self.colours.iteritems()])}
        return max([value for _, value in cols.iteritems()])

    def get_schedule_plan(self):
        """ Return a dictionnary of dependencies for each node
            e.g.: {1: [2, 3], 2: [1,4], 3: [1], 4: [2], 5: []}
        """
        schedule_plan = {}
        for edge in self.graph.edges():
            schedule_plan.setdefault(edge[0], {})
            schedule_plan[edge[0]].setdefault('S%s' % edge[0], edge[1])
            schedule_plan.setdefault(edge[1], {})
            schedule_plan[edge[1]].setdefault('S%s' % edge[1], edge[0])
        return schedule_plan

    def check_neighbours(self, node, colour):
        """ @param node: node to consider
            @param colour: colour to check
            We check for every neighbor of node if it has colour as colour
            If not we return true, else we return false
        """
        if colour in [self.colours[x[1]] for x in self.graph.edges(node)]:
            return(False)
        return(True)

    def get_history_node_ordered(self):
        """ Give the list of node sorted such that first node was coloured first, ans so on
        """
        res = []
        for step, history in self.history.iteritems():
            for node, colour in history.iteritems():
                if colour != 'white' and node not in res:
                    res.append(node)
        return res

    def draw(self, save=False, with_labels=False, ind=0, ax=None, clf=False, colours=None, pos={}):
        """ @param save: do we save the picture
            @param with_labels: do we write the labels of the nodes on the picture
            @param ind: index of the picture
            @param ax: if we have an ax we draw on it
            @param clf: after saving we clean the figure if clf==True
            Draw the graph with the self.colours and save it if save==true
        """
        cols = [colour for _, colour in colours.iteritems()] or [colour for _, colour in self.colours.iteritems()]
        nx.draw(self.graph, pos, node_color=cols, with_labels=with_labels, ax=ax, node_size=1500,
                labels={node: "P%s" % node for node in self.graph.nodes()}, font_size=16)
        if save:
            filename = self.DIRECTORY + self.plotname
            if(ind < 10):
                filename = filename + '00'
            elif(ind < 100):
                filename = filename + '0'
            plt.savefig("%s%s.jpg" % (filename, ind))
        if clf:
            plt.clf()

    def draw_calendar(self, save=False, with_labels=False, ind=0, clf=False, ax=None, colours=None):
        """ @param save: do we save the picture?
            @param with_labels: Do we add labels of the node on the picture?
            @param ind: index of the picture
            @param clf: after saving we clean the figure if clf==True
            We draw the graph as a calendar: each color has a given x coordinate
            We save it if save==True
        """
        # How many nodes with a given color did we already draw
        periods = ['9:00', '11:00', '13:00', '15:00', '17:00', '19:00', '21:00', '23:00']
        periods_places = [i * 80 for i in range(len(periods))]
        counter_colors = {color: 0 for color in all_colours}
        cols = colours or self.colours
        if ax is None:
            fig, ax = plt.subplot()
        xticklabels, yticklabels = {}, {}
        node_list = self.get_history_node_ordered()
        for node in node_list:
            # The indice of the colour given to node in all_colours
            color_ind = [i for i in range(len(all_colours)) if all_colours[i] == cols[node]]
            if color_ind:
                color_ind = color_ind[0]
            else:
                continue
            xticklabels.setdefault(counter_colors[self.colours[node]] * 50 + 20,
                                   'Raum %s' % (counter_colors[self.colours[node]] + 1))
            ax.bar(counter_colors[self.colours[node]] * 50, 80, bottom=color_ind * 120, width=40,
                   color=cols[node])
            counter_colors[cols[node]] += 1
            # Add text labels
            if with_labels:
                ax.text(counter_colors[self.colours[node]] * 50 - 15, color_ind * 120 + 40, 'P%s' % node,
                        ha='right', fontsize=16)
        nb_yticklabels = int(len(set(self.colours.itervalues())) * 120 / 80.) + 1
        yticklabels = {periods_places[i]: periods[i] for i in range(nb_yticklabels)}
        # Axis parameters
        ax.set_title('Kalendar')
        ax.set_xticks(list(xticklabels.iterkeys()))
        ax.set_xticklabels(list(xticklabels.itervalues()), fontsize=12)
        ax.set_yticks(list(yticklabels.iterkeys()))
        ax.set_yticklabels(list(yticklabels.itervalues()), fontsize=12)
        ax.axes.xaxis.set_label('Räume')
        ax.axes.yaxis.set_label('Perioden')
        if save:
            filename = '%scalendar-%s-' % (self.DIRECTORY, strftime("%Y%m%d"))
            if(ind < 10):
                filename = filename + '00'
            elif(ind < 100):
                filename = filename + '0'
            plt.savefig("%s%s.jpg" % (filename, ind))
        if clf:
            plt.clf()

    def draw_schedule_plan(self, ind=0):
        """ From the graph create a schedule plan like the poster
        """
        schedule_plan = self.get_schedule_plan()
        text = '   | %s \n' % ' | '.join(['S%s' % node for node in self.graph.nodes()])
        for node, dependencies in schedule_plan.iteritems():
            tab = ['P%s' % node]
            for nod in self.graph.nodes():
                if node in schedule_plan[nod]:
                    tab.append('x')
                else:
                    tab.append(' ')
            text += ' %s \n' % ' | '.join(tab)
        filename = '%sschedule-plan-%s-' % (self.DIRECTORY, strftime("%Y%m%d"))
        if(ind < 10):
            filename = filename + '00'
        elif(ind < 100):
            filename = filename + '0'
        filename += "%s.txt" % ind
        with open(filename, 'wb') as src:
            src.write(text)

    def draw_simulation(self, save=True, name='', clf=True, axarr=None, line=0):
        """ @param save: do we save the picture?
            @param name: name of the picture
            @param clf: after saving we clean the figure if clf==True
            @param axarr: list of axes where to plot
            @param line: line of the axarr where to plot
            Draw for both heuristics and exact solution the calendar and the graph
        """
        if axarr is None:
            fig, axarr = plt.subplots(1, 2)
            line = 0
        self.draw(save=False, ind=name, clf=clf, ax=axarr[line, 0])
        self.draw_calendar(save=False, ind=name, clf=clf, ax=axarr[line, 1])
        if save:
            filename = '%ssimulation-%s-%s.jpg' % (self.DIRECTORY, strftime("%Y%m%d"), name)
            plt.savefig(filename)

    def draw_heuristics_and_exact(self, directory, save=False, with_labels=False, pos={}):
        """ @param dir: the directory where to save the files
            We draw together the heuristics and exact solution (calendar and graph) in the same plot
        """
        # We copy the graph and let run the heuristic
        graph_heur = deepcopy(self)
        graph_heur.reset()
        graph_heur.color_graph()
        width = max(graph_heur.get_max_ind_set(), self.get_max_ind_set()) * 50
        height = max(graph_heur.get_chromatic_number(), self.get_chromatic_number()) * 100

        # for each step of the history we save a file in dir
        steps = list(set(self.history.iterkeys()).union(set(graph_heur.history.iterkeys())))
        steps.sort()
        screen_size = get_screen_size()
        for step in steps:
            fig, axarr = plt.subplots(2, 2, figsize=screen_size)
            axarr[0, 1].set_xlim(0, width)
            axarr[0, 1].set_ylim(height, 0)
            axarr[1, 1].set_xlim(0, width)
            axarr[1, 1].set_ylim(height, 0)
            self.draw(save=False, clf=False, ax=axarr[0, 0],
                      colours=self.history.get(step), with_labels=with_labels, pos=pos)
            self.draw_calendar(save=False, clf=False, ax=axarr[0, 1],
                               colours=self.history.get(step), with_labels=with_labels)
            graph_heur.draw(save=False, clf=False, ax=axarr[1, 0],
                            colours=graph_heur.history.get(step), with_labels=with_labels, pos=pos)
            graph_heur.draw_calendar(save=False, clf=False, ax=axarr[1, 1],
                                     colours=graph_heur.history.get(step), with_labels=with_labels)
            if not os.path.exists(directory):
                os.makedirs(directory)
            ind = '%s' % step
            if len(ind) == 1:
                ind = '0%s' % ind
            if save:
                plt.savefig('%ssimulation-%s.jpg' % (directory, ind))
            plt.clf()

    def get_calendar_simulation_files(self, save=False):
        """ @param history: dictionnary of key: value. key = step, value = list of colours
            if save,we save the different steps in self.DIRECTORY
        """
        for step, colours in self.history.iteritems():
            self.colours = colours
            self.draw_calendar(save=True, ind=step)

    def build_rand_graph(self, nb_nodes=16, probability=0.5):
        """ @param nb_nodes: number of nodes of the constructed graph
            @param probability: the ratio of edge we want in expectation
            We build a graph with exactly nb_nodes and approximately #possible_edges*probability
        """
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
        """ @param nb_nodes: number of cases in sudoku
            We create a graph representing a sudoku: each node is a case and an edge represent the fact that
            two nodes are neighbor in the sudoku
        """
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
        self.add_edge(0 * 4 + 2, (1) * 4 + 3)
        self.add_edge(1 * 4 + 2, (0) * 4 + 3)
        self.add_edge(2 * 4, (3) * 4 + 1)
        self.add_edge(3 * 4, (2) * 4 + 1)
        self.add_edge(2 * 4 + 2, (3) * 4 + 3)
        self.add_edge(3 * 4 + 2, (2) * 4 + 3)

    def color_node(self, node):
        """ Check the colors of the neighbors, and color the node with a different color
        """
        for col in all_colours:
            if self.check_neighbours(node, col):
                self.colours[node] = col
                break

    def color_graph(self):
        """ @param save: do we save the sequence?
            We solve the colouring graph problem with a greedy algorithm
            We take the node from the biggest degree to the lowest and we color them to have no conflict
            We try to have as little colours as possible
        """
        degree = self.get_degree()

        # sort by degree
        sl = sorted([(dg, node) for node, dg in degree.iteritems()])
        lookup_order = [x[1] for x in sl]
        if self.revert:
            lookup_order = reversed(lookup_order)

        # Save the state
        self.history[0] = deepcopy(self.colours)

        counter = 1
        for node in lookup_order:

            # respect initial condition
            if self.colours[node] != 'white':
                continue

            self.color_node(node)

            # Save the state
            self.history[counter] = deepcopy(self.colours)

            counter += 1

        return self.colours

    def color_graph_rand(self):
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

        # Save the state
        self.history[0] = deepcopy(self.colours)

        counter = 1
        while lookup_order:
            rand, n, ind = rd.randint(0, sum(degree)), 0, 0
            while ind < len(degree):
                n += degree[ind]
                if n >= rand:
                    break
                ind += 1
            node = lookup_order[ind]
            self.color_node(node)
            # Save the state
            self.history[counter] = deepcopy(self.colours)

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
        colours, history, min_chromatic_number = {}, {}, []
        for i in range(it):
            self.reset()
            cols = deepcopy(self.color_graph_rand())
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
            history = deepcopy(self.history)
        self.colours = colours
        self.history = history
        return colours

    def color_backtracking_rec(self, node, colours={}, history={}, step=0):
        """ Intermediate step of the backtracking algorithm
        """
        cols = deepcopy(colours)
        hist = deepcopy(history)

        self.color_node(node)
        cols[node] = self.colours[node]
        hist[step] = deepcopy(self.colours)
        white_nodes = [node for node, colour in colours.iteritems() if colour == 'white']
        if len(white_nodes) == 0:
            return colours, {step: colours}
        for nod in white_nodes:
            cs, hst = self.color_backtracking_rec(nod, colours=colours, step=step + 1)
            if len(set([colour for colour in cs.iteritems()])) < len(set([colour for colour in cols.iteritems()])):
                cols, hist = cs, hst
        self.colours[node] = 'white'
        del self.history[step]

        return cols, hist

    def color_backtracking(self):
        """ We color the graph thanks to a backtracking algorithm
        """
        # First reset the graph
        self.reset()
        colours, history = {}, {}
        for node in self.graph.nodes():
            self.color_backtracking_rec(node, colours=colours, history=history, step=0)
            if not colours or self.get_chromatic_number() < len(set([colour for _, colour in colours.iteritems()])):
                colours = deepcopy(self.colours)
                history = deepcopy(self.history)
            self.reset()
        self.colours = colours
        self.history = history


def create_alex_graph(special_edge=False):
    # Build the Graph
    G = ColorGraph()
    for i in range(9):
        G.graph.add_node(i)
    G.graph.add_edge(0, 1)
    G.graph.add_edge(0, 2)
    G.graph.add_edge(0, 3)
    G.graph.add_edge(0, 6)
    G.graph.add_edge(2, 4)
    G.graph.add_edge(3, 5)
    G.graph.add_edge(4, 8)
    G.graph.add_edge(5, 8)
    G.graph.add_edge(6, 7)
    G.graph.add_edge(7, 8)
    if special_edge:
        G.graph.add_edge(2, 5)
    G.colours = {node: 'white' for node in G.graph.nodes()}

    # Build the position
    pos = {
        0: (0, 1),
        1: (0, 0),
        2: (1, 2),
        3: (0, 3),
        4: (2, 2),
        5: (3, 3),
        6: (2, 0),
        7: (3, 0),
        8: (3, 1)
    }

    G.color_graph()
    print G.get_chromatic_number()
    G.reset()
    G.color_graph_rand_iter(it=20)
    print G.get_chromatic_number()

    G.draw_heuristics_and_exact('%sbooth/alex/plots/' % PROJECT_PATH, save=True, with_labels=True, pos=pos)

    os.system("convert -delay 200 -loop 0 %s/booth/alex/plots/simulation-*.jpg %s/booth/alex/gif/animated.gif"
              % (PROJECT_PATH, PROJECT_PATH))


def find_bad_greedy_algorithm_graph(nb_it=50, min_colour=0):
    """ @param nb_it: for each number of nodes we do nb_ititerations
        @param min_colour: how many colours we want at least
        We try to construct a graph with a specific number of nodes (all nodes between 5 and 20)
        where the greedy algorithm is as bad as possible
    """
    graphs = {}  # key = nb_node, value = graph
    node_min, node_max = 5, 20
    print "----------- Start creating graphs ---------------"
    t = time()
    for n in range(node_min, node_max + 1):
        diff = 0
        print "Number of nodes: %s" % n
        for it in range(nb_it):
            G = ColorGraph()
            G.build_rand_graph(nb_nodes=n, probability=0.3)
            # greedy algorithm
            G.color_graph()
            n_greedy = G.get_chromatic_number()
            # rand algorithm
            G.reset()
            G.color_graph_rand_iter(it=20)
            n_rand = G.get_chromatic_number()
            # We compare the solutions
            delta_n = n_greedy - n_rand
            if delta_n > diff and min(n_greedy, n_rand) >= min_colour:
                diff = delta_n
                graphs[n] = (G, diff)
    print "Job completed after %s sec" % (time() - t)
    print "----------- Done ---------------"
    pk.dump(graphs, open('%sbooth/files/relevant_graphs' % PROJECT_PATH, 'wb'))
    return graphs


def generate_plots_from_file():
    """
        We load the pickle file and we generate the plot for heuristics, exact solution, both calendar
        and graph, and the schedule plan
    """
    print "-------- Start generating plots ---------------"
    graphs = pk.load(open('%s/booth/files/relevant_graphs' % PROJECT_PATH, 'rb'))
    for nb_nodes, graph in graphs.iteritems():
        fig, axarr = plt.subplots(2, 2)
        if PROJECT_PATH not in graph[0].DIRECTORY:
            graph[0].DIRECTORY = '%sbooth/%s' % (PROJECT_PATH, graph[0].DIRECTORY)
        graph[0].draw_simulation(save=False, name='exact-simulation-%s' % nb_nodes, clf=False, axarr=axarr, line=0)
        graph[0].reset_colours()
        graph[0].color_graph()
        graph[0].draw_simulation(save=False, name='heuristics-simulation-%s' % nb_nodes, clf=False, axarr=axarr, line=1)
        filename = '%ssimulation-%s.jpg' % (graph[0].DIRECTORY, nb_nodes)
        plt.savefig(filename)
        print "Plot simulation-%s.jpg saved" % nb_nodes
        plt.clf()
    print "------------- Done -------------"


def generate_plot_simulation_from_file():
    """
        We load the pickle file and we generate the plot for heuristics, exact solution, both calendar
        and graph, for all step of the resolution
    """
    print "-------- Start generating plots ---------------"
    graphs = pk.load(open('%s/booth/files/relevant_graphs' % PROJECT_PATH, 'rb'))
    for nb_nodes, graph in graphs.iteritems():
        pos = nx.spring_layout(graph[0].graph)
        graph[0].draw_heuristics_and_exact('%sbooth/plots/%s/' % (PROJECT_PATH, nb_nodes), save=True,
                                           with_labels=True, pos=pos)
        print "Plots directory %s/ created" % nb_nodes
    print "---------- Done -------------"


def generate_gif_from_plots():
    """ After having generated the jpg files, we generate the gif file in plots/gif/
    """
    print "-------- Start creating gif ---------------"
    plots_directory = '%sbooth/' % PROJECT_PATH
    if os.path.exists(plots_directory):
        if not os.path.exists("%sgif/" % plots_directory):
            os.makedirs("%sgif/" % plots_directory)
        for subdir, dirs, files in os.walk(plots_directory):
            st = subdir.split('/')
            if len(st) > 1 and st[-2] == 'plots' and st[-1] not in ['gif', '']:
                name = st[-1]
                print "creating gif simulation-%s.gif" % name
                os.system("convert -delay 200 -loop 0 %splots/%s/simulation-*.jpg %s/gif/simulation-%s.gif"
                          % (plots_directory, name, plots_directory, name))
    print "------------- Done -------------"


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
    p.add_argument('-n', '--new', default=False, type=bool,
                   help='<Default: False> Do we generate new graphs?')
    args = p.parse_args()

    os.system("rm -rf %sbooth/plots/" % PROJECT_PATH)
    os.system("rm -rf %sbooth/gif/" % PROJECT_PATH)
    os.makedirs("%sbooth/plots/" % PROJECT_PATH)
    os.makedirs("%sbooth/gif/" % PROJECT_PATH)
    if not os.path.exists("%sbooth/files/relevant_graphs" % PROJECT_PATH) or args.new:
        find_bad_greedy_algorithm_graph(nb_it=args.it, min_colour=3)
    generate_plot_simulation_from_file()
    generate_gif_from_plots()

if __name__ == '__main__':
    # main()
    create_alex_graph()
