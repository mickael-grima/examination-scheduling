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

import picos as pic
import csv
from model.base_problem import BaseProblem


class Problem(BaseProblem):
    def __init__(self):
        super(Problem, self).__init__()
        self.c = 0.5  # criteria factor
        self.available_constants = ['s', 'c', 'Q', 'T', 'h']  # every constants names have to be included in this list

    def build_dimensions(self, data):
        """ get the dimension from data
        """
        self.dimensions['n'] = data.get('n', 0)
        self.dimensions['r'] = data.get('r', 0)
        self.dimensions['p'] = data.get('p', 0)
        if not self.dimensions['n'] or not self.dimensions['r'] or not self.dimensions['p']:
            self.logger.warning("%s: at least one variable is missing" % self.__class__.__name__)
            return False
        return True

    def build_constants(self, data):
        for name in self.available_constants:
            self.constants[name] = data.get(name, {})

    def build_variables(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the variables of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        for i in range(n):
            self.vars.setdefault('x', {})
            for k in range(r):
                # exam i in room k
                self.vars['x'][i, k] = self.problem.add_variable('x[%s, %s]' % (i, k), 1, vtype='binary')
            self.vars.setdefault('y', {})
            for l in range(p):
                # exam i during period l
                self.vars['y'][i, l] = self.problem.add_variable('y[%s, %s]' % (i, l), 1, vtype='binary')
            self.vars.setdefault('z', {})
            for j in range(i + 1, n):
                self.vars['z'][i, j] = self.problem.add_variable('z[%s, %s]' % (i, j), 1, vtype='integer')

    def build_constraints(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the variables of the problem from the data
        """
        n, r, p = self.dimensions['n'], self.dimensions['r'], self.dimensions['p']
        for i in range(n):
            # Each exam i is scheduled on exactly one period
            constraint = (pic.sum([self.vars['y'][i, l] for l in range(p)]) == 1)
            self.problem.add_constraint(constraint)
            # enough seats for each student for exam i
            constraint = (
                pic.sum([self.vars['x'][i, k] * self.constants['c'][k] for k in range(r)]) >=
                self.constants['s'][i]
            )
            self.problem.add_constraint(constraint)
            # No conflicts
            for l in range(p):
                constrant = (
                    pic.sum([self.vars['y'][j, l] * self.constants['Q'][i][j] for j in range(n) if j != i]) <=
                    (1 - self.vars['y'][i, l]) * n
                )
                self.problem.add_constraint(constrant)
            for k in range(r):
                for l in range(p):
                    if self.constants['T'][k][l] == 0:
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

    def build_objectif(self):
        """ @param n, r, p: number of exams, rooms and periods
            Build the constants of the problem from the data
        """
        n, r = self.dimensions['n'], self.dimensions['r']
        crit = (
            self.c * pic.sum([self.vars['x'][i, k] * self.constants['s'][i] for i in range(n) for k in range(r)]) -
            pic.sum([self.vars['z'][i, j] for i in range(n) for j in range(i + 1, n)])
        )
        self.problem.set_objective('min', crit)

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
                        colnum += 1
                        pass
