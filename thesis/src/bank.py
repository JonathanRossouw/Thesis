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

#from _typeshed import OpenTextModeUpdating
import logging
from abm_template.src.baseagent import BaseAgent

# ============================================================================
#
# class Bank
#
# ============================================================================


class Bank(BaseAgent):
    #
    #
    # VARIABLES
    #
    #

    identifier = ""  # identifier of the specific bank
    parameters = {}  # parameters of the specific bank
    state_variables = {}  # state variables of the specific bank
    accounts = []  # all accounts of a bank (filled with transactions)
    store = []  # store transaction info
    assets = []
    liabilities = []
    bank_accounts = []
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
        super(Bank, self).set_identifier(value)

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, value):
        super(Bank, self).set_parameters(value)

    def get_state_variables(self):
        return self.state_variables

    def set_state_variables(self, value):
        super(Bank, self).set_state_variables(value)

    def append_parameters(self, value):
        super(Bank, self).append_parameters(value)

    def append_state_variables(self, value):
        super(Bank, self).append_state_variables(value)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # functions needed to make Bank() hashable
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
        self.identifier = ""  # identifier of the specific bank
        self.parameters = {}  # parameters of the specific bank
        self.state_variables = {}  # state variables of the specific bank
        self.accounts = []  # all accounts of a bank (filled with transactions)
        self.store = [] # store transaction info
        # DO NOT EVER ASSIGN PARAMETERS BY HAND AS DONE BELOW IN PRODUCTION CODE
        # ALWAYS READ THE PARAMETERS FROM CONFIG FILES
        # OR USE THE FUNCTIONS FOR SETTING / CHANGING VARIABLES
        # CONVERSELY, IF YOU WANT TO READ THE VALUE, DON'T USE THE FULL NAMES
        # INSTEAD USE __getattr__ POWER TO CHANGE THE COMMAND FROM
        # instance.static_parameters["xyz"] TO instance.xyz - THE LATTER IS PREFERRED
        self.parameters["interest_rate_loans"] = 0.0  # interest rate on loans
        self.parameters["interest_rate_deposits"] = 0.0  # interest rate on deposits
        self.parameters["active"] = 0  # this is a control parameter checking whether bank is active
        self.parameters["bank"] = 0  # this is a control parameter checking whether bank is active
        self.assets = ["loans", "reserves", "bank_notes"]
        self.liabilities = ["deposits", "receivables"] #self.liabilities = ["capital_bank", "deposits", "open_market_operations", "ach_deposits"]
        self.bank_accounts = {}
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __del__
    # -------------------------------------------------------------------------
    def __del__(self):
        pass
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __str__
    # returns a string describing the bank and its properties
    # based on the implementation in the abstract class BaseAgent
    # but adds the type of agent (bank) and lists all transactions
    # -------------------------------------------------------------------------
    def __str__(self):
        bank_string = super(Bank, self).__str__()
        bank_string = bank_string.replace("\n", "\n    <type value='bank'>\n", 1)
        text = "\n"
        text = text + "  </agent>"
        return bank_string.replace("\n  </agent>", text, 1)
    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_parameters_from_file
    # reads the specified config file given the environment
    # and sets parameters to the ones found in the config file
    # the config file should be an xml file that looks like the below:
    # <bank identifier='string'>
    #     <parameter name='string' value='string'></parameter>
    # </bank>
    # -------------------------------------------------------------------------
    def get_parameters_from_file(self,  bank_filename, environment):
        super(Bank, self).get_parameters_from_file(bank_filename, environment)
    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_initialize(self, environment, tranx, time)
    # create accounts for deposits and loans for each household and firm at bank
    # bank is capitalized by equity from households
    # -------------------------------------------------------------------------
    def bank_initialize(self, environment):
        G = environment.bank_network #Get consumption network
        for agent in list(G.adj[self.identifier]):
            self.bank_accounts.update({agent : {"loans": 0, "deposits": 0, "receivables": 0}})

        self.assets.append("ach_payee_" + self.identifier)
        self.liabilities.append("ach_payer_" + self.identifier)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_capitalize(self, environment, tranx, time)
    # bank is capitalized by equity from households
    # -------------------------------------------------------------------------
    def bank_capitalize(self, environment, tranx, time):
        # Provide capital to bank
        environment.new_transaction(type_="equity_bank", asset='', from_= tranx["from_"], to = tranx["to"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        environment.new_transaction(type_="bank_notes", asset='', from_= tranx["to"], to = tranx["from_"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        print(self.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # initialize_reserves(self, environment, tranx, time)
    # bank deposits all bank notes at central bank for reserves
    # -------------------------------------------------------------------------
    def initialize_reserves(self, environment, time):
        # Transfer bank notes to CB fro reserves
        bank_notes = self.get_account("bank_notes")
        capital_bank_tranx = {"type_": "bank_notes", "from_" : self.identifier, "to" : "central_bank", "amount" : bank_notes, "time" : time}
        environment.central_bank[0].initialize_reserves(environment, capital_bank_tranx, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # new_loan
    # firm takes out loan to finance production
    # -------------------------------------------------------------------------
    def new_loan(self, environment, loan_tranx):
        # Create loan agreement with household
        environment.new_transaction(type_="loans", asset='', from_= loan_tranx["from_"], to = loan_tranx["bank_from"], amount = loan_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        self.bank_accounts[loan_tranx["from_"]]["loans"] += loan_tranx["amount"]
        # Open deposit account for household at bank
        environment.new_transaction(type_="deposits", asset='', from_= loan_tranx["bank_from"], to = loan_tranx["from_"], amount = loan_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        self.bank_accounts[loan_tranx["from_"]]["deposits"] += loan_tranx["amount"]
        print(f"\n {loan_tranx['from_']} took out new loan of {loan_tranx['amount']} at {loan_tranx['bank_from']}")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # repay_loan
    # firm repays loan for production
    # -------------------------------------------------------------------------
    def repay_loan(self, environment, loan_tranx):
        # Create loan agreement with household
        environment.new_transaction(type_="loans", asset='', from_= loan_tranx["bank_from"], to = loan_tranx["from_"], amount = loan_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        # Open deposit account for household at bank
        environment.new_transaction(type_="deposits", asset='', from_= loan_tranx["from_"], to = loan_tranx["bank_from"], amount = loan_tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        self.bank_accounts[loan_tranx["from_"]]["loans"] -= loan_tranx["amount"]
        print(f"\n {loan_tranx['from_']} repaid loan of {loan_tranx['amount']} at {loan_tranx['bank_from']}")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # bank_asset_allocation
    # bank determines reserves from number of households and loan amounts
    # calls Central Bank method to initialize reserves and Open Market 
    # Transactions to balance assets and liabilities
    # -------------------------------------------------------------------------
    def bank_allocate_reserves(self, environment):
        # Create reserves
        reserves_required = 0.2 * self.get_account("deposits")
        reserves_allocation = {"type_": "reserves", "from_": "central_bank", "to": self.identifier, "amount": reserves_required}
        environment.get_agent_by_id("central_bank").new_reserves(environment, reserves_allocation)
        print(f"\n{self.identifier} has {reserves_required} reserves, and {reserves_required} Open Market Operations")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # ach_deposits_collateral
    # Create deposits at ACH and provide collateral
    # -------------------------------------------------------------------------
    def ach_deposits_collateral(self, environment, time):
        # Create deposits equal to the maximimum amount of deposits expected to be paid
        # during single batching period. Collateral is equal to deposits. Negative deposits
        # is not allowed.
        ach_deposit_amount = self.get_account("deposits")
        ach_deposit = {"type_": "ach_deposits", "from_": "ach", "to": self.identifier, "amount": ach_deposit_amount}
        environment.new_transaction(type_=ach_deposit["type_"], asset='', from_= ach_deposit["from_"], to = ach_deposit["to"], amount = ach_deposit["amount"], interest=0.00, maturity=0, time_of_default=-1)
        # New collateral with loans
        ach_collateral_amount = ach_deposit_amount
        ach_collateral = {"type_": "loans", "from_": self.identifier, "to": "ach", "amount": ach_collateral_amount}
        environment.new_transaction(type_=ach_collateral["type_"], asset='', from_= ach_collateral["from_"], to = ach_collateral["to"], amount = ach_collateral["amount"], interest=0.00, maturity=0, time_of_default=-1)
        environment.get_agent_by_id("ach").collateral[self.identifier] = ach_collateral_amount
        # Ensure sufficient reserves
        new_reserves = ach_deposit_amount - self.get_account("reserves")
        if new_reserves > 0:
            reserve_tranx = {"type_": "reserves", "from_": "central_bank", "to": self.identifier, "amount": new_reserves}
            environment.get_agent_by_id("central_bank").new_reserves(environment, reserve_tranx)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # make_payment
    # takes in transaction details from household or firms and makes payment
    # -------------------------------------------------------------------------
    def make_payment(self, environment, tranx, time):
		# We print the action of transferring deposits
        print(f"\n{tranx['from_']}s paid {tranx['amount']} to {tranx['bank_from']} for {tranx['to']} at time {tranx['time']}.")
        # If payment is within bank, immediately debit and credit accounts
        if (tranx["bank_from"] == tranx["bank_to"]):
            # Transfer receipt from bank to household
            environment.new_transaction(type_="deposits", asset='', from_= tranx["from_"], to = tranx["to"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            self.bank_accounts[tranx["from_"]]["deposits"] -= tranx["amount"]
            self.bank_accounts[tranx["to"]]["deposits"] += tranx["amount"]
            print(f"\n {self.identifier} paid {tranx['amount']} to {tranx['to']} \n")


        # It payment is between banks, send transaction to ACH
        elif (tranx["bank_from"] != tranx["bank_to"]):
            # Household or firm paying credits their deposit account and their bank debits their deposit account
            environment.new_transaction(type_="deposits", asset='', from_=tranx["from_"], to=tranx["bank_from"], amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            self.bank_accounts[tranx["from_"]]["deposits"] -= tranx["amount"]
            # The transaction is sent to the ACH for batching
            environment.get_agent_by_id("ach").make_ach_payment(environment, tranx, time)
            print(f"\n {self.identifier} paid {tranx['amount']} to {tranx['to']} \n")
        environment.total_payments += tranx["amount"]
        environment.total_deposit_payments += tranx["amount"]
        #logging.info("  payments made on step: %s",  time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # make_ach_payment
    # takes in transaction details from household or firms and makes payment
    # -------------------------------------------------------------------------
    def make_ach_payment(self, environment, tranx, time):
		# We print the action of transferring deposits to batch
        print(f"\n{tranx['from_']}s paid {tranx['amount']} to {tranx['bank_from']} for {tranx['to']} at time {tranx['time']}.")
        # If payment is within bank, immediately debit and credit accounts
        if (tranx["bank_from"] == tranx["bank_to"]):
            # Transfer receipt from bank to household
            environment.new_transaction(type_="deposits", asset='', from_= tranx["from_"], to = tranx["to"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            print(f"\n {self.identifier} paid {tranx['amount']} to {tranx['to']} \n")
        # It payment is between banks, send transaction to ACH
        elif (tranx["bank_from"] != tranx["bank_to"]):
            # Household or firm paying credits their deposit account and their bank debits their deposit account
            environment.new_transaction(type_="deposits", asset='', from_=tranx["from_"], to=tranx["bank_from"], amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            # Store transaction for settling at bank receiving payment
            environment.get_agent_by_id(tranx["bank_to"]).store.append(tranx)
            # ACH includes transaction to batch
            environment.get_agent_by_id("ach").batches[tranx["bank_from"]].append(-tranx["amount"])
            environment.get_agent_by_id("ach").batches[tranx["bank_to"]].append(tranx["amount"])
            # Sender bank credits their ACH deposits account. ACH debits the sender bank's deposits account
            environment.new_transaction(type_="ach_deposits", asset='', from_= tranx["bank_from"], to = "ach", amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            # Receiving bank debits their ACH deposits account. ACH credits the receiving bank's deposits account
            environment.new_transaction(type_="ach_deposits", asset='', from_= "ach", to = tranx["bank_to"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        #print(self.balance_sheet())
        #logging.info("  payments made on step: %s",  time)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # settle_ach_payments
    # takes in transaction details from bank and makes payment to household
    # -------------------------------------------------------------------------
    def settle_ach_payments(self, environment, time):
        # Loop through bank accounts and determine which accounts have receivables
        for item in self.bank_accounts:
            receivables = self.bank_accounts[item]["receivables"]
            if receivables > 0:
                environment.new_transaction(type_="deposits", asset='', from_= self.identifier, to = item, amount = receivables, interest=0.00, maturity=0, time_of_default=-1)
                self.bank_accounts[item]["deposits"] += receivables
                environment.new_transaction(type_="receivables", asset='', from_= item, to = self.identifier, amount = receivables, interest=0.00, maturity=0, time_of_default=-1)
                self.bank_accounts[item]["receivables"] -= receivables
                
        # Take in transaction details and transfer amount to deposits of household
                print(f"{self.identifier} settled payment of {receivables} to {item} at time {time}.")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------


    # # -------------------------------------------------------------------------
    # # interbank_settle(environment, time)
    # # This function settles the transactions following the shock. If from and 
    # # to are at the same bank then transaction is settled. If different banks
    # # then only every fourth period is settled.
    # # -------------------------------------------------------------------------
    # def interbank_settle(self,  environment, time):
    #     # Settle payments by with banks
    #     # Iterate through stored transactions
    #     for tranx in self.store[:]:
	# 		# Settlement of funds between customers of bank each period
    #         if (tranx["bank_from"] == tranx["bank_to"]):
	# 			# Transfer receipt from bank to household
    #             environment.new_transaction(type_="deposits", asset='', from_= tranx["bank_from"], to = tranx["to"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
	# 			# Remove stored transaction
    #             self.store.remove(tranx)
	# 			# Print details of transaction
    #             print(f"\n{tranx['bank_from']}s transferred deposits of {tranx['amount']}f to {tranx['to']}s at time {time}d.")
    #             #print(self.balance_sheet())
			
	# 		# Batch payments for transactions between customers of bank with households
    #         # that are customers of different bank and settle every fourth period
    #         elif (time % environment.batch == 0):
    #             if self.get_account("reserves") < tranx["amount"]:
    #                 print(f"{self.identifier} required more reserves, since {self.get_account('reserves')} reserves is less than {tranx['amount']} loan amount")
    #                 # Increase reserves to finance loan
    #                 reserves_tranx = {"from_":"central_bank", "to":self.identifier, "amount":tranx["amount"]}
    #                 environment.get_agent_by_id("central_bank").new_reserves(environment, reserves_tranx)
    #             # Call method at central bank to continue transaction
    #             environment.get_agent_by_id("central_bank").rgts_payment(environment, tranx, time)
	# 			# Remove stored transaction
    #             self.store.remove(tranx)
	# 			# Print details of transaction
    #             print(f"\n{tranx['bank_from']}s RTGSed reserves of {tranx['amount']}f  to {'central_bank'}s at time {time}d.")
    #             #print(self.balance_sheet())
    # # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # cbdc_exchange
    # Household exchanges deposits at bank for cbdc at central bank
    # -------------------------------------------------------------------------
    def cbdc_exchange(self, environment, tranx, time):
        if tranx["to"] == "central_bank":
            # Decrease Deposits for household
            environment.new_transaction(type_="deposits", asset='', from_=tranx["from_"], to=tranx["bank_from"], amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            # Call Central Bank method to transfer Open Market Operations to Central Bank, CBDC to Household, Open Market
            # Transactions to Bank and Reserves to Bank
            environment.get_agent_by_id("central_bank").cbdc_settle(environment, tranx, time)
        elif tranx["to"] != "central_bank":
            # Decrease Deposits for household
            environment.new_transaction(type_="deposits", asset='', from_=tranx["bank_to"], to=tranx["to"], amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            # Call Central Bank method to transfer Open Market Operations to Central Bank, CBDC to Household, Open Market
            # Transactions to Bank and Reserves to Bank
            environment.get_agent_by_id("central_bank").cbdc_settle(environment, tranx, time)

    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_notes_purchase
    # Household exchanges deposits at bank for cbdc at central bank
    # -------------------------------------------------------------------------
    def bank_notes_to_deposits(self, environment, tranx, time):
            # Create deposits for household
            environment.new_transaction(type_="deposits", asset='', from_=tranx["bank_from"], to=tranx["from_"], amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            # Receive bank notes from household
            environment.new_transaction(type_="bank_notes", asset='', from_=tranx["from_"], to=tranx["bank_from"], amount=tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
            self.bank_accounts[tranx["from_"]]["deposits"] += tranx["amount"]
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
            assets[item] = self.get_account(item)
        for item in self.liabilities:
            liabilities[item] = self.get_account(item)

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
    # check_consistency
    # checks whether the assets and liabilities have the same total value
    # -------------------------------------------------------------------------
    def check_consistency(self):
        import numpy as np 
        balance_sheet = self.balance_sheet()
        assets_round = round(sum(balance_sheet[self.identifier]["assets"].values()), 0)
        liabilities_round = round(sum(balance_sheet[self.identifier]["liabilities"].values()), 0)
        balance_sheet = self.balance_sheet()
        assets_floor = np.floor(sum(balance_sheet[self.identifier]["assets"].values()))
        liabilities_floor = np.floor(sum(balance_sheet[self.identifier]["liabilities"].values()))

        return (assets_floor == liabilities_floor or assets_round == liabilities_round)
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
        return super(Bank, self).get_account_num_transactions(type_)
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
        transaction.this_transaction(type_, asset, from_id,  to_id,  amount,  interest,  maturity,  time_of_default)
        transaction.add_transaction(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # clear_accounts
    # removes all transactions from bank's accounts
    # only for testing, the one in transaction should be used in production
    # -------------------------------------------------------------------------
    def clear_accounts(self):
        super(Bank, self).clear_accounts()
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # purge_accounts
    # removes worthless transactions from bank's accounts
    # -------------------------------------------------------------------------
    def purge_accounts(self, environment):
        super(Bank, self).purge_accounts(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_transactions_from_file
    # reads transactions from the config file to the bank's accounts
    # -------------------------------------------------------------------------
    def get_transactions_from_file(self, filename, environment):
        super(Bank, self).get_transactions_from_file(filename, environment)
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
        return super(Bank, self).__getattr__(attr)
    # -------------------------------------------------------------------------
