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

import networkx as nx
import logging

#-------------------------------------------------------------------------
#
# class Network
#
#-------------------------------------------------------------------------
class Network(object):
	#
	# VARIABLES
	#
	identifier = ""
	contracts = nx.DiGraph()
	#exposures = nx.DiGraph()
	
	#
	# METHODS
	#
	#-------------------------------------------------------------------------
	# __init__
	#-------------------------------------------------------------------------
	def __init__(self,  identifier):
		self.identifier = identifier
		self.contracts = nx.DiGraph()
	#-------------------------------------------------------------------------

	#-------------------------------------------------------------------------
	# initialize_networks
	#-------------------------------------------------------------------------    
	def initialize_networks(self,  environment):
		# Create networkx graph instance
		self.contracts = nx.DiGraph()
		# Determine number of households
		n = len(environment.households)
		# Create random graph with number of nodes equal to number of households.
		# Parameter determining randomness of graph treated as exogenous for now
		self.contracts = nx.gnp_random_graph(n, 0.6,  directed=True)
		# Iterate through nodes in graph and assign households to each node.
		# Give nodes an attribute of the households ID
		for iden, house in enumerate(environment.households):
			self.contracts.add_node(iden, id = house.identifier)
	#-------------------------------------------------------------------------


#
# HELPER ROUTINES
#
	#-------------------------------------------------------------------------
	# __str()__
	#-------------------------------------------------------------------------
	def __str__(self):
		text = "<network type='contracts' identifier='" + self.identifier + "'>\n"
		for node in self.contracts.nodes():
			text += "  <node id='" + node.identifier + "'>\n"
		for edge in self.contracts.edges():
			text += "  <edge from='" + edge[0].identifier+ "' to='" + edge[1].identifier+ "'>\n"
		text += "</network>\n"
		
		text += "<network type='exposures' identifier='" + self.identifier + "'>\n"
		for node in self.exposures.nodes():
			text += "  <node id='" + node.identifier + "'>\n"
		for fromID,  toID,  edata in self.exposures.edges(data=True):
			text += "  <edge from='" + fromID.identifier + "' to='" + toID.identifier + "' weight='" + str(edata['weight']) + "'>\n"
		text += "</network>\n"
		
		return text
	#-------------------------------------------------------------------------


	#-------------------------------------------------------------------------
	# write_network_of_exposures
	#-------------------------------------------------------------------------
	def write_network_of_exposures(self, time):
		nx.write_edgelist(self.exposures.to_directed(), "exposures-" + self.identifier + "-" + str(time) + ".list")
	#-------------------------------------------------------------------------
