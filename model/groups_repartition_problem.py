#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base_problem import BaseProblem
import gurobipy as gb


class GroupsRepartitionProblem(BaseProblem):
    def __init__(self, data, gamma=1.0, name="GroupsRepartitionProblem"):
        super(GroupsRepartitionProblem, self).__init__(name=name)
        self.gamma = gamma

        self.build_problem(data)

    def build_dimensions(self, data):
        self.dimensions['c'] = data.get('c', 0)
        self.dimensions['p'] = data.get('p', 0)
        return True

    def build_constants(self, data):
        self.constants['v'] = data.get('v', [])
        self.constants['h'] = data.get('h', [])
        self.constants['conflicts'] = data.get('conflicts', {})
        return True

    def build_variables(self):
        self.vars['x'] = {}
        for i in range(self.dimensions['c']):
            for l in self.constants['available']:
                # x[i, l] = 1 if group i is schedule in timeslot l
                self.vars['x'][i, l] = self.problem.addVar(vtype=gb.GRB.BINARY, name='x[%s, %s]' % (i, l))
        return True

    def build_constraints(self):
        for l in self.dimensions['p']:
            # Avoid conflicts between groups
            self.problem.addConstr(gb.quicksum([self.vars['x'][i, l] for i in range(self.dimensions['c']) if l in self.constants['available'][i]]) <= 1)
        for i in range(self.dimensions['c']):
            # each group has to have at least one time slot
            self.problem.addConstr(gb.quicksum([self.vars['x'][i, l] for l in range(self.dimensions['p'])]) >= 1)
        return True

    def build_objectif(self):
        c, p = self.dimensions['c'], self.dimensions['p']
        h, Q = self.constants['h'], self.constants['conflicts']
        obj_room = gb.quicksum(self.vars['x'].itervalues())
        dist = {(i, j): Q.get((i, j), 0) * gb.quicksum(h[l] * (self.vars['x'][i, l] - self.vars['x'][j, l]) for l in self.constants['available'][i])
                for i in range(c) for j in range(c)}
        obj = self.gamma * gb.quicksum([dist[i, j] * dist[i, j] for i in range(c) for j in range(c)]) - obj_room
        self.problem.setObjective(obj, gb.GRB.MAXIMIZE)
        return True
