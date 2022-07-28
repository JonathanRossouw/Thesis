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
# class CentralBank
#
# ============================================================================


class CentralBank(BaseAgent):
    #
    #
    # VARIABLES
    #
    #

    identifier = ""  # identifier of the central bank
    parameters = {}  # parameters of the central bank
    state_variables = {}  # state variables of the central bank
    accounts = []  # all accounts of the central bank (filled with transactions)
    assets = []
    liabilities = []
    bank_accounts = {}

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
        super(CentralBank, self).set_identifier(value)

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, value):
        super(CentralBank, self).set_parameters(value)

    def get_state_variables(self):
        return self.state_variables

    def set_state_variables(self, value):
        super(CentralBank, self).set_state_variables(value)

    def append_parameters(self, value):
        super(CentralBank, self).append_parameters(value)

    def append_state_variables(self, value):
        super(CentralBank, self).append_state_variables(value)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # functions needed to make CentralBank() hashable
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
        self.identifier = ""  # identifier of the central bank
        self.parameters = {}  # parameters of the central bank
        self.state_variables = {}  # state variables of the central bank
        self.accounts = []  # all accounts of the bank (filled with transactions)
        # DO NOT EVER ASSIGN PARAMETERS BY HAND AS DONE BELOW IN PRODUCTION CODE
        # ALWAYS READ THE PARAMETERS FROM CONFIG FILES
        # OR USE THE FUNCTIONS FOR SETTING / CHANGING VARIABLES
        # CONVERSELY, IF YOU WANT TO READ THE VALUE, DON'T USE THE FULL NAMES
        # INSTEAD USE __getattr__ POWER TO CHANGE THE COMMAND FROM
        # instance.static_parameters["xyz"] TO instance.xyz - THE LATTER IS PREFERRED
        self.parameters["interest_rate_cb_loans"] = 0.0  # interest rate on loans
        self.assets = ["loans_central_bank"]
        self.liabilities = ["reserves", "bank_notes", "open_market_operations"]
        self.bank_accounts = {}
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # sell_open_market_operations
    # transfer open_market_operations to bank for reserves
    # -------------------------------------------------------------------------
    def sell_open_market_operations(self, environment, tranx, time):
        # Create reserves for bank
        environment.new_transaction(type_="reserves", asset='', from_= tranx["bank_to"], to = tranx["bank_from"], amount = tranx["amount"], interest=environment.reserves_interest, maturity=0, time_of_default=-1)
        # Create Open Market Operations agreement with Bank
        environment.new_transaction(type_="open_market_operations", asset='', from_= tranx["bank_from"], to = tranx["bank_to"], amount = tranx["amount"], interest=environment.open_market_operations_interest, maturity=0, time_of_default=-1)
        #print(f"Central Bank sold {tranx['amount']} of open market operations to {tranx['bank_to']}")
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # purchase_open_market_operations
    # transfer reserves to bank for open_market_operations
    # -------------------------------------------------------------------------
    def purchase_open_market_operations(self, environment, tranx, time):
        # Create reserves for bank
        environment.new_transaction(type_="reserves", asset='', from_= tranx["bank_from"], to = tranx["bank_to"], amount = tranx["amount"], interest=environment.reserves_interest, maturity=0, time_of_default=-1)
        # Create Open Market Operations agreement with Bank
        environment.new_transaction(type_="open_market_operations", asset='', from_= tranx["bank_to"], to = tranx["bank_from"], amount = tranx["amount"], interest=environment.open_market_operations_interest, maturity=0, time_of_default=-1)
        #print(f"Central Bank purchased {tranx['amount']} of open market operations from {tranx['bank_to']}")
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # initialize_bank_notes
    # takes in transaction details from household and makes payment
    # -------------------------------------------------------------------------
    def initialize_bank_notes(self, environment, tranx, time):
        # Transfer funds from central bank to household
        environment.new_transaction(type_="bank_notes", asset='', from_="central_bank", to=tranx["to"], amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
		# We print the action of selling to the screen
        #print(f"\n {tranx['to']} initialize with {tranx['amount']} bank notes")
        #print(self.balance_sheet())
        #logging.info("  payments made on step: %s",  time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # initialize_reserves
    # takes in transaction details from household and makes payment
    # -------------------------------------------------------------------------
    def initialize_reserves(self, environment, tranx, time):
        # Transfer funds from bank to central bank
        environment.new_transaction(type_="bank_notes", asset='', from_=tranx["from_"], to="central_bank", amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        environment.new_transaction(type_="reserves", asset='', from_="central_bank", to=tranx["from_"], amount=tranx["amount"], interest=environment.reserves_interest, maturity=0, time_of_default=-1)
		# We print the action of selling to the screen
        #print(f"\n {tranx['to']} initialize with {tranx['amount']} reserves")
        #print(self.balance_sheet())
        #logging.info("  payments made on step: %s",  time)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # make_bank_notes_payment
    # takes in transaction details from household and makes payment
    # -------------------------------------------------------------------------
    def make_bank_notes_payment(self, environment, tranx, time):
		# Transfer funds from household to central bank to household
        environment.new_transaction(type_="bank_notes", asset='', from_=tranx["from_"], to="central_bank", amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        # Transfer funds from central bank to household
        environment.new_transaction(type_="bank_notes", asset='', from_="central_bank", to=tranx["to"], amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
		# We print the action of selling to the screen
        #print(f"\n{tranx['from_']}s paid {tranx['amount']}f of cbdc to {self.identifier}s for {tranx['to']}s at time {tranx['time']}d.")
        #print(f"\n{self.identifier}s settled {tranx['amount']}f of cbdc to {tranx['to']}s at time {tranx['time']}d.")
        #print(self.balance_sheet())
        #logging.info("  payments made on step: %s",  time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # rgts_payment
    # takes in transaction details between banks
    # -------------------------------------------------------------------------
    def rgts_payment(self, environment, tranx, time):
		# Transfer funds from central bank to bank
        environment.new_transaction(type_="reserves", asset='', from_=tranx["bank_from"], to=tranx["bank_to"], amount=tranx["amount"], interest=environment.reserves_interest, maturity=0, time_of_default=-1)
        #print(f"\n RTGS payment of {tranx['amount']} of reserves from {tranx['bank_from']} to {tranx['bank_to']} at time {time}d.")
        #print(self.balance_sheet())
        #logging.info("  payments made on step: %s",  time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # issue_central_bank_loan
    # bank issues loan to another bank
    # -------------------------------------------------------------------------
    def issue_central_bank_loan(self, environment, loan_tranx, time):
        # Create loan agreement with household
        environment.new_transaction(type_="loans_central_bank", asset='', from_= loan_tranx["bank_from"], to = self.identifier, amount = loan_tranx["amount"], interest=environment.loans_central_bank_interest, maturity=0, time_of_default=-1)
        if loan_tranx["bank_from"] in loan_tranx:
            self.bank_accounts[loan_tranx["bank_from"]]["loans_central_bank"] += loan_tranx["amount"]
        elif loan_tranx["bank_from"] not in loan_tranx:
            self.bank_accounts[loan_tranx["bank_from"]] = {"loans_central_bank": loan_tranx["amount"]}
        # Transfer reserves
        reserves_tranx = {"type_": "reserves", "amount" : loan_tranx["amount"], "bank_from":self.identifier, "bank_to":loan_tranx["bank_from"], "time" : time}
        self.rgts_payment(environment, reserves_tranx, time)    
        #print(f"\n {loan_tranx['bank_from']} took out new loan of {loan_tranx['amount']} at {self.identifier}")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # settle_central_bank_loan
    # settle loan issued by central bank to bank
    # -------------------------------------------------------------------------
    def settle_central_bank_loan(self, environment, loan_tranx, time):
        # Reverse loan transaction
        environment.new_transaction(type_="loans_central_bank", asset='', from_= self.identifier, to = loan_tranx["bank_to"], amount = loan_tranx["amount"], interest=environment.loans_central_bank_interest, maturity=0, time_of_default=-1)
        del self.bank_accounts[loan_tranx["bank_to"]]["loans_central_bank"]
        # Transfer reserves as payment
        reserves_tranx = {"type_": "reserves", "amount" : loan_tranx["amount"], "bank_from":loan_tranx["bank_to"], "bank_to": self.identifier, "time" : time}
        self.rgts_payment(environment, reserves_tranx, time)    
        #print(f"\n {loan_tranx['bank_to']} repaid loan of {loan_tranx['amount']} at {self.identifier} in {time}")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # __del__
    # -------------------------------------------------------------------------
    def __del__(self):
        pass
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __str__
    # returns a string describing the central bank and its properties
    # based on the implementation in the abstract class BaseAgent
    # but adds the type of agent (bank) and lists all transactions
    # -------------------------------------------------------------------------
    def __str__(self):
        bank_string = super(CentralBank, self).__str__()
        bank_string = bank_string.replace("\n", "\n    <type value='central_bank'>\n", 1)
        text = "\n"
        text = text + "  </agent>"
        return bank_string.replace("\n  </agent>", text, 1)
    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_parameters_from_file
    # reads the specified config file given the environment
    # and sets parameters to the ones found in the config file
    # the config file should be an xml file that looks like the below:
    # <central_bank identifier='string'>
    #     <parameter name='string' value='string'></parameter>
    # </central_bank>
    # -------------------------------------------------------------------------
    def get_parameters_from_file(self,  bank_filename, environment):
        super(CentralBank, self).get_parameters_from_file(bank_filename, environment)
    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # balance_sheet
    # returns balance sheet of agent
    # -------------------------------------------------------------------------
    def balance_sheet(self):
        balance_sheet = {}
        assets = {}
        liabilities = {}
        for item in self.assets:
            assets[item] = self.get_account(item)
        for item in self.liabilities:
            liabilities[item] = self.get_account(item)

        balance_sheet["assets"] = assets
        balance_sheet["liabilities"] = liabilities
        balance_sheet = {self.identifier: balance_sheet}
        return balance_sheet

    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # check_consistency
    # checks whether the assets and liabilities have the same total value
    # -------------------------------------------------------------------------
    def check_consistency(self):
        import numpy as np 
        balance_sheet = self.balance_sheet()
        assets_round = round(sum(balance_sheet[self.identifier]["assets"].values()), 0)
        liabilities_floor = round(sum(balance_sheet[self.identifier]["liabilities"].values()), 0)
        balance_sheet = self.balance_sheet()
        assets = np.floor(sum(balance_sheet[self.identifier]["assets"].values()))
        liabilities = np.floor(sum(balance_sheet[self.identifier]["liabilities"].values()))

        return (assets == liabilities or assets_round == liabilities_floor)
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
        return super(CentralBank, self).get_account_num_transactions(type_)
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
    def add_transaction(self, type_, asset,  from_id,  to_id,  amount,  interest,  maturity, time_of_default, environment):
        from src.transaction import Transaction
        transaction = Transaction()
        transaction.add_transaction(type_, asset, from_id,  to_id,  amount,  interest,  maturity,  time_of_default, environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # clear_accounts
    # removes all transactions from central bank's accounts
    # only for testing, the one in transaction should be used in production
    # -------------------------------------------------------------------------
    def clear_accounts(self, environment):
        super(CentralBank, self).clear_accounts(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # purge_accounts
    # removes worthless transactions from central bank's accounts
    # -------------------------------------------------------------------------
    def purge_accounts(self, environment):
        super(CentralBank, self).purge_accounts(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_transactions_from_file
    # reads transactions from the config file to the central bank's accounts
    # -------------------------------------------------------------------------
    def get_transactions_from_file(self, filename, environment):
        super(CentralBank, self).get_transactions_from_file(filename, environment)
    # -------------------------------------------------------------------------

    # __getattr__
    # if the attribute isn't found by Python we tell Python
    # to look for it first in parameters and then in state variables
    # which allows for directly fetching parameters from the Bank
    # i.e. bank.active instead of a bit more bulky
    # bank.parameters["active"]
    # makes sure we don't have it in both containers, which
    # would be bad practice [provides additional checks]
    # -------------------------------------------------------------------------
    def __getattr__(self, attr):
        return super(CentralBank, self).__getattr__(attr)
    # -------------------------------------------------------------------------
