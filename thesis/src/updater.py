from src.market import Market

"""
black_rhino is a multi-agent simulator for financial network analysis
Copyright (C) 2016 Co-Pierre Georg (co-pierre.georg@keble.ox.ac.uk)
Pawel Fiedor (pawel@fiedor.eu)

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

from abm_template.src.basemodel import BaseModel
import random
import logging
from src.transaction import Transaction
from src.network import Network
from src.market import Market
# -------------------------------------------------------------------------
#  class Updater
# -------------------------------------------------------------------------


class Updater(BaseModel):
    #
    #
    # VARIABLES
    #
    #

    identifier = ""
    model_parameters = {}
    interactions = None

    #
    #
    # METHODS
    #
    #

    def get_identifier(self):
        return self.identifier

    def get_store(self):
        return self.store

    def set_identifier(self, _value):
        super(Updater, self).set_identifier(_value)

    def get_model_parameters(self):
        return self.model_parameters

    def set_model_parameters(self, _value):
        super(Updater, self).set_model_parameters(_value)

    def get_interactions(self):
        return self.interactions

    def set_interactions(self, _value):
        super(Updater, self).set_interactions(_value)

    def __str__(self):
        return super(Updater, self).__str__()

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self,  environment):
        self.environment = environment
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # do_update
    # -------------------------------------------------------------------------
    def do_update(self,  environment,  time):
        # As a first step, we accrue all interest over the transactions
        # Thus, important to notice to keep 0 as interest by default
        # Unless transaction should carry interest
        # DON'T DO INTERESTS SO FAR, DO ONCE THE REST WORKS
        #self.accrue_interests(environment, time)
        # Then agents get their labour endowment for the step (e.g. work hours to spend)
        # For now we don't need to keep track of labour left as there is no queue
        self.endow_agents(environment, time)
        self.initiate_production(environment, time)
        self.do_ration_output(environment, time)
        #self.payment_shock(environment, time)
        self.net_settle(environment, time)
        # The households sell labour to firms
        #self.sell_labour(environment, time)
        # The firms sell goods to households
        #self.consume_rationed(environment, time)
        # We net deposits and loans
        #self.net_loans_deposits(environment, time)
        # We remove goods and labour (perishable) and are left with capital
        # Purging accounts at every step just in case
        transaction = Transaction()
        transaction.purge_accounts(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # endow_agents
    # Calls methods for households, firms and banks to allocate endowment
    # -------------------------------------------------------------------------
    def endow_agents(self, environment, time):
        # For eacn of households, firms and banks
        if time == 0:
            self.hh_endow_assets(environment, time)
            self.firm_endow_assets(environment, time)
            self.bank_endow_assets(environment, time)
            self.hh_allocate_assets(environment, time)
            self.firm_allocate_assets(environment, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # hh_endow_assets
    # This function makes sure that all households have the appropriate
    # deposit endowment for every step, in line with the parameters
    # -------------------------------------------------------------------------
    def hh_endow_assets(self,  environment, time):
        # Call endowment method in Households class
        if time == 0:
            for household in environment.households:
                household.hh_asset_endowment(environment, time)
            logging.info("  deposit endowed on step: %s",  time)
        # Keep on the log with the number of step, for debugging mostly
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # hh_allocate_assets
    # Households reallocate deposits to CBDC, bank notes and remaining deposits
    # -------------------------------------------------------------------------
    def hh_allocate_assets(self,  environment, time):
        # Call allocation method in Households class
        if time == 0:
            for household in environment.households:
                household.hh_asset_allocation(environment, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # firm_endow_assets
    # This function makes sure that all firms have the appropriate
    # deposit endowment for every step, in line with the parameters
    # -------------------------------------------------------------------------
    def firm_endow_assets(self,  environment, time):
        # Call endowment method in Firms class
        if time == 0:
            for firm in environment.firms:
                firm.firm_asset_endowment(environment, time)
            logging.info("  deposit endowed on step: %s",  time)
        # Keep on the log with the number of step, for debugging mostly
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # firm_allocate_assets
    # This function makes sure that all firms have the appropriate
    # deposit endowment for every step, in line with the parameters
    # -------------------------------------------------------------------------
    def firm_allocate_assets(self,  environment, time):
        # Call allocation method in Firms class
        if time == 0:
            for firm in environment.firms:
                firm.firm_asset_allocation(environment, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_endow_deposits
    # This function makes sure that all households have the appropriate
    # deposit endowment for every step, in line with the parameters
    # -------------------------------------------------------------------------
    def bank_endow_assets(self,  environment, time):
        # Call endowment method in Households and Banks class
        if time == 0:
            for bank in environment.banks:
                bank.bank_asset_allocation(environment)
            logging.info("  deposit endowed on step: %s",  time)
        # Keep on the log with the number of step, for debugging mostly
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # payment_shock(environment, time)
    # This function provides the payment shock. A portion of households are 
    # randomly hit by shock. The shock dictates that households pay a portion
    #  of deposits to a random household that shares an edge.
    # -------------------------------------------------------------------------
    def payment_shock(self, environment, time):
        if time > 0:
            import networkx as nx
            import numpy as np
            # Set G as the network
            G = environment.social_network
            # Loop through nodes in the network
            for house in G.nodes:
                # For each node randomly select whether experiences a shock using 
                # a random bernoulli variable with p = 0.6
                shock = np.random.binomial(1, 0.6, 1)
                # Shock is selected in bernoulli variable equals 1
                if shock[0] == 1:
                    # Initialize network class instance
                    environment.get_agent_by_id(house).initiate_payment(environment, time)
                    # Make payment using network class method   
    # -------------------------------------------------------------------------    

    # -------------------------------------------------------------------------
    # production(environment, time)
    # This function calls for production to be initiated for the step. Households
    # provide labour to firms, which firms pay for. Firms use labour to produce
    # output. The households purchase output and the labour/output obligation is
    # cancelled out.
    # -------------------------------------------------------------------------
    def initiate_production(self, environment, time):
        if time > 0:
            G = environment.employment_network
            # Loop through firms in the network and initiate production
            for u in G.nodes(data=False):
                agent = environment.get_agent_by_id(u)
                if agent in environment.firms:
                    agent.production(environment, time)
    # ------------------------------------------------------------------------- 

    # -------------------------------------------------------------------------
    # do_ration_output(self, environment)
    # Loop through nodes in consumption network and ration output for each 
    # household and all firms
    # -------------------------------------------------------------------------
    def do_ration_output(self, environment, time):
        if time > 0:
            mark = Market(environment)
            G = environment.consumption_network
            for node in list(G.nodes(data=True)):
                if node[1]["id"] == "household":
                    mark.output_rationing(environment, node, time)
    # -------------------------------------------------------------------------
 

    # -------------------------------------------------------------------------
    # net_settles(environment, time)
    # This function settles the transactions following the shock. If from and 
    # to are at the same bank then transaction is settled. If different banks
    # then only every fourth period is settled.
    # -------------------------------------------------------------------------
    def net_settle(self,  environment, time):
        # Settle payments by with banks
        # Iteratre through stored transactions
        for bank_trans in environment.banks[:]:
            bank_trans.interbank_settle(environment, time)
            #settlement = Network(environment)
            #settlement.net_settle_transaction(environment, bank_trans, time)
    # -------------------------------------------------------------------------
