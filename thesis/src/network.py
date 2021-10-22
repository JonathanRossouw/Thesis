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

from networkx.algorithms.shortest_paths.weighted import negative_edge_cycle

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
	# initialize_social_network
	#-------------------------------------------------------------------------    
	def initialize_social_network(self,  environment):
		# Create networkx graph instance
		self.social_network = nx.Graph()
		# Determine number of households
		n = len(environment.households)
		# Create random graph with number of nodes equal to number of households.
		# Parameter determining randomness of graph treated as exogenous for now
		self.social_network = nx.gnp_random_graph(n, 0.6,  directed=False)
		# Iterate through nodes in graph and assign households to each node.
		# Relabel node id's to household identifier and id to house
		for iden, house in enumerate(environment.households):
			self.social_network.add_node(iden, id = "household")
			mapping = {iden: house.identifier}
			nx.relabel_nodes(self.social_network, mapping, copy = False)
	#-------------------------------------------------------------------------

	#-------------------------------------------------------------------------
	# initialize_employment_network
	# Create employment network with firms and households. Edges are created 
	# between households and firm where they work
	#-------------------------------------------------------------------------    
	def initialize_employment_network(self,  environment):
		import random
		# Create networkx graph instance
		self.employment_network = nx.Graph()
		# Loop through firms adding nodes to network
		for firm in environment.firms:
			self.employment_network.add_node(firm.identifier, id = "firm")
		# Loop through households adding to network and adding edge between 
		# household and firm where it works
		for house in environment.households:
			# Add household to network
			self.employment_network.add_node(house.identifier, id = "household")
			# Create edge between household and firm
			firm_id = random.sample(environment.firms, 1)[0].identifier
			self.employment_network.add_edge(house.identifier, firm_id)
	#-------------------------------------------------------------------------

	#-------------------------------------------------------------------------
	# initialize_consumption_network
	# Create comsumption network with firms and households. Edges are created 
	# between households and all firms
	#-------------------------------------------------------------------------    
	def initialize_consumption_network(self,  environment):
		# Create networkx graph instance
		self.consumption_network = nx.Graph()
		# Loop through firms adding nodes to network
		for firm in environment.firms:
			self.consumption_network.add_node(firm.identifier, id = "firm")
		# Loop through households adding to network and adding edge between 
		# household and firm where it works
		for house in environment.households:
			# Add household to network
			self.consumption_network.add_node(house.identifier, id = "household")
			for node in self.consumption_network.nodes(data=True):
				if node[1]["id"] == "firm":
					# Create edge between household and firm
					self.consumption_network.add_edge(house.identifier, node[0])
	#-------------------------------------------------------------------------

	#-------------------------------------------------------------------------
	# initialize_bank_network
	#-------------------------------------------------------------------------    
	def initialize_bank_network(self,  environment):
		import random
		# Create networkx graph instance
		self.bank_network = nx.Graph()
		# Loop through banks adding nodes to network
		for bank in environment.banks:
			self.bank_network.add_node(bank.identifier, id = "bank")
		# Loop through households and firms adding nodes to network and for each
		# household and firm, adds edge between bank where agent is customer
		# and agent
		for house in environment.households:
			# Add household to network
			self.bank_network.add_node(house.identifier, id = "household")
			# Create edge between household and bank
			bank_id = random.sample(environment.banks, 1)[0].identifier
			self.bank_network.add_edge(house.identifier, bank_id)

		for firm in environment.firms:
			# Add firm to network
			self.bank_network.add_node(firm.identifier, id = "household")
			# Create edge between firm and bank
			bank_id = random.sample(environment.banks, 1)[0].identifier
			self.bank_network.add_edge(firm.identifier, bank_id)
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
