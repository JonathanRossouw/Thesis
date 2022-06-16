#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
black_rhino is a multi-agent simulator for financial network analysis
Copyright (C) 2012 Co-Pierre Georg (co-pierre.georg@keble.ox.ac.uk)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import logging
# ============================================================================
#
# class br-generate-measurements
#
# ============================================================================
class Generate_Measurements:


	#
    #
    # VARIABLES
    #
    #

    # numAgents = ""  # Number of Agents
    # fileName = ""  # Directory for Measurement File
    #
    #
    # CODE
    #
    #


	# -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
	def __init__(self):
		# Create empty lists of agent identifiers
		self.numAgents = 0
		# Create empty class variable for measurement xml files 
		self.measurementfileName = ""
	# -------------------------------------------------------------------------

	# -------------------------------------------------------------------------
    # generate_general_measurements
	# append xml files for general non agent related measurements
    # -------------------------------------------------------------------------
	def generate_measurements(self, accounts_measured, measurementfileName):
		# Read in number of agents and name of directory to store measurements
		self.measurementfileName = measurementfileName
		# Loop through number of agents and create xml files
		measurementfileName = self.measurementfileName + ".xml"
		outFile = open(measurementfileName,  'w')
		text = "<?xml version='1.0' encoding='UTF-8'?>\n"
		text = text + "<measurement identifier='" + "test_measurements" + "'>\n"
		text = text + "    <parameter type='filename' value='measurements/" + "Test_Output" + ".csv'></parameter>\n"
		text = text + "    <parameter type='output' column='1' header='Step' value='current_step'></parameter>\n"
		count = 1
		for item in accounts_measured:	
			count += 1
			text = text + "    <parameter type='output' column='" + str(count) + "' header='" + item + "' value='" + item + "' ></parameter>\n"
		text = text + "</measurement>"
		outFile.write(text)
		outFile.close()	
	# -------------------------------------------------------------------------