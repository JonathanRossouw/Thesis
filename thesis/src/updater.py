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
import datetime
import numpy as np
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
        self.net_settle(environment, time)
        self.payment_shock(environment, time)
        self.net_settle(environment, time)
        self.firms_repay_loans(environment, time)
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
        # Set Date Time from time
        year,julian = [2021,time]
        date_time = datetime.datetime(year, 1, 1)+datetime.timedelta(days=julian -1)
        # Year Month Day
        year = int(date_time.strftime("%y"))
        month = int(date_time.strftime("%m"))
        day = date_time.strftime("%d")
        # Find last day of month
        end_day = (datetime.date(year + int(month/12), month%12+1, 1) -datetime.timedelta(days=1)).strftime("%d")
        if time > 0 and day != end_day and day != 1:
            # Set G as the network
            G = environment.social_network
            # Loop through nodes in the network
            for house in G.nodes:
                # For each node randomly select whether experiences a shock using 
                # a random bernoulli variable with p = 0.6
                shock = np.random.binomial(1, 0.2, 1)
                # Shock is selected in bernoulli variable equals 1
                if shock[0] == 1:
                    # Initialize network class instance
                    environment.get_agent_by_id(house).initiate_payment(environment, time)
    # -------------------------------------------------------------------------    

    # -------------------------------------------------------------------------
    # production(environment, time)
    # This function calls for production to be initiated for the step. Households
    # provide labour to firms, which firms pay for. Firms use labour to produce
    # output. The households purchase output and the labour/output obligation is
    # cancelled out.
    # -------------------------------------------------------------------------
    def initiate_production(self, environment, time):
        # Set Date Time from time
        year,julian = [2021,time]
        date_time = datetime.datetime(year, 1, 1)+datetime.timedelta(days=julian -1)
        # Year Month Day
        year = int(date_time.strftime("%y"))
        month = int(date_time.strftime("%m"))
        day = date_time.strftime("%d")
        # Find last day of month
        end_day = (datetime.date(year + int(month/12), month%12+1, 1) -datetime.timedelta(days=1)).strftime("%d")
        # Production on the first of the month
        if time > 0:
            if day == "01":
                G = environment.employment_network
                # Loop through firms in the network and initiate production
                for u in G.nodes(data=False):
                    agent = environment.get_agent_by_id(u)
                    if agent in environment.firms:
                        agent.production(environment, time)
                        print(f"\n PRODUCTION {agent.identifier}!!! \n")

            # Wages on the 25th of the month
            if (int(day) % 25) == 0:
                environment.sweep_cbdc_payments = 0
                G = environment.employment_network
                # Loop through firms in the network and pay wages
                for u in G.nodes(data=False):
                    agent = environment.get_agent_by_id(u)
                    if agent in environment.firms:
                        agent.production_wage(environment, time)
                        print(f"\n PAID WAGES {agent.identifier}!!! \n")
                        
    # ------------------------------------------------------------------------- 

    # -------------------------------------------------------------------------
    # firms_repay_loans(self, environment, time)
    # Loop through firms and repay loans to banks
    # -------------------------------------------------------------------------
    def firms_repay_loans(self, environment, time):
        # Set Date Time from time
        year,julian = [2021,time]
        date_time = datetime.datetime(year, 1, 1)+datetime.timedelta(days=julian -1)
        # Year Month Day
        year = int(date_time.strftime("%y"))
        month = int(date_time.strftime("%m"))
        day = date_time.strftime("%d")
        # Find last day of month
        end_day = (datetime.date(year + int(month/12), month%12+1, 1) -datetime.timedelta(days=1)).strftime("%d")
        # Production on the first of the month
        if time > 0:
        # Repay loans and contracts expire on the last day of the month
            if end_day == day:
                environment.sweep_cbdc_payments = 0
                G = environment.employment_network
                # Loop through firms in the network and repay loans
                for u in G.nodes(data=False):
                    agent = environment.get_agent_by_id(u)
                    if agent in environment.firms:
                        agent.production_repay_loan(environment, time)
                        print(f"\n REPAY LOANS {agent.identifier}!!! \n")
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # do_ration_output(self, environment, time)
    # Loop through nodes in consumption network and ration output for each 
    # household and all firms
    # -------------------------------------------------------------------------
    def do_ration_output(self, environment, time):
        # Set Date Time from time
        year,julian = [2021,time]
        date_time = datetime.datetime(year, 1, 1)+datetime.timedelta(days=julian -1)
        # Year Month Day
        year = int(date_time.strftime("%y"))
        month = int(date_time.strftime("%m"))
        day = date_time.strftime("%d")
        # Find last day of month
        end_day = (datetime.date(year + int(month/12), month%12+1, 1) -datetime.timedelta(days=1)).strftime("%d")
        # Production on the first of the month
        mark = Market(environment)
        G = environment.consumption_network
        if time > 0:
            if day != end_day:
                for node in list(G.nodes(data=True)):
                    if node[1]["id"] == "household":
                        shock = np.random.binomial(1, 0.6, 1)
                        # Shock is selected in bernoulli variable equals 1
                        if shock[0] == 1:
                            mark.output_rationing(environment, node, time)
                            print(f"\n RATION OUTPUT!!! \n")
            elif day == end_day:
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
    # -------------------------------------------------------------------------
