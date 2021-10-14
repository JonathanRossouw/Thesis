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
# class Household
#
# ============================================================================


class Household(BaseAgent):
    #
    #
    # VARIABLES
    #
    #

    identifier = ""  # identifier of the specific household
    parameters = {}  # parameters of the specific household
    state_variables = {}  # state variables of the specific household
    accounts = []  # all accounts of a household (filled with transactions)

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
        super(Household, self).set_identifier(value)

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, value):
        super(Household, self).set_parameters(value)

    def get_state_variables(self):
        return self.state_variables

    def set_state_variables(self, value):
        super(Household, self).set_state_variables(value)

    def append_parameters(self, value):
        super(Household, self).append_parameters(value)

    def append_state_variables(self, value):
        super(Household, self).append_state_variables(value)

    # -------------------------------------------------------------------------
    # functions needed to make Household() hashable
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
        self.identifier = ""  # identifier of the specific household
        self.parameters = {}  # parameters of the specific household
        self.state_variables = {}  # state variables of the specific household
        self.accounts = []  # all accounts of a household (filled with transactions)
        # DO NOT EVER ASSIGN PARAMETERS BY HAND AS DONE BELOW IN PRODUCTION CODE
        # ALWAYS READ THE PARAMETERS FROM CONFIG FILES
        # OR USE THE FUNCTIONS FOR SETTING / CHANGING VARIABLES
        # CONVERSELY, IF YOU WANT TO READ THE VALUE, DON'T USE THE FULL NAMES
        # INSTEAD USE __getattr__ POWER TO CHANGE THE COMMAND FROM
        # instance.static_parameters["xyz"] TO instance.xyz - THE LATTER IS PREFERRED
        #self.parameters["labour"] = 0.0  # labour to sell every step (labour endowment)
        #self.parameters["propensity_to_save"] = 0.40  # propensity to save, percentage of income household wants to save as deposits
        #self.parameters["active"] = 0  # this is a control parameter checking whether bank is active
        # The below is not needed, but kept just in case it will become needed
        # self.state_variables["sweep_labour"] = 0.0  # labour left in the simulation step
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __del__
    # -------------------------------------------------------------------------
    def __del__(self):
        pass
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __str__
    # returns a string describing the household and its properties
    # based on the implementation in the abstract class BaseAgent
    # but adds the type of agent (household) and lists all transactions
    # -------------------------------------------------------------------------
    def __str__(self):
        household_string = super(Household, self).__str__()
        household_string = household_string.replace("\n", "\n    <type value='household'>\n", 1)
        text = "\n"
        text = text + "  </agent>"
        return household_string.replace("\n  </agent>", text, 1)
    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_parameters_from_file
    # reads the specified config file given the environment
    # and sets parameters to the ones found in the config file
    # the config file should be an xml file that looks like the below:
    # <household identifier='string'>
    #     <parameter name='string' value='string'></parameter>
    # </household>
    # -------------------------------------------------------------------------
    def get_parameters_from_file(self,  household_filename, environment): ########## NEW CODE
        from xml.etree import ElementTree

        try:
            xmlText = open(household_filename).read()
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
                    self.parameters[name] = value
                else:
                    self.parameters[name] = float(value)

        except:
            logging.error("    ERROR: %s could not be parsed",  household_filename)
    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # hh_asset_allocation
    # household randomly choices proportion of endowment held in bank deposits
    # and proportion held in CBDC
    # -------------------------------------------------------------------------
    def hh_asset_allocation(self, environment, time):
        import random
        # Create Loan Account at Bank
        loan_tranx = {"type_": "loan_endow", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : self.identifier, "bank_to" : self.bank_acc, "amount" : self.endowment, "time" : time}
        environment.get_agent_by_id(self.bank_acc).bank_initialize_household(environment, loan_tranx)
        # Decide on asset allocation
        # Decide on Deposits
        deposits = self.endowment * random.uniform(0.4, 0.8)   #### Use this to set asset allowcation to only deposits
        # Decide on CBDC
        cbdc = (self.endowment - deposits) #* random.uniform(0.5, 1)  #### Use this to set asset allowcation to only CBDC
        # Remainder to bank_notes
        bank_notes = (self.endowment - deposits - cbdc)
        # Purchase CBDC from Deposits at Bank with Central Bank
        cbdc_allocation = {"type_": "deposits", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : "central_bank", "bank_to" : "central_bank", "amount" : cbdc, "time" : time}
        environment.get_agent_by_id(self.bank_acc).cbdc_purchase(environment, cbdc_allocation, time)
        # Create Bank_notes at Central Bank
        bank_notes_allocation = {"type_": "deposits", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : "central_bank", "bank_to" : "central_bank", "amount" : bank_notes, "time" : time}
        environment.get_agent_by_id(self.bank_acc).bank_notes_purchase(environment, bank_notes_allocation, time)
        print("{} chose {} deposits, {} cbdc, and {} bank_notes").format(self.identifier, deposits, cbdc, bank_notes)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # balance
    # net payments and receipts, returns balance
    # -------------------------------------------------------------------------
    def balance(self, type_):
        # Determine Endowments
        loans = self.get_account("loan_endow")
        deposits = self.get_account("deposits_endow")
        cbdc = self.get_account("cbdc_endow")
        bank_notes = self.get_account("bank_notes_endow")
        # Track Changes for different asset classes
        for tranx in self.accounts:
            # Transaction from household decrease balance
            if tranx.from_.identifier == self.identifier:
                if tranx.type_ == "deposits":
                   deposits -= tranx.amount
                elif tranx.type_ == "loans":
                   loans -= tranx.amount
                elif tranx.type_ == "cbdc":
                   cbdc -= tranx.amount
                elif tranx.type_ == "bank_notes":
                   bank_notes -= tranx.amount
            # Transactions to household increase balance
            elif tranx.from_.identifier != self.identifier:
                if tranx.type_ == "deposits":
                   deposits += tranx.amount
                elif tranx.type_ == "loans":
                   loans += tranx.amount
                elif tranx.type_ == "cbdc":
                   cbdc += tranx.amount
                elif tranx.type_ == "bank_notes":
                   bank_notes += tranx.amount
        # Return Requested Balance
        if type_ == "deposits":
            return deposits
        elif type_ == "loans":
            return loans
        elif type_ == "cbdc":
            return cbdc
        elif type_ == "bank_notes":
            return bank_notes
        elif type_ == "assets":
            return (deposits + cbdc + bank_notes)
        elif type_ == "liabilities":
            return (loans)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # initiate_payment
    # initiate payment and details of payment
    # Payment amount is random portion of total assets (deposits + CBDC)
    # Payment to HH with same bank, preference for deposits, if payment less than 
    # deposits balance, pay only in deposits, otherwise pay all deposits and 
    # rest with cbdc.
    # Payment to HH with different bank, preference for CBDC, if payment less than  
    # CBDC balance, pay only in CBDC, otherwise pay all CBDC and rest with deposits
    # -------------------------------------------------------------------------
    def initiate_payment(self, environment, time):
        import networkx as nx
        import random
        G = nx.get_node_attributes(environment.network, "id")
        # Get key corresponding to household making payment
        from_id = G.values().index(self.identifier)
        # Select random edge from household making payments edges
        if len(environment.network.edges(from_id)) > 0:
            to_id = random.sample(environment.network.edges(from_id), 1)
            # Determine the key value of the other household along edge
            to_index = to_id[0][1]
            # Get household identifier corresponding edge
            to_household = environment.get_agent_by_id(G[to_index])
            # Payment is a random uniform proportion of the households positive balance
            if self.balance("assets") > 0.0:
                payment = self.balance("assets") * random.uniform(0.2, 0.7)
                # Payment to household that is a customer of a different bank
                # Prefernce for CBDC transactions
                if to_household.bank_acc != self.bank_acc:
                    # If payment shock is less than CBDC balance, full amount paid in CBDC
                    if payment < self.balance("cbdc"):
                        tranx = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household.identifier, "bank_to" : "central_bank", "amount" : payment, "time" : time}
                        environment.get_agent_by_id("central_bank").make_cbdc_payment(environment, tranx, time)
                        environment.cbdc_payments += payment
                        environment.total_payments += payment
                    # If payment shock greater than CBDC balance, all CBDC paid and remainder paid with deposits
                    elif payment > self.balance("cbdc"):
                        if payment < (self.balance("cbdc") + self.balance("bank_notes")):
                            # CBDC portion
                            cbdc_portion = self.balance("cbdc")
                            tranx_cbdc = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household.identifier, "bank_to" : "central_bank", "amount" : cbdc_portion, "time" : time}
                            environment.get_agent_by_id("central_bank").make_cbdc_payment(environment, tranx_cbdc, time)
                            environment.cbdc_payments += cbdc_portion
                            # Bank Notes Portion
                            amount_remainder = payment - cbdc_portion
                            tranx_bank_notes = {"type_": "bank_notes", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : to_household.identifier, "bank_to" : to_household.bank_acc, "amount" : amount_remainder, "time" : time}
                            environment.get_agent_by_id("central_bank").make_bank_notes_payment(environment, tranx_bank_notes, time)
                            environment.total_payments += payment
                        elif payment > (self.balance("cbdc") + self.balance("bank_notes")):
                            # CBDC portion
                            cbdc_portion = self.balance("cbdc")
                            tranx_cbdc = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household.identifier, "bank_to" : "central_bank", "amount" : cbdc_portion, "time" : time}
                            environment.get_agent_by_id("central_bank").make_cbdc_payment(environment, tranx_cbdc, time)
                            environment.cbdc_payments += cbdc_portion
                            # Bank Notes Portion
                            bank_notes_portion = self.balance("bank_notes")
                            tranx_bank_notes = {"type_": "bank_notes", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : to_household.identifier, "bank_to" : to_household.bank_acc, "amount" : bank_notes_portion, "time" : time}
                            environment.get_agent_by_id("central_bank").make_bank_notes_payment(environment, tranx_bank_notes, time)
                            # Deposits Portion
                            amount_remainder = payment - cbdc_portion - bank_notes_portion
                            tranx_deposits = {"type_": "deposits", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : to_household.identifier, "bank_to" : to_household.bank_acc, "amount" : amount_remainder, "time" : time}
                            environment.get_agent_by_id(self.bank_acc).make_payment(environment, tranx_deposits, time)
                            environment.deposits_payments += amount_remainder
                            # Record total payment value
                            environment.total_payments += payment

                # Payment to household that is a customer of the same bank
                # Prefernce for deposits transactions
                elif to_household.bank_acc == self.bank_acc:
                    # If payment shock is less than deposits balance, full amount paid in deposits
                    if payment < self.balance("deposits"):
                        tranx = {"type_": "deposits", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : to_household.identifier, "bank_to" : to_household.bank_acc, "amount" : payment, "time" : time}
                        environment.get_agent_by_id(self.bank_acc).make_payment(environment, tranx, time)
                        environment.deposits_payments += payment
                        # Record total payment value
                        environment.total_payments += payment
                    # If payment shock greater than deposits balance, all deposits paid and remainder paid with CBDC
                    elif payment > self.balance("deposits"):
                        if payment < (self.balance("deposits") + self.balance("cbdc")):
                            # Deposits Portion
                            deposits_portion = self.balance("deposits")
                            tranx_deposits = {"type_": "deposits", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : to_household.identifier, "bank_to" : to_household.bank_acc, "amount" : deposits_portion, "time" : time}
                            environment.get_agent_by_id(self.bank_acc).make_payment(environment, tranx_deposits, time)
                            environment.deposits_payments += deposits_portion
                            # CBDC portion
                            amount_remainder = payment - deposits_portion
                            tranx_cbdc = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household.identifier, "bank_to" : "central_bank", "amount" : amount_remainder, "time" : time}
                            environment.get_agent_by_id("central_bank").make_cbdc_payment(environment, tranx_cbdc, time)
                            environment.cbdc_payments += amount_remainder
                            # Record total payment value
                            environment.total_payments += payment
                        elif payment > (self.balance("deposits") + self.balance("cbdc")):
                            # Deposits Portion
                            deposits_portion = self.balance("deposits")
                            tranx_deposits = {"type_": "deposits", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : to_household.identifier, "bank_to" : to_household.bank_acc, "amount" : deposits_portion, "time" : time}
                            environment.get_agent_by_id(self.bank_acc).make_payment(environment, tranx_deposits, time)
                            environment.deposits_payments += deposits_portion
                            # CBDC portion
                            cbdc_portion = self.balance("cbdc")
                            tranx_cbdc = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household.identifier, "bank_to" : "central_bank", "amount" : cbdc_portion, "time" : time}
                            environment.get_agent_by_id("central_bank").make_cbdc_payment(environment, tranx_cbdc, time)
                            environment.cbdc_payments += cbdc_portion
                            # Bank Notes Portion
                            amount_remainder = payment - deposits_portion - cbdc_portion
                            tranx_bank_notes = {"type_": "bank_notes", "from_" : self.identifier, "bank_from": self.bank_acc, "to" : to_household.identifier, "bank_to" : to_household.bank_acc, "amount" : amount_remainder, "time" : time}
                            environment.get_agent_by_id("central_bank").make_bank_notes_payment(environment, tranx_bank_notes, time)
                            # Record total payment value
                            environment.total_payments += payment

                    
                

    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_new_savings
    # placeholder for a function determining savings size of a household
    # -------------------------------------------------------------------------
    def get_new_savings(self, low, high):
        pass
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # check_consistency
    # checks whether the assets and liabilities have the same total value
    # the types of transactions that make up assets and liabilities is
    # controlled by the lists below
    # NOT IMPLEMENTED FOR HOUSEHOLD YET, NEED TO FILL assets & liabilities
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
        return super(Household, self).get_account(type_)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_account_num_transactions
    # returns the number of transactions of a given type
    # -------------------------------------------------------------------------
    def get_account_num_transactions(self,  type_):
        return super(Household, self).get_account_num_transactions(type_)
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
    def add_transaction(self, from_id,  to_id,  amount, environment):
        from src.transaction import Transaction
        transaction = Transaction()
        transaction.this_transaction(from_id, to_id, amount)
        transaction.add_transaction(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # clear_accounts
    # removes all transactions from bank's accounts
    # only for testing, the one in transaction should be used in production
    # -------------------------------------------------------------------------
    def clear_accounts(self):
        super(Household, self).clear_accounts()
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # purge_accounts
    # removes worthless transactions from bank's accounts
    # -------------------------------------------------------------------------
    def purge_accounts(self, environment):
        super(Household, self).purge_accounts(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_transactions_from_file
    # reads transactions from the config file to the household's accounts
    # -------------------------------------------------------------------------
    def get_transactions_from_file(self, filename, environment):
        super(Household, self).get_transactions_from_file(filename, environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __getattr__
    # if the attribute isn't found by Python we tell Python
    # to look for it first in parameters and then in state variables
    # which allows for directly fetching parameters from the Household
    # i.e. household.active instead of a bit more bulky
    # household.parameters["active"]
    # makes sure we don't have it in both containers, which
    # would be bad practice [provides additional checks]
    # -------------------------------------------------------------------------
    def __getattr__(self, attr):
        return super(Household, self).__getattr__(attr)
    # -------------------------------------------------------------------------