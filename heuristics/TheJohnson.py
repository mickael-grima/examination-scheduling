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

from time import time
from operator import itemgetter

from model.instance import build_small_input
from inputData import examination_data

# This class implements the actual Johnson algorithm as described in the paper "Timetabling University Examinations"
class TheJohnson(object):

	def __init__(self, data):
		self.data = data
		self.n = data['n']
		self.r = data['r']
		self.p = data['p']

		# indicator variables for exam i in room k during period l
		self.x = np.int_(np.zeros((self.n,self.r,self.p)))

		# total number of still available seats in all periods (initiated by sum over all room capacities subject to opening times)
		self.period_cap = np.int_(np.zeros(self.p))
		
		# ordered list of rooms
		self.ordered_rooms = [elmts[0] for elmts in sorted(zip(range(self.r), data['c']), key=itemgetter(1), reverse=False)]

	def schedule_exams(self, gamma=0.5, n_factors=50, threshold=0):

		obj_val = np.array([sys.maxint for fac in range(n_factors)])
		optimum = np.int_(np.zeros((self.n,self.r,self.p)))
		opt_val = sys.maxint

		#set alpha
		start = -0.5
		end = 1
		alpha = list(np.linspace(start=start, stop=end, num = n_factors))

		for fac in range(n_factors):
			# reinitialize:
			# indicator variables for exam i in room k during period l
			self.x = np.int_(np.zeros((self.n,self.r,self.p)))
			# total number of still available seats in all periods (initiated by sum over all room capacities subject to opening times)
			self.period_cap = np.array([sum(np.array(data['c'])*np.array(data['T'])[:,period]) for period in range(self.p)])

			# generate exam order
			exam_order = self.generate_exam_order(alpha=alpha[fac])

			planning_failed = False			
			for exm in exam_order:
				if not self.plan_single(exam=exm, threshold=threshold):
					planning_failed = True
					break

			if planning_failed:
				# print 'factor ', alpha[fac], ' failed'
				continue
			print 'factor ', alpha[fac], ' successful'

			obj_val[fac] = self.evaluate_plan(gamma=gamma)
			if obj_val[fac] < opt_val:
				opt_val = obj_val[fac]
				optimum = self.x

		return [optimum, opt_val]


	def evaluate_plan(self, gamma=0.5):

		# compute room value
		room_val = np.sum(self.x)

		# compute time value
		# find periods for all exams
		period_of_exam = [(np.argwhere(self.x[exam,:,:]>0))[0,1] for exam in range(self.n)]
		# find mininmal distance between exam and conflicting exams (at some point I probably understood what's going on here, yet if I were to simplify this, it would probably be about 10 times the amount of code (and time))
		time_val_for_exams = np.array([np.amin([0]+[np.absolute(self.data['h'][period_of_exam[conflict_exam]]-self.data['h'][period_of_exam[exam]]) for conflict_exam in [i for i,j in enumerate(self.data['Q'][exam]) if j == 1]]) for exam in range(self.n)])
		# sum over the minima computed above
		time_val = np.sum(time_val_for_exams)

		return room_val - gamma * time_val
			


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


	def plan_single(self, exam, threshold):

		avail_sessions = []
		avail_rooms = []

		# chosen_session = -1
		chosen_rooms = []

		student_number = self.data['s'][exam]

		# find conflicts
		conflicts_for_this_exam = [i for i,j in enumerate(self.data['Q'][exam]) if j == 1]

		# identify session which can accommodate course
		for session in range(self.p):

			# if session already has an exam conflicting with this exam, then cancel
			if np.sum(self.x[conflicts_for_this_exam,:,session]) > 0:
				continue
			# if the session doesn't have enough available capacity for this exam, then cancel
			if self.period_cap[session] < self.data['s'][exam]:
				continue
			avail_sessions.append(session)

		# no available session
		if not avail_sessions:
			print 'no available session'
			return False
		# otherwise choose first available
		chosen_session = avail_sessions[0]

		# identify rooms that are not taken yet and aren't closed
		avail_rooms = [room for room in self.ordered_rooms if (np.sum(self.x[:,room,chosen_session]) == 0 and self.data['T'][room][chosen_session] == 1)]

		# no available / big enough room
		if not avail_rooms:
			print 'no available room'
			return False
		
		# otherwise find out if one of the rooms is big enough
		big_enough_rooms = [room for room in avail_rooms if self.data['c'][room] >= student_number]
		# there is one big enough
		if big_enough_rooms:
			chosen_rooms = [big_enough_rooms[0]]
		# if not, then fill biggest room, look again, and continue like that
		else:
			while not big_enough_rooms:
				if not avail_rooms:
					print 'impossible error'
					return False
				chosen_rooms.append(avail_rooms[-1]) #plan biggest available room for this exam
				avail_rooms.pop() #removes last index
				student_number = student_number - self.data['c'][chosen_rooms[-1]]
				big_enough_rooms = [room for room in avail_rooms if self.data['c'][room] >= student_number]
				# if now there is a big enough room, exit while and append it to the chosen rooms below
				# if not, continue the while loop
			chosen_rooms.append(big_enough_rooms[0])

		# update period capacity
		for chosen in chosen_rooms:
			self.period_cap[chosen_session] = self.period_cap[chosen_session] - self.data['c'][chosen]
		# plan this exam in the choosen rooms during the chosen session
		self.x[exam,chosen_rooms,chosen_session] = 1
		return True


if __name__ == '__main__':
	# n = 12
	# r = 8
	# p = 5
	# tseed = 200

	gamma = 1
	n_factors = 10
	threshold = 0

	# data = build_small_input() 
	data = examination_data.read_data(semester = "16S", threshold = threshold)
	print data['n'], data['r'], data['p']
	print n_factors, threshold
	ts = TheJohnson(data)

	t = time()

	solution = ts.schedule_exams(gamma=gamma, n_factors=n_factors, threshold=threshold)
	
	print 'Time: ', time()-t
	print 'Obj_Val: ', solution[1]
