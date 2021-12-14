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
# class br-generate-households 
#
# ============================================================================
class Generate_Agents:


	#
    #
    # VARIABLES
    #
    #

    # numHouseholds = ""  # Number of Households
	# numBanks = "" # Number of Banks
    # fileName = ""  # Directory for generate banks
    #
    #
    # CODE
    #
    #


	# -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
	def __init__(self):
		self.numHouseholds = 0
		self.numBanks = 0
		self.numFirms = 0
		self.householdfileName = ""
		self.bankfileName = ""
	# -------------------------------------------------------------------------


	# -------------------------------------------------------------------------
    # generate_households
	# read in number of households and banks from parameter_values
	# generate xml files for households each randomly assigned to a bank
    # -------------------------------------------------------------------------
	def generate_households(self, numHouseholds, householdfileName):
		import numpy as np
		# Read in number of households, number of banks, and name of directory to store households
		self.numHouseholds = int(numHouseholds)
		self.householdfileName = householdfileName
		# Loop through number of households and create xml files
		for i in range(self.numHouseholds):
			identifier = "household_" + str(i)
			householdfileName = self.householdfileName + identifier
			# the following code ensures leading zeros so filenames will be in the right order
			# for python to read in. Also, bank names are sorted properly in activeBanks of madfimas
			# this code is ugly, but works...
			labour = round((4000 * np.random.lognormal(0, 0.4, 1))[0], 3)
			householdfileName += ".xml"
			outFile = open(householdfileName,  'w')
			text = "<?xml version='1.0' encoding='UTF-8'?>\n"
			text = text + "<household identifier= '" + identifier + "'>\n"
			text = text + "    <parameter name='equity' value='" + str(labour) + "'></parameter>\n"
			text = text + "    <parameter name='labour' value='" + str(labour) + "'></parameter>\n"
			text = text + "    <parameter name='propensity_to_save' value='0.4'></parameter>\n"
			text = text + "</household>\n"
			outFile.write(text)
			outFile.close()
	# -------------------------------------------------------------------------

	# -------------------------------------------------------------------------
    # generate_firms
	# read in number of households and banks from parameter_values
	# generate xml files for households each randomly assigned to a bank
    # -------------------------------------------------------------------------
	def generate_firms(self, numFirms, firmfileName):
		# Read in number of firms, number of banks, and name of directory to store firms
		self.numFirms = int(numFirms)
		self.firmfileName = firmfileName
		# Loop through number of firms and create xml files
		for i in range(self.numFirms):
			identifier = "firm_" + str(i)
			firmfileName = self.firmfileName + identifier
			# the following code ensures leading zeros so filenames will be in the right order
			# for python to read in. Also, bank names are sorted properly in activeBanks of madfimas
			# this code is ugly, but works...
			firmfileName += ".xml"
			outFile = open(firmfileName,  'w')
			text = "<?xml version='1.0' encoding='UTF-8'?>\n"
			text = text + "<firm identifier= '" + identifier + "'>\n"
			text = text + "    <parameter name='endowment' value='0.0'></parameter>\n"
			text = text + "    <parameter name='propensity_to_save' value='0.4'></parameter>\n"
			text = text + "</firm>\n"
			outFile.write(text)
			outFile.close()
	# -------------------------------------------------------------------------


	# -------------------------------------------------------------------------
    # generate_banks
	# read in number of banks from parameter_values
	# generate xml files for banks
    # -------------------------------------------------------------------------
	def generate_banks(self, numBanks, bankfileName):
		import sys
		# Read in number of banks and name of directory to store banks
		self.numBanks = int(numBanks)
		self.bankfileName = bankfileName

		for i in range(self.numBanks):
			bankfileName = self.bankfileName + "bank_"+str(i)
			# the following code ensures leading zeros so filenames will be in the right order
			# for python to read in. Also, bank names are sorted properly in activeBanks of madfimas
			# this code is ugly, but works...
			bankfileName += ".xml"
			outFile = open(bankfileName,  'w')

			text = "<?xml version='1.0' encoding='UTF-8'?> \n"
			text = text + "<bank identifier= 'bank_" + str(i) + "'>\n"
			text = text + "    <parameter type='static' name='interest_rate_loans' value='0.00'></parameter>\n"
			text = text + "    <parameter type='static' name='interest_rate_deposits' value='0.00'></parameter>\n"
			text = text + "</bank>\n"
			outFile.write(text)
			outFile.close()
	# -------------------------------------------------------------------------