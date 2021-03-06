#!/usr/bin/env python
# [SublimeLinter pep8-max-line-length:150]
# -*- coding: utf-8 -*-

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

import logging
from abm_template.src.baseagent import BaseAgent

# ============================================================================
#
# class Firm
#
# ============================================================================


class Firm(BaseAgent):
    #
    #
    # VARIABLES
    #
    #

    identifier = ""  # identifier of the specific firm
    parameters = {}  # parameters of the specific firm
    state_variables = {}  # state variables of the specific firm
    accounts = []  # all accounts of a firm (filled with transactions)
    assets = []
    liabilities = []
    sales = 0.0
    wages = 0.0
    capital = 0

    #
    #
    # CODE
    #
    #

    # -------------------------------------------------------------------------
    # functions for setting/changing id, parameters, and state variables
    # these either return or set specific value to the above variables
    # with the exception of append (2 last ones) which append the dictionaries
    # which contain parameters or state variables
    # -------------------------------------------------------------------------
    def get_identifier(self):
        return self.identifier

    def set_identifier(self, value):
        super(Firm, self).set_identifier(value)

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, value):
        super(Firm, self).set_parameters(value)

    def get_state_variables(self):
        return self.state_variables

    def set_state_variables(self, value):
        super(Firm, self).set_state_variables(value)

    def append_parameters(self, value):
        super(Firm, self).append_parameters(value)

    def append_state_variables(self, value):
        super(Firm, self).append_state_variables(value)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # functions needed to make Firm() hashable
    # -------------------------------------------------------------------------
    def __key__(self):
        return self.identifier

    def __eq__(self, other):
        return self.__key__() == other.__key__()

    def __hash__(self):
        return hash(self.__key__())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self):
        self.identifier = ""  # identifier of the specific firm
        self.parameters = {}  # parameters of the specific firm
        self.state_variables = {}  # state variables of the specific firm
        self.accounts = []  # all accounts of a firm (filled with transactions)
        # DO NOT EVER ASSIGN PARAMETERS BY HAND AS DONE BELOW IN PRODUCTION CODE
        # ALWAYS READ THE PARAMETERS FROM CONFIG FILES
        # OR USE THE FUNCTIONS FOR SETTING / CHANGING VARIABLES
        # CONVERSELY, IF YOU WANT TO READ THE VALUE, DON'T USE THE FULL NAMES
        # INSTEAD USE __getattr__ POWER TO CHANGE THE COMMAND FROM
        # instance.static_parameters["xyz"] TO instance.xyz - THE LATTER IS PREFERRED
        #self.parameters["productivity"] = 0.0  # how many units of goods do we get from 1 unit of labour
        #self.parameters["active"] = 0  # this is a control parameter checking whether firm is active
        self.assets = ["deposits", "bank_notes", "receivables"]
        self.liabilities = ["loans"] #self.liabilities = ["capital_firm", "loans"]
        self.supply = 0
        self.sales = 0
        self.equity_households = {}
        self.capital = 0
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __del__
    # -------------------------------------------------------------------------
    def __del__(self):
        pass
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __str__
    # returns a string describing the firm and its properties
    # based on the implementation in the abstract class BaseAgent
    # but adds the type of agent (firm) and lists all transactions
    # -------------------------------------------------------------------------
    def __str__(self):
        firm_string = super(Firm, self).__str__()
        firm_string = firm_string.replace("\n", "\n    <type value='firm''>\n", 1)
        text = "\n"
        text = text + "  </agent>"
        return firm_string.replace("\n  </agent>", text, 1)
    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_parameters_from_file
    # reads the specified config file given the environment
    # and sets parameters to the ones found in the config file
    # the config file should be an xml file that looks like the below:
    # <firm identifier='string'>
    #     <parameter name='string' value='string'></parameter>
    # </firm>
    # -------------------------------------------------------------------------
    def get_parameters_from_file(self,  firm_filename, environment): ###### NEW CODE
        from xml.etree import ElementTree

        try:
            xmlText = open(firm_filename).read()
            element = ElementTree.XML(xmlText)
            # we get the identifier
            self.identifier = element.attrib['identifier']
            # and then we're only interested in <parameter> fields
            element = element.findall('parameter')

            # loop over all <parameter> entries in the xml file
            for subelement in element:
                name = subelement.attrib['name']
                value = subelement.attrib['value']
                # add them to parameter list
                if name == "bank_acc":
                    self.parameters[name] = str(value)
                else:
                    self.parameters[name] = float(value)

        except:
            logging.error("    ERROR: %s could not be parsed",  firm_filename)

    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # firm_capitalize
    # firm is capitalized by equity from households
    # -------------------------------------------------------------------------
    def firm_capitalize(self, environment, tranx, time):
        # Capitalize firm, provide household with equity
        environment.new_transaction(type_="equity_firm", asset='', from_= tranx["from_"], to = tranx["to"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        environment.new_transaction(type_="bank_notes", asset='', from_= tranx["to"], to = tranx["from_"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        self.equity_households[tranx["to"]] = tranx["amount"]
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # firm_deposit_bank_notes
    # firm is capitalized by equity from households
    # -------------------------------------------------------------------------
    def firm_deposit_bank_notes(self, environment, time):
        # Create record of proportions of equity each household owns
        total_equity = sum(self.equity_households.values())
        for val in self.equity_households:
            self.equity_households[val] = round(self.equity_households[val]/total_equity, 8)

        # Deposit bank notes at bank to create deposits
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        bank_notes = self.get_account("bank_notes")
        # Allocate Endowment and create bank balance
        endowment_tranx = {"type_": "bank_notes", "from_" : self.identifier, "bank_from": bank_acc, "to" : self.identifier, "bank_to" : bank_acc, "amount" : bank_notes, "time" : time}
        environment.get_agent_by_id(bank_acc).bank_notes_to_deposits(environment, endowment_tranx, time)
        #pr(self.balance_sheet())
    # -------------------------------------------------------------------------



    # -------------------------------------------------------------------------
    # loan_capital
    # take out long term long to purchase capital
    # -------------------------------------------------------------------------
    def loan_capital(self, environment, time):
        # Take out loan
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        loan_amount = self.get_equity()
        loan_tranx = {"type_": "loans", "from_" : self.identifier, "bank_from": bank_acc, "to" : bank_acc, "amount" : loan_amount, "time" : time}
        environment.get_agent_by_id(bank_acc).new_loans_firm_capital(environment, loan_tranx, time)
        # Purchase capital
        self.capital += loan_amount
        #print(f"{self.identifier} took out loan of {loan_amount} for capital")
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # get_households
    # create list of household identifiers for households that work at firm
    # -------------------------------------------------------------------------
    def get_households(self, environment):
        households = []
        import networkx as nx
        G = environment.network
        # Loop through nodes in the network
        for u, dat in G.nodes(data=True):
        # Loop through all households
            # If household is customer append to list
            if environment.get_agent_by_id(dat["id"]).firm_acc == self.identifier:
                households.append(dat["id"])
        return households
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # production_function
    # create daily production
    # -------------------------------------------------------------------------
    def production_function(self, environment, time):
        households = list(environment.employment_network.adj[self.identifier])
        # Get labour from households
        labour = 0
        for id_ in households:
            house = environment.get_agent_by_id(id_)
            labour += house.labour # Could be changed to a stochastic variable where household decide whether or not to provide labour
        capital = self.capital * 0.01
        gamma = 1
        beta = 1    
        # Produce Output
        import numpy

        #technology_shock = numpy.random.binomial(1, 0.2) * numpy.random.uniform(0.1, 0.5) 
        technology_shock = 0
        if technology_shock > 0:
            self.supply = technology_shock * (labour ** beta) * (capital ** gamma) # Production function
        else: 
            self.supply =  (labour ** beta) * (capital ** gamma) # Production function
        environment.total_output += self.supply
        #print(f"\n{self.identifier} produced {self.supply} units of output using {capital} units of capital and {labour} units of labour at time {time}.")
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # production_wage
    # pay wages on the 25th of month
    # -------------------------------------------------------------------------
    def production_wage(self, environment, time):
        # Get households that work at firm
        households = list(environment.employment_network.adj[self.identifier])
        # Get firm bank acc
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        # Determine proportion of sales each household receives
        wage = self.sales/len(households)
        self.sales -= self.sales

        # Pay for wages
        for id_ in households:
            house = environment.get_agent_by_id(id_)
            house_bank_acc = list(environment.bank_network.adj[id_])[0]
            # Check level of deposits
            deposits_remain = self.get_account("deposits")
            # If transaction amount is greater than remaining deposits, household takes
            # out new loan for residual amount
            if wage > deposits_remain:
                loan_amount = wage - deposits_remain
                # New loan
                self.loan_new(environment, loan_amount, time)
                # Pay for Wages with deposits
                deposit_tranx = {"type_": "deposits", "from_" : self.identifier, "bank_from": bank_acc, "to" : house.identifier, "bank_to" : house_bank_acc, "amount" : wage, "time" : time}
                environment.get_agent_by_id(bank_acc).make_payment(environment, deposit_tranx, time)
            else: 
                # Pay for Wages with deposits
                deposit_tranx = {"type_": "deposits", "from_" : self.identifier, "bank_from": bank_acc, "to" : house.identifier, "bank_to" : house_bank_acc, "amount" : wage, "time" : time}
                environment.get_agent_by_id(bank_acc).make_payment(environment, deposit_tranx, time)
            #print(f"\n {wage} unit wage paid with {house.identifier} for labour")
            #print(self.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # loan_repay
    # firm repays loans
    # -------------------------------------------------------------------------
    def loan_repay(self, environment, time):
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        loan_amount = self.get_account("loans")
        loan_tranx = {"type_": "loans", "from_" : self.identifier, "bank_from": bank_acc, "to" : self.identifier, "bank_to" : bank_acc, "amount" : loan_amount, "time" : time}
        environment.get_agent_by_id(bank_acc).repay_loan(environment, loan_tranx)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # loan_new
    # firm takes out new loans
    # -------------------------------------------------------------------------
    def loan_new(self, environment, loan_amount, time):
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        loan_tranx = {"type_": "loans", "from_" : self.identifier, "bank_from": bank_acc, "to" : bank_acc, "bank_to" : bank_acc, "amount" : loan_amount, "time" : time}
        environment.get_agent_by_id(bank_acc).new_loan(environment, loan_tranx)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # get_new_investments
    # placeholder for a function determining production size of a firm
    # -------------------------------------------------------------------------
    def get_new_investments(self, low, high):
        pass
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # balance_sheet
    # returns balance sheet of agent
    # -------------------------------------------------------------------------
    def balance_sheet(self):
        balance_sheet = {}
        assets = {"capital":self.capital}
        liabilities = {}
        for item in self.assets:
            assets[item] = round(self.get_account(item), 5)
        for item in self.liabilities:
            liabilities[item] = round(self.get_account(item), 5)

        equity = sum(assets.values()) - sum(liabilities.values())
        if equity > 0:
            liabilities["equity"] = equity
        elif equity < 0:
            assets["equity"] = abs(equity)

        balance_sheet["assets"] = assets
        balance_sheet["liabilities"] = liabilities
        balance_sheet = {self.identifier: balance_sheet}
        return balance_sheet

    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_equity
    # calculates equity
    # -------------------------------------------------------------------------
    def get_equity(self):
        assets = {"capital":self.capital}
        liabilities = {}
        for item in self.assets:
            assets[item] = round(self.get_account(item), 7)
        for item in self.liabilities:
            liabilities[item] = round(self.get_account(item), 7)

        equity = sum(assets.values()) - sum(liabilities.values())
        return equity
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # check_consistency
    # checks whether the assets and liabilities have the same total value
    # -------------------------------------------------------------------------
    def check_consistency(self):
        balance_sheet = self.balance_sheet()
        assets = sum(balance_sheet[self.identifier]["assets"].values())
        liabilities = sum(balance_sheet[self.identifier]["liabilities"].values())
        return assets == liabilities
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_account
    # returns the value of all transactions of a given type
    # -------------------------------------------------------------------------
    def get_account(self,  type_):
        volume = 0.0

        for transaction in self.accounts:
            if transaction.type_ in self.assets:
                if (transaction.type_ == type_) & (transaction.from_.identifier == self.identifier):
                    volume = volume - float(transaction.amount)
                elif (transaction.type_ == type_) & (transaction.from_ .identifier!= self.identifier):
                    volume = volume + float(transaction.amount)
            elif transaction.type_ in self.liabilities:
                if (transaction.type_ == type_) & (transaction.from_.identifier == self.identifier):
                    volume = volume + float(transaction.amount)
                elif (transaction.type_ == type_) & (transaction.from_.identifier != self.identifier):
                    volume = volume - float(transaction.amount)
        if type_ == "fixed_assets":
            volume = -volume
        return volume
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_account_num_transactions
    # returns the number of transactions of a given type
    # -------------------------------------------------------------------------
    def get_account_num_transactions(self,  type_):
        return super(Firm, self).get_account_num_transactions(type_)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # add_transaction
    # adds a transaction to the accounts
    # the transaction is endowed with the following information:
    #   type_           - type of transactions, e.g. "deposit"
    #   assets          - type of asset, used for investment types
    #   from_id         - agent being the originator of the transaction
    #   to_id           - agent being the recipient of the transaction
    #   amount          - amount of the transaction
    #   interest        - interest rate paid to the originator each time step
    #   maturity        - time (in steps) to maturity
    #   time_of_default - control variable checking for defaulted transactions
    # -------------------------------------------------------------------------
    def add_transaction(self,  type_, asset, from_id,  to_id,  amount,  interest,  maturity, time_of_default, environment):
        from src.transaction import Transaction
        transaction = Transaction()
        transaction.this_transaction(type_, asset, from_id,  to_id,  amount,  interest,  maturity,  time_of_default)
        transaction.add_transaction(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # clear_accounts
    # removes all transactions from firm's accounts
    # only for testing, the one in transaction should be used in production
    # -------------------------------------------------------------------------
    def clear_accounts(self):
        super(Firm, self).clear_accounts()
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # purge_accounts
    # removes worthless transactions from firm's accounts
    # -------------------------------------------------------------------------
    def purge_accounts(self, environment):
        super(Firm, self).purge_accounts(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_transactions_from_file
    # reads transactions from the config file to the firm's accounts
    # -------------------------------------------------------------------------
    def get_transactions_from_file(self, filename, environment):
        super(Firm, self).get_transactions_from_file(filename, environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __getattr__
    # if the attribute isn't found by Python we tell Python
    # to look for it first in parameters and then in state variables
    # which allows for directly fetching parameters from the Firm
    # i.e. firm.active instead of a bit more bulky
    # firm.parameters["active"]
    # makes sure we don't have it in both containers, which
    # would be bad practice [provides additional checks]
    # -------------------------------------------------------------------------
    def __getattr__(self, attr):
        return super(Firm, self).__getattr__(attr)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # demand_for_labour(price)
    # this is for testing for now, makes the demand labour to be
    # a linear function of price
    # TEST ONLY, REMOVE LATER IF NOT NECESSARY
    # -------------------------------------------------------------------------
    def demand_for_labour(self, price):
        return max(0.0, 100.0 - price * 1.5)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # demand_for_labour_new(price)
    # this is for testing for now, makes the demand labour to be
    # Cobb-Douglas with no capital Y = a * l^b * 1 (for capital)
    # TEST ONLY, REMOVE LATER IF NOT NECESSARY
    # -------------------------------------------------------------------------
    def demand_for_labour_new(self, price):
        a = 5
        b = 0.5
        goods_price = 10.0
        return max(0, (price / (a * b * goods_price)) ** (1 / (b-1)))
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # demand_for_labour_solow(price)
    # Demand for labour stemming from the Solow model with C-D function
    # Derived as maximum utility (profit: production*price - wage*labour)
    # given C-D production function Y=a*L^b*C^c
    # -------------------------------------------------------------------------
    def demand_for_labour_solow(self, price_of_labour):
        # The parameters of the production function are read from the config
        # And reassigned here for easier formula below
        a = self.total_factor_productivity
        b = self.labour_elasticity
        c = self.capital_elasticity
        # This is the one price set up, we only consider relative prices in the model
        # as consistent with DSGE models and the rest of macroeconomics
        goods_price = 10.0
        # Finally max(U) given particular wage
        return max(0, (price_of_labour / (a * b * goods_price * self.get_account("capital") ** c)) ** (1 / (b-1)))
    # -------------------------------------------------------------------------
