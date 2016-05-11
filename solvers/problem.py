#!/usr/bin/env python
# -*- coding: utf-8 -*-

import picos as pic
import logging
import csv


class Constants(dict):
    """ Contain all the constants concerning our problem
    """
    def __init__(self, nb_exams=0, nb_rooms=0, nb_periods=0):
        super(Constants, self).__init__()
        self.n = nb_exams  # number of exams
        self.r = nb_rooms  # number of rooms
        self.p = nb_periods  # number of periods

        # Constants of our problems
        self.s = {i: 0 for i in range(self.n)}  # Number of students per exam
        self.c = {k: 0 for k in range(self.r)}  # Number of seats per room
        # 1 if exam i and j has a conflict (One student does both exams)
        self.Q = {(i, j): 0 for i in range(self.n) for j in range(self.n)}
        self.T = {(k, l): 0 for k in range(self.r) for l in range(self.p)}  # 1 if room k is open during period l
        self.h = {l: 0 for l in range(self.p)}  # Number of hours from the beginning to the starting of period l

        self.logger = logging

    def __getitem__(self, key):
        res = None
        exec("res = self.%s" % key)
        return res

    def add_constant(self, name, rank, value):
        """ @param name: name of the constant. e.g.: 'Q', 'h', 's', ...
            @param rank: indexes
            @param value: value of the constant name for the given rank
        """
        const = None
        try:
            exec("const = self.%s" % name)
        except Exception as e:
            self.logger.exception(repr(e))
            return False
        if const.get(rank) is None:
            self.logger.exception("%s: rank %s for constant %s doesn't exist"
                                  % (self.__class__.__name__, repr(rank), repr(name)))
            return False
        else:
            const[rank] = value
            return True

    def add_set_of_constants(self, name, data):
        """ @param name: name of the constant. e.g.: 'Q', 'h', 's', ...
            @param data: dictionnary that represents the value of the constant name
            We just verify that the given rank are the right one
        """
        if name == 's':
            for i in range(self.n):
                try:
                    self.s[i] = data[i]
                except:
                    self.logger.exception("%s: range %s doesn't exist for constant %s"
                                          % (self.__class__.__name__, i, name))
        elif name == 'c':
            for k in range(self.r):
                try:
                    self.c[k] = data[k]
                except:
                    self.logger.exception("%s: range %s doesn't exist for constant %s"
                                          % (self.__class__.__name__, k, name))
        elif name == 'Q':
            for i in range(self.n):
                for j in range(self.n):
                    try:
                        self.Q[i, j] = data[i][j]
                    except:
                        self.logger.exception("%s: range %s doesn't exist for constant %s"
                                              % (self.__class__.__name__, repr((i, j)), name))
        elif name == 'T':
            for k in range(self.r):
                for l in range(self.p):
                    try:
                        self.T[k, l] = data[k][l]
                    except:
                        self.logger.exception("%s: range %s doesn't exist for constant %s"
                                              % (self.__class__.__name__, repr((k, l)), name))
        elif name == 'h':
            for l in range(self.p):
                try:
                    self.h[l] = data[l]
                except:
                    self.logger.exception("%s: range %s doesn't exist for constant %s"
                                          % (self.__class__.__name__, l, name))


class Problem(object):
    def __init__(self):
        self.problem = pic.Problem()
        self.constants = None  # Constants
        self.vars = {'x': {}, 'y': {}, 'z': {}}  # variables
        self.c = 0.5  # criteria factor

        self.available_constants = ['s', 'c', 'Q', 'T', 'h']  # every constants names have to be included in this list
        self.logger = logging

    def build_problem(self, data):
        """ @param data: contains the constants: 'Q', 's', ...
            the constants are representing as a dictionnary
        """
        # First extract the dimension problems: n, r and p
        n = data.get('n', 0)
        r = data.get('r', 0)
        p = data.get('p', 0)
        if n * r * p == 0:
            self.logger.warning("%s: at least one variable is missing" % self.__class__.__name__)
            return False

        # ----------- CONSTANTS -------------
        self.constants = Constants(n, r, p)
        for name in self.available_constants:
            self.constants.add_set_of_constants(name, data.get(name, {}))

        # ----------- VARIABLES -------------
        for i in range(n):
            for k in range(r):
                # exam i in room k
                self.vars['x'][i, k] = self.problem.add_variable('x[%s, %s]' % (i, k), 1, vtype='binary')
            for l in range(p):
                # exam i during period l
                self.vars['y'][i, l] = self.problem.add_variable('y[%s, %s]' % (i, l), 1, vtype='binary')
            for j in range(i + 1, n):
                self.vars['z'][i, j] = self.problem.add_variable('z[%s, %s]' % (i, j), 1, vtype='integer')

        # ----------- CONSTRAINTS -------------
        for i in range(n):
            # Each exam i is scheduled on exactly one period
            constraint = (pic.sum([self.vars['y'][i, l] for l in range(p)]) <= 1)
            self.problem.add_constraint(constraint)
            # enough seats for each student for exam i
            constraint = (pic.sum([self.vars['x'][i, k] * self.constants['c'][k]]) >= self.constants['s'][i])
            self.problem.add_constraint(constraint)
            # No conflicts
            for l in range(p):
                constrant = (pic.sum([self.vars['y'][j, l] for j in range(i + 1, n)]) <= (1 - self.vars['y'][i, l]) * n)
                self.problem.add_constraint(constrant)
            for k in range(r):
                for l in range(p):
                    if not self.constants['T'][k, l]:
                        # We use room k if and only if the room is open
                        constraint = (self.vars['x'][i, k] + self.vars['y'][i, l] <= 1)
                        self.problem.add_constraint(constraint)
            for j in range(i + 1, n):
                for k in range(r):
                    for l in range(p):
                        # One room k can have only exam for a given period l
                        constraint = (
                            self.vars['x'][j, k] + self.vars['y'][j, l] <=
                            3 - self.vars['x'][i, k] - self.vars['y'][i, l]
                        )
                        self.problem.add_constraint(constraint)
                # Criteria constraint for 'z'
                constraint = (
                    self.vars['z'][i, j] >= pic.sum([self.vars['y'][i, l] * self.constants['h'][l] for l in range(p)]) -
                    pic.sum([self.vars['y'][j, l] * self.constants['h'][l] for l in range(p)])
                )
                self.problem.add_constraint(constraint)
                constraint = (
                    self.vars['z'][i, j] >= pic.sum([self.vars['y'][j, l] * self.constants['h'][l] for l in range(p)]) -
                    pic.sum([self.vars['y'][i, l] * self.constants['h'][l] for l in range(p)])
                )
                self.problem.add_constraint(constraint)

        # ----------- CRITERIA -------------
        crit = (
            self.c * pic.sum([self.vars['x'][i, k] * self.constants['s'][i] for i in range(n) for k in range(r)]) -
            pic.sum([self.vars['z'][i, j] for i in range(n) for j in range(i + 1, n)])
        )
        self.problem.set_objective('min', crit)

    def solve(self):
        """ Solve the problem
        """
        self.problem.solve()

    def build_from_csv(self, input_file):
        """ load the data from input_file, build the data dictionnary and build the problem
        """
        with open(input_file, "rb") as src:
            reader = csv.reader(src)
            data = {}
            first, header = True, []
            for row in reader:
                # Save header row.
                if first:
                    header = row
                    first = False
                    for col in header:
                        data.setdefault(data, {})
                else:
                    colnum = 0
                    for col in row:
                        # TODO
                        pass
