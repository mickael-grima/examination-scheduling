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
import numpy as np
import time

from operator import itemgetter

from model.instance import build_small_input

# This class implements the actual Johnson algorithm as described in the paper "Timetabling University Examinations"
class TheJohnson(object):

	def schedule_exams(self, n_factors=50):

		#set alpha
		start = 0
		end = 0.5
		alpha = list(np.linspace(start=start, stop=end, num = n_factors))

		for fac in range(n_factors):
			#generate exam order
			exam_order = self.generate_exam_order(alpha=alpha[fac])
			print exam_order

		#TODO

	def __init__(self, data):
		self.data = data
		self.n = data['n']
		self.r = data['r']
		self.p = data['p']
		self.x = np.int_(np.zeros((self.n,self.r,self.p)))

	def generate_exam_order(self, alpha):

		conflicts = self.data['conflicts']

		# compute number of conflicts for all exams
		conf_num = np.zeros(self.n)
		# Assumes symmetric conflict data
		for i in range(self.n):
			conf_num[i] = len(conflicts[i])

		# build difficulty factor
		z = np.array(self.data['s'])*alpha + conf_num

		# sort nodes by difficulty factor
		return [elmts[0] for elmts in sorted(zip(np.arange(self.n), z), key=itemgetter(1), reverse=True)]


	# def plan_single():
	# 	pass


if __name__ == '__main__':

	# n = 12
	# r = 8
	# p = 5
	# tseed = 200

	n_factors = 10

	data = build_small_input() 
	ts = TheJohnson(data)

	schedule = ts.schedule_exams(n_factors=n_factors)