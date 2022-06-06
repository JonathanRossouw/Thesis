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
    assets = []
    liabilities = []

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
        self.assets = ["deposits", "bank_notes", "receivables"] #self.assets = ["equity_firm", "equity_bank", "deposits", "cbdc", "bank_notes"]
        self.liabilities = ["loans"]
        self.equity_firm = 0.0
        self.equity_bank = 0.0
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
                elif name == "firm_acc":
                    self.parameters[name] = value
                else:
                    self.parameters[name] = float(value)

        except:
            logging.error("    ERROR: %s could not be parsed",  household_filename)
    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # hh_asset_endowment
    # Household is endowed bank notes from central bank equal to wealth.
    # Household creates deposits using bank notes at bank equal to endowed wealth. 
    # Household then determines level of liquid deposits for the month, the remainder of deposits
    # is evenly split between firm and bank capital which
    # -------------------------------------------------------------------------
    def hh_asset_endowment(self, environment, time):
        import random
        from numpy import floor
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        firm_acc = list(environment.employment_network.adj[self.identifier])[0]
        firm_bank_acc = list(environment.bank_network.adj[firm_acc])[0]
        # Create bank notes equal to total endowed wealth
        bank_notes = self.wealth 
        endowment_tranx = {"type_": "bank_notes", "from_" : self.identifier, "bank_from": "central_bank", "to" : self.identifier, "bank_to" : "central_bank", "amount" : bank_notes, "time" : time}
        environment.central_bank[0].initialize_bank_notes(environment, endowment_tranx, time)


        # Determine asset allocation
        liquid_deposits = floor(30 * round(random.uniform(0.6, 1.6), 2))
        # Remainder of wealth divided between firm and bank capital
        equity_firm_amount = floor((bank_notes - liquid_deposits)/2)
        equity_bank_amount = bank_notes - liquid_deposits - equity_firm_amount
        # Capitalize banks
        equity_bank_tranx = {"type_": "equity_bank", "from_" : bank_acc, "bank_from": bank_acc, "to" : self.identifier, "bank_to" : bank_acc, "amount" : equity_bank_amount, "time" : time}
        environment.get_agent_by_id(bank_acc).bank_capitalize(environment, equity_bank_tranx, time)
        self.equity_bank = equity_bank_amount
        # Capitalize firms
        equity_firm_tranx = {"type_": "equity_firm", "from_" : firm_acc, "to" : self.identifier, "amount" : equity_firm_amount, "time" : time}
        environment.get_agent_by_id(firm_acc).firm_capitalize(environment, equity_firm_tranx, time)
        self.equity_firm = equity_firm_amount
        # Allocate Endowment and create bank balance
        endowment_tranx = {"type_": "deposits", "from_" : self.identifier, "bank_from": bank_acc, "to" : self.identifier, "bank_to" : bank_acc, "amount" : liquid_deposits, "time" : time}
        environment.get_agent_by_id(bank_acc).bank_notes_to_deposits(environment, endowment_tranx, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # deposits_payment(self, environment, tranx, time)
    # make payment using deposits with bank
    # -------------------------------------------------------------------------
    def deposits_payment(self, environment, tranx, time):
        deposits_remain = self.get_account("deposits")
        environment.number_of_deposits += 1
        # If transaction amount is greater than remaining deposits, household takes
        # out new loan for residual amount
        if tranx["amount"] > deposits_remain:
            loan_amount = tranx["amount"] - deposits_remain
            # New loan
            self.loan_new(environment, loan_amount, time)
            # Request deposit payment with bank
            bank_acc = list(environment.bank_network.adj[self.identifier])[0]
            environment.get_agent_by_id(bank_acc).make_payment(environment, tranx, time)
        else: 
            # Request deposit payment with bank
            bank_acc = list(environment.bank_network.adj[self.identifier])[0]
            environment.get_agent_by_id(bank_acc).make_payment(environment, tranx, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # cbdc_payment(self, environment, tranx, time)
    # make payment using deposits with bank
    # -------------------------------------------------------------------------
    def cbdc_payment(self, environment, tranx, time):
        # Request CBDC payment with Central Bank
        environment.get_agent_by_id("central_bank").make_cbdc_payment(environment, tranx, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_notes_payment(self, environment, tranx, time)
    # make payment using deposits with bank
    # -------------------------------------------------------------------------
    def bank_notes_payment(self, environment, tranx, time):
        # Request CBDC payment with Central Bank
        environment.get_agent_by_id("central_bank").make_bank_notes_payment(environment, tranx, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # loan_repay
    # household repays loans
    # -------------------------------------------------------------------------
    def loan_repay(self, environment, loan_amount, time):
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        loan_tranx = {"type_": "loans", "from_" : self.identifier, "bank_from": bank_acc, "to" : self.identifier, "bank_to" : bank_acc, "amount" : loan_amount, "time" : time}
        environment.get_agent_by_id(bank_acc).repay_loan(environment, loan_tranx)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # loan_new
    # household takes out new loans
    # -------------------------------------------------------------------------
    def loan_new(self, environment, loan_amount, time):
        bank_acc = list(environment.bank_network.adj[self.identifier])[0]
        loan_tranx = {"type_": "loans", "from_" : self.identifier, "bank_from": bank_acc, "to" : bank_acc, "bank_to" : bank_acc, "amount" : loan_amount, "time" : time}
        environment.get_agent_by_id(bank_acc).new_loan(environment, loan_tranx)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # get_new_savings
    # placeholder for a function determining savings size of a household
    # -------------------------------------------------------------------------
    def get_new_savings(self, low, high):
        pass
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # balance_sheet
    # returns balance sheet of agent
    # -------------------------------------------------------------------------
    def balance_sheet(self):
        balance_sheet = {}
        assets = {}
        liabilities = {}
        for item in self.assets:
            assets[item] = round(self.get_account(item), 5)
        for item in self.liabilities:
            liabilities[item] = round(self.get_account(item), 5)
        assets["equity_firm"] = self.equity_firm
        assets["equity_bank"] = self.equity_bank
        balance_sheet["assets"] = assets
        balance_sheet["liabilities"] = liabilities
        balance_sheet = {self.identifier: balance_sheet}
        return balance_sheet
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # check_npv
    # check net present value given as assets minus liabilities
    # -------------------------------------------------------------------------
    def check_npv(self):
        # Check net present value given as assets minus liabilities
        balance_sheet = self.balance_sheet()
        assets_total = sum(balance_sheet[self.identifier]["assets"].values())
        liabilities_total= sum(balance_sheet[self.identifier]["liabilities"].values())
        npv = round(assets_total - liabilities_total, 1)
        return {self.identifier: {"npv": npv}}
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
        return volume
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

    # -------------------------------------------------------------------------
    # # initiate_payment
    # # initiate payment and details of payment
    # # Payment amount is random portion of total assets (deposits + CBDC)
    # # Payment to HH with same bank, preference for deposits, if payment less than 
    # # deposits balance, pay only in deposits, otherwise pay all deposits and 
    # # rest with cbdc.
    # # Payment to HH with different bank, preference for CBDC, if payment less than  
    # # CBDC balance, pay only in CBDC, otherwise pay all CBDC and rest with deposits
    # # -------------------------------------------------------------------------
    # def initiate_payment(self, environment, time):
    #     import networkx as nx
    #     import random
    #     bank_acc = list(environment.bank_network.adj[self.identifier])[0]
    #     # Select random edge from household making payments edges
    #     if len(environment.social_network.edges(self.identifier)) > 0:
    #         to_household = random.sample(list(environment.social_network.edges(self.identifier)), 1)[0][1]
    #         to_bank_acc = list(environment.bank_network.adj[to_household])[0]
    #         # Payment is a random uniform proportion of the households positive balance
    #         total_assets = self.get_account("deposits") + self.get_account("cbdc") + self.get_account("bank_notes")
    #         total_acceptable_equity = 0.25 * self.equity

    #         if total_assets > 0.0 and total_acceptable_equity >0.0:
    #             payment = total_assets * random.uniform(0.2, 0.7) - total_acceptable_equity
    #             # Transfer equity between households representing expense or income from transaction
    #             equity_tranx = {"type_": "equity", "from_" : self.identifier, "to" : to_household, "amount" : payment, "time" : time}
    #             environment.new_transaction(type_=equity_tranx["type_"], asset='', from_=equity_tranx["to"], to=equity_tranx["from_"], amount=equity_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1) 
    #             print(f"{self.identifier} transferred {payment} units of equity to {to_household} at time {time}.")
    #             # Payment to household that is a customer of a different bank
    #             # Prefernce for CBDC transactions
    #             if to_bank_acc != bank_acc:
    #                 # If payment shock is less than CBDC balance, full amount paid in CBDC
    #                 if payment < self.get_account("cbdc"):
    #                     tranx = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household, "bank_to" : "central_bank", "amount" : payment, "time" : time}
    #                     self.cbdc_payment(environment, tranx, time)
    #                     environment.cbdc_payments += payment
    #                     environment.total_payments += payment
                        
    #                 # If payment shock greater than CBDC balance, all CBDC paid and remainder paid with deposits
    #                 elif payment > self.get_account("cbdc"):
    #                     if payment < (self.get_account("cbdc") + self.get_account("bank_notes")):
    #                         # CBDC portion
    #                         cbdc_portion = self.get_account("cbdc")
    #                         tranx_cbdc = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household, "bank_to" : "central_bank", "amount" : cbdc_portion, "time" : time}
    #                         self.cbdc_payment(environment, tranx_cbdc, time)
    #                         environment.cbdc_payments += cbdc_portion
    #                         # Bank Notes Portion
    #                         amount_remainder = payment - cbdc_portion
    #                         tranx_bank_notes = {"type_": "bank_notes", "from_" : self.identifier, "bank_from": bank_acc, "to" : to_household, "bank_to" : to_bank_acc, "amount" : amount_remainder, "time" : time}
    #                         self.bank_notes_payment(environment, tranx_bank_notes, time)
    #                         environment.total_payments += payment

    #                     elif payment > (self.get_account("cbdc") + self.get_account("bank_notes")):
    #                         # CBDC portion
    #                         cbdc_portion = self.get_account("cbdc")
    #                         tranx_cbdc = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household, "bank_to" : "central_bank", "amount" : cbdc_portion, "time" : time}
    #                         self.cbdc_payment(environment, tranx_cbdc, time)
    #                         environment.cbdc_payments += cbdc_portion
    #                         # Bank Notes Portion
    #                         bank_notes_portion = self.get_account("bank_notes")
    #                         tranx_bank_notes = {"type_": "bank_notes", "from_" : self.identifier, "bank_from": bank_acc, "to" : to_household, "bank_to" : to_bank_acc, "amount" : bank_notes_portion, "time" : time}
    #                         self.bank_notes_payment(environment, tranx_bank_notes, time)
    #                         # Deposits Portion
    #                         amount_remainder = payment - cbdc_portion - bank_notes_portion
    #                         tranx_deposits = {"type_": "deposits", "from_" : self.identifier, "bank_from": bank_acc, "to" : to_household, "bank_to" : to_bank_acc, "amount" : amount_remainder, "time" : time}
    #                         self.deposits_payment(environment, tranx_deposits, time)
    #                         environment.deposits_payments += amount_remainder
    #                         # Record total payment value
    #                         environment.total_payments += payment

    #             # Payment to household that is a customer of the same bank
    #             # Prefernce for deposits transactions
    #             elif to_bank_acc == bank_acc:
    #                 # If payment shock is less than deposits balance, full amount paid in deposits
    #                 if payment < self.get_account("deposits"):
    #                     tranx = {"type_": "deposits", "from_" : self.identifier, "bank_from": bank_acc, "to" : to_household, "bank_to" : to_bank_acc, "amount" : payment, "time" : time}
    #                     self.deposits_payment(environment, tranx, time)
    #                     environment.deposits_payments += payment
    #                     # Record total payment value
    #                     environment.total_payments += payment
    #                 # If payment shock greater than deposits balance, all deposits paid and remainder paid with CBDC
    #                 elif payment > self.get_account("deposits"):
    #                     if payment < (self.get_account("deposits") + self.get_account("cbdc")):
    #                         # Deposits Portion
    #                         deposits_portion = self.get_account("deposits")
    #                         tranx_deposits = {"type_": "deposits", "from_" : self.identifier, "bank_from": bank_acc, "to" : to_household, "bank_to" : to_bank_acc, "amount" : deposits_portion, "time" : time}
    #                         self.deposits_payment(environment, tranx_deposits, time)
    #                         environment.deposits_payments += deposits_portion
    #                         # CBDC portion
    #                         amount_remainder = payment - deposits_portion
    #                         tranx_cbdc = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household, "bank_to" : "central_bank", "amount" : amount_remainder, "time" : time}
    #                         self.cbdc_payment(environment, tranx_cbdc, time)
    #                         environment.cbdc_payments += amount_remainder
    #                         # Record total payment value
    #                         environment.total_payments += payment
    #                     elif payment > (self.get_account("deposits") + self.get_account("cbdc")):
    #                         # Deposits Portion
    #                         deposits_portion = self.get_account("deposits")
    #                         tranx_deposits = {"type_": "deposits", "from_" : self.identifier, "bank_from": bank_acc, "to" : to_household, "bank_to" : to_bank_acc, "amount" : deposits_portion, "time" : time}
    #                         self.deposits_payment(environment, tranx_deposits, time)
    #                         environment.deposits_payments += deposits_portion
    #                         # CBDC portion
    #                         cbdc_portion = self.get_account("cbdc")
    #                         tranx_cbdc = {"type_": "cbdc", "from_" : self.identifier, "bank_from": "central_bank", "to" : to_household, "bank_to" : "central_bank", "amount" : cbdc_portion, "time" : time}
    #                         self.cbdc_payment(environment, tranx_cbdc, time)
    #                         environment.cbdc_payments += cbdc_portion
    #                         # Bank Notes Portion
    #                         amount_remainder = payment - deposits_portion - cbdc_portion
    #                         tranx_bank_notes = {"type_": "bank_notes", "from_" : self.identifier, "bank_from": bank_acc, "to" : to_household, "bank_to" : to_bank_acc, "amount" : amount_remainder, "time" : time}
    #                         self.bank_notes_payment(environment, tranx_bank_notes, time)
    #                         # Record total payment value
    #                         environment.total_payments += payment
    # # -------------------------------------------------------------------------