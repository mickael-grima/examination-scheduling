#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script describe an instance of the examination problem.
# We find here classes and methods to load the data to this class

import logging


class Instance(object):
    def __init__(self, logger=None):
        self.logger = logger or logging  # To save the logs

    def build_from_data_file(self, source):
        """ @ param source: the location of the file to read, as a string
            @ return: 1 if success, 0 otherwise
        """
        try:
            with open(source, 'r') as src:
                # TODO instancie the parameters of the class from the data
                pass
        except Exception as e:
            # If an error occurs we send an exception
            self.logger.exception("%s: Build class parameters from data file failed: %s"
                                  % (self.__class__.__name__, repr(e)))
            return 0
        return 1

    def sketch(self):
        # Write here a code to visualize the data
        pass
