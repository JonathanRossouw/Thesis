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
    # firm_asset_allocation
    # firm takes loan out at bank
    # -------------------------------------------------------------------------
    def firm_asset_endowment(self, environment, time):
        import random
        # Create Loan Account at Bank
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        loan_tranx = {"type_": "loan_endow", "from_" : self.identifier, "bank_from": bank_acc, "to" : self.identifier, "bank_to" : bank_acc, "amount" : self.endowment, "time" : time}
        environment.get_agent_by_id(bank_acc).bank_initialize_firm(environment, loan_tranx)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # firm_asset_allocation
    # firm chooses proportion of endowment held in bank deposits, CBDC and
    # bank notes
    # -------------------------------------------------------------------------
    def firm_asset_allocation(self, environment, time):
        import random
        # Decide on asset allocation
        # Decide on Deposits
        deposits = self.endowment * 2/3# random.uniform(0.4, 0.8)   #### Use this to set asset allowcation to only deposits
        # Decide on CBDC
        cbdc = (self.endowment - deposits) #* random.uniform(0.5, 1)  #### Use this to set asset allowcation to only CBDC
        # Remainder to bank_notes
        bank_notes = (self.endowment - deposits - cbdc)
        # Purchase CBDC from Deposits at Bank with Central Bank
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        cbdc_allocation = {"type_": "deposits", "from_" : self.identifier, "bank_from": bank_acc, "to" : "central_bank", "bank_to" : "central_bank", "amount" : cbdc, "time" : time}
        environment.get_agent_by_id(bank_acc).cbdc_purchase(environment, cbdc_allocation, time)
        # Create Bank_notes at Central Bank
        bank_notes_allocation = {"type_": "deposits", "from_" : self.identifier, "bank_from": bank_acc, "to" : "central_bank", "bank_to" : "central_bank", "amount" : bank_notes, "time" : time}
        environment.get_agent_by_id(bank_acc).bank_notes_purchase(environment, bank_notes_allocation, time)
        print(f"{self.identifier} chose {deposits} deposits, {cbdc} cbdc, and {bank_notes} bank_notes")
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # balance
    # net payments and receipts, returns balance
    # -------------------------------------------------------------------------
    def balance(self, type_):
        # Determine Endowments
        labour = 0
        wages = 0
        output = 0
        loans = self.get_account("loan_endow")
        deposits = self.get_account("deposits_endow")
        cbdc = self.get_account("cbdc_endow")
        bank_notes = self.get_account("bank_notes_endow")
        # Track Changes for different asset classes
        for tranx in self.accounts:
            # Transaction from firm decrease balance
            if tranx.from_.identifier == self.identifier:
                if tranx.type_ == "deposits":
                   deposits -= tranx.amount
                elif tranx.type_ == "loans":
                   loans -= tranx.amount
                elif tranx.type_ == "cbdc":
                   cbdc -= tranx.amount
                elif tranx.type_ == "bank_notes":
                   bank_notes -= tranx.amount

                elif tranx.type_ == "labour":
                    labour -= tranx.amount
                elif tranx.type_ == "wages":
                    wages += tranx.amount
                elif tranx.type_ == "output":
                    output += tranx.amount

            # Transactions to firm increase balance
            elif tranx.from_.identifier != self.identifier:
                if tranx.type_ == "deposits":
                   deposits += tranx.amount
                elif tranx.type_ == "loans":
                   loans += tranx.amount
                elif tranx.type_ == "cbdc":
                   cbdc += tranx.amount
                elif tranx.type_ == "bank_notes":
                   bank_notes += tranx.amount

                elif tranx.type_ == "labour":
                    labour += tranx.amount
                elif tranx.type_ == "wages":
                    wages -= tranx.amount
                elif tranx.type_ == "output":
                    output -= tranx.amount
        # Return Requested Balance
        if type_ == "deposits":
            return deposits
        elif type_ == "loans":
            return loans
        elif type_ == "cbdc":
            return cbdc
        elif type_ == "bank_notes":
            return bank_notes
        elif type_ == "labour":
            return labour
        elif type_ == "wages":
            return wages
        elif type_ == "output":
            return output
        elif type_ == "assets":
            return (deposits + cbdc + bank_notes + wages)
        elif type_ == "liabilities":
            return (loans + output)
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
    # production
    # placeholder for a function determining production size of a firm
    # -------------------------------------------------------------------------
    def production(self, environment, time):
        households = list(environment.employment_network.adj[self.identifier])
        labour = self.balance("labour")
        capital = self.balance("deposits")
        wage = 1
        loan = wage * labour
        alpha = 1/capital
        beta = 1
        gamma = 1
        price = 1
        # Take out loan
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        loan_tranx = {"type_": "loans", "from_" : self.identifier, "bank_from": bank_acc, "to" : self.identifier, "bank_to" : bank_acc, "amount" : loan, "time" : time}
        environment.get_agent_by_id(bank_acc).new_loan(environment, loan_tranx)

        # Produce Output

        self.supply = round(alpha * (labour ** beta) * (capital ** gamma), 5)
        environment.total_output += self.supply

        # Create wage agreement and pay for wages
        for id_ in households:
            house = environment.get_agent_by_id(id_)
            house_bank_acc = list(environment.bank_network.adj[id_])[0]
            # Create Agreement
            wages = (wage * labour)/len(households)
            wage_tranx = {"type_": "wages", "from_" : self.identifier, "bank_from": bank_acc, "to" : house.identifier, "bank_to" : house_bank_acc, "amount" : wages, "time" : time}
            environment.new_transaction(type_="wages", asset='', from_= wage_tranx["from_"], to = wage_tranx["to"], amount = wage_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            # Create demand
            house.supply = -self.supply/len(households)
            # Pay for Wages with deposits
            wage_tranx["type_"] = "deposits"
            environment.get_agent_by_id(bank_acc).make_payment(environment, wage_tranx, time)
            print(f"{wages} unit wage agreement with {house.identifier} for labour")

        # Create output agreement and sell output
        for id_ in households:
            house = environment.get_agent_by_id(id_)
            house_bank_acc = list(environment.bank_network.adj[id_])[0]
            # Create Output agreement and 
            out = (price * self.supply)/len(households)
            out_tranx = {"type_": "output", "from_" : self.identifier, "bank_from": bank_acc, "to" : house.identifier, "bank_to" : house_bank_acc, "amount" : out, "time" : time}
            environment.new_transaction(type_="output", asset='', from_= out_tranx["from_"], to = out_tranx["to"], amount = out_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            # Sell output for deposits
            sell_tranx = {"type_": "deposits", "from_" : house.identifier, "bank_from": house_bank_acc, "to" : self.identifier, "bank_to" : bank_acc, "amount" : out, "time" : time}
            house.deposits_payment(environment, sell_tranx, time)
            print(f"{out} units output agreement with {house.identifier}")

        # Repay Loan
        environment.get_agent_by_id(bank_acc).repay_loan(environment, loan_tranx)

        # Households consume output and agreements are settled

        for id_ in households:
            house = environment.get_agent_by_id(id_)
            house_bank_acc = list(environment.bank_network.adj[id_])[0]
            # Settle Labour Agreement
            lab = (labour)/len(households)
            lab_tranx = {"type_": "labour", "from_" : self.identifier, "to" : house.identifier, "amount" : lab, "time" : time}
            environment.new_transaction(type_="labour", asset='', from_= lab_tranx["from_"], to = lab_tranx["to"], amount = lab_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            # Settle wage agreements
            wages = (wage * labour)/len(households)
            wage_tranx = {"type_": "wages", "from_" : self.identifier, "bank_from": bank_acc, "to" : house.identifier, "bank_to" : house_bank_acc, "amount" : wages, "time" : time}
            environment.new_transaction(type_="wages", asset='', from_= wage_tranx["to"], to = wage_tranx["from_"], amount = wage_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            # Settle output agreements
            out = (price * self.supply)/len(households)
            out_tranx = {"type_": "output", "from_" : self.identifier, "bank_from": bank_acc, "to" : house.identifier, "bank_to" : house_bank_acc, "amount" : out, "time" : time}
            environment.new_transaction(type_="output", asset='', from_= out_tranx["to"], to = out_tranx["from_"], amount = out_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # get_new_investments
    # placeholder for a function determining production size of a firm
    # -------------------------------------------------------------------------
    def get_new_investments(self, low, high):
        pass
    # -------------------------------------------------------------------------

# -------------------------------------------------------------------------
    # check_consistency
    # checks whether the assets and liabilities have the same total value
    # the types of transactions that make up assets and liabilities is
    # controlled by the lists below
    # -------------------------------------------------------------------------
    def check_consistency(self):
        assets = round(self.balance("assets"), 0)
        liabilities = round(self.balance("liabilities"), 0)
        return (assets == liabilities)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_account
    # returns the value of all transactions of a given type
    # -------------------------------------------------------------------------
    def get_account(self,  type_):
        return super(Firm, self).get_account(type_)
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
