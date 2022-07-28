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

		# Make sure all firms have at least one household
		hh_count = []
		firm_id = []
		for firm in environment.firms:
			households = list(self.employment_network.adj[firm.identifier])
			firm_id.append(firm.identifier)
			hh_count.append(len(households)) 
			while min(hh_count) == 0:
				firm_min_id = firm_id[hh_count.index(min(hh_count))]
				firm_max_id = firm_id[hh_count.index(max(hh_count))]

				household_max = list(self.employment_network.adj[firm_max_id])[0]

				self.employment_network.add_edge(household_max, firm_min_id)
				self.employment_network.remove_edge(household_max, firm_max_id)

				hh_count = []
				firm_id = []

				for firm in environment.firms:
					households = list(self.employment_network.adj[firm.identifier])
					firm_id.append(firm.identifier)
					hh_count.append(len(households)) 
	#-------------------------------------------------------------------------

	#-------------------------------------------------------------------------
	# initialize_consumption_network
	# Create comsumption network with firms and households. Edges are created 
	# between households and all firms
	#-------------------------------------------------------------------------    
	def initialize_consumption_network(self,  environment):
		from random import sample
		from numpy import floor
		# Create networkx graph instance
		self.consumption_network = nx.Graph()
		# Loop through households adding nodes to network
		for house in environment.households:
			self.consumption_network.add_node(house.identifier, id = "household")

		# firms and household that are in this consumption neighbourhood
		for firm in environment.firms:
			# Add household to network
			self.consumption_network.add_node(firm.identifier, id = "firm")
			# Create edge between firm and random households
			# connect random number of households between a third and all households
			# to firm for consumption neighbourhood
			num_hh = len(environment.households)
			hh_sample_size = list(range(int(floor(num_hh/3)), num_hh))
			households_id = sample(environment.households, sample(hh_sample_size, 1)[0])
			for id_ in households_id:
				self.consumption_network.add_edge(firm.identifier, id_.identifier)

		# Make sure all households have at least one firm
		for house in environment.households:
			firms = list(self.consumption_network.adj[house.identifier])
			firm_count = len(firms)
			if firm_count == 0:
				firm_id = sample(environment.firms, 1)[0].identifier
				self.consumption_network.add_edge(firm_id, house.identifier)
	#-------------------------------------------------------------------------

	#-------------------------------------------------------------------------
	# initialize_bank_network
	#-------------------------------------------------------------------------    
	def initialize_bank_network(self,  environment):
		import random
		# Create networkx graph instance
		self.bank_network = nx.Graph()
					
		# Loop through households and firms adding nodes to network and for each
		# household and firm, adds edge between bank where agent is customer
		# and agent

		# # Loop through banks adding nodes to network and create dict for banks
		bank_count = len(environment.banks)
		bank_ids = {}
		for bank in environment.banks:
			self.bank_network.add_node(bank.identifier, id = "bank")
			bank_ids[bank.identifier] = []

		# Create list of households and add to network
		hh_ids = []
		[hh_ids.append(x.identifier) for x in environment.households]
		for hh in hh_ids:
			self.bank_network.add_node(hh, id = "household")

		# Shuffle households ids
		random.shuffle(hh_ids)
		
		# Match banks and households
		for i, key in enumerate(bank_ids):
			bank_ids[key] = hh_ids[i::bank_count]
		# Add edge between bank and households
		for key in bank_ids:
			for values in bank_ids[key]:
				self.bank_network.add_edge(values, key)
		# Create list of firms and add to network
		firm_ids = []
		[firm_ids.append(x.identifier) for x in environment.firms]
		for firm in firm_ids:
			self.bank_network.add_node(firm, id = "firm")
		# Shuffle firm ids
		random.shuffle(firm_ids)
		# Match banks and firms
		for i, key in enumerate(bank_ids):
			bank_ids[key] = firm_ids[i::bank_count]
		# Add edge between bank and firm
		for key in bank_ids:
			for values in bank_ids[key]:
				self.bank_network.add_edge(values, key)




		# for house in environment.households:
		# 	# Add household to network
		# 	self.bank_network.add_node(house.identifier, id = "household")
		# 	# Create edge between household and bank
		# 	bank_id = random.sample(environment.banks, 1)[0].identifier
		# 	self.bank_network.add_edge(house.identifier, bank_id)

		# for firm in environment.firms:
		# 	# Add firm to network
		# 	self.bank_network.add_node(firm.identifier, id = "household")
		# 	# Create edge between firm and bank
		# 	bank_id = random.sample(environment.banks, 1)[0].identifier
		# 	self.bank_network.add_edge(firm.identifier, bank_id)


		# Make sure all banks have at least one household or firm
		agent_count = []
		bank_id = []
		for bank in environment.banks:
			agents = list(self.bank_network.adj[bank.identifier])
			bank_id.append(bank.identifier)
			agent_count.append(len(agents)) 
			while min(agent_count) == 0:
				bank_min_id = bank_id[agent_count.index(min(agent_count))]
				bank_max_id = bank_id[agent_count.index(max(agent_count))]

				agent_max = list(self.bank_network.adj[bank_max_id])[0]

				self.bank_network.add_edge(agent_max, bank_min_id)
				self.bank_network.remove_edge(agent_max, bank_max_id)

				agent_count = []
				bank_id = []

				for bank in environment.banks:
					agents = list(self.bank_network.adj[bank.identifier])
					bank_id.append(bank.identifier)
					agent_count.append(len(agents)) 
	#-------------------------------------------------------------------------


	#-------------------------------------------------------------------------
	# initialize_interbank_network
	#-------------------------------------------------------------------------    
	def initialize_interbank_network(self,  environment):
		# Create networkx graph instance
		self.interbank_network = nx.Graph()
		# Determine number of households
		n = len(environment.banks)
		# Create random graph with number of nodes equal to number of households.
		# Parameter determining randomness of graph treated as exogenous for now
		self.interbank_network = nx.gnp_random_graph(n, 1,  directed=False)

		# Iterate through nodes in graph and assign households to each node.
		# Relabel node id's to household identifier and id to house
		for iden, bank in enumerate(environment.banks):
			self.interbank_network.add_node(iden, id = "bank")
			mapping = {iden: bank.identifier}
			nx.relabel_nodes(self.interbank_network, mapping, copy = False)
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
