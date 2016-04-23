#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Here is the class Graphicer, that should be used for any visulalization problem

import logging


class Graphicer(object):
	def __init__(self, logger=None):
		self.logger = logger or logging  # Save here the logs

	def draw_bar_graph(self):
		""" draw a bar graph
		"""
		pass

	def draw_pie_chart(self):
		""" draw here a pie chart
		"""
		pass
