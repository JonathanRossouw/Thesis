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
        self.assets = ["loans", "reserves", "bank_notes", "open_market_operations"]
        self.liabilities = ["deposits", "receivables", "loans_central_bank"] #self.liabilities = ["capital_bank", "deposits", "open_market_operations", "ach_deposits"]
        self.bank_accounts = {}
        self.equity_households = {}
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

        for bank in environment.banks: #Add interbank loans to assets
            if bank.identifier != self.identifier:
                self.assets.append("loans_interbank_" + bank.identifier)

        self.assets.append("ach_payee_" + self.identifier)
        self.liabilities.append("ach_payer_" + self.identifier)
        self.liabilities.append("loans_interbank_" + self.identifier)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_capitalize(self, environment, tranx, time)
    # bank is capitalized by equity from households
    # -------------------------------------------------------------------------
    def bank_capitalize(self, environment, tranx, time):
        # Provide capital to bank
        environment.new_transaction(type_="equity_bank", asset='', from_= tranx["from_"], to = tranx["to"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        environment.new_transaction(type_="bank_notes", asset='', from_= tranx["to"], to = tranx["from_"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        self.equity_households[tranx["to"]] = tranx["amount"]
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # initialize_reserves(self, environment, tranx, time)
    # bank deposits all bank notes at central bank for reserves
    # record the proportion of equity each household has in bank
    # -------------------------------------------------------------------------
    def initialize_reserves(self, environment, time):
        # Create record of proportions of equity each household owns
        total_equity = sum(self.equity_households.values())
        for val in self.equity_households:
            self.equity_households[val] = round(self.equity_households[val]/total_equity, 8)

        # Transfer bank notes to CB for reserves
        bank_notes = self.get_account("bank_notes")
        capital_bank_tranx = {"type_": "bank_notes", "from_" : self.identifier, "to" : "central_bank", "amount" : bank_notes, "time" : time}
        environment.central_bank[0].initialize_reserves(environment, capital_bank_tranx, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # new_loan
    # household or firm takes out loan
    # -------------------------------------------------------------------------
    def new_loan(self, environment, loan_tranx):
        # Create loan agreement with household
        environment.new_transaction(type_="loans", asset='', from_= loan_tranx["from_"], to = loan_tranx["bank_from"], amount = loan_tranx["amount"], interest=environment.loans_interest, maturity=0, time_of_default=-1)
        self.bank_accounts[loan_tranx["from_"]]["loans"] += loan_tranx["amount"]
        # Increase deposit for agent at bank
        environment.new_transaction(type_="deposits", asset='', from_= loan_tranx["bank_from"], to = loan_tranx["from_"], amount = loan_tranx["amount"], interest=environment.deposits_interest, maturity=0, time_of_default=-1)
        self.bank_accounts[loan_tranx["from_"]]["deposits"] += loan_tranx["amount"]
        #print(f"\n {loan_tranx['from_']} took out new loan of {loan_tranx['amount']} at {loan_tranx['bank_from']}")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # repay_loan
    # household or firm repays loan
    # -------------------------------------------------------------------------
    def repay_loan(self, environment, loan_tranx):
        # Create loan agreement with household
        environment.new_transaction(type_="loans", asset='', from_= loan_tranx["bank_from"], to = loan_tranx["from_"], amount = loan_tranx["amount"], interest=environment.loans_interest, maturity=0, time_of_default=-1)
        # Open deposit account for household at bank
        environment.new_transaction(type_="deposits", asset='', from_= loan_tranx["from_"], to = loan_tranx["bank_from"], amount = loan_tranx["amount"], interest=environment.deposits_interest, maturity=0, time_of_default=-1)
        self.bank_accounts[loan_tranx["from_"]]["loans"] -= loan_tranx["amount"]
        #print(f"\n {loan_tranx['from_']} repaid loan of {loan_tranx['amount']} at {loan_tranx['bank_from']}")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # new_loans_firm_capital
    # firm takes out loan for capital
    # -------------------------------------------------------------------------
    def new_loans_firm_capital(self, environment, loan_tranx, time):
        # Create loan agreement with firm
        environment.new_transaction(type_="loans", asset='', from_= loan_tranx["from_"], to = loan_tranx["bank_from"], amount = loan_tranx["amount"], interest=environment.loans_interest, maturity=0, time_of_default=-1)
        self.bank_accounts[loan_tranx["from_"]]["loans"] = loan_tranx["amount"]
        # Increase deposit for agent at bank
        environment.new_transaction(type_="deposits", asset='', from_= loan_tranx["bank_from"], to = loan_tranx["from_"], amount = loan_tranx["amount"], interest=environment.deposits_interest, maturity=0, time_of_default=-1)
        self.bank_accounts[loan_tranx["from_"]]["deposits"] += loan_tranx["amount"]
        #print(f"\n {loan_tranx['from_']} took out new loan of {loan_tranx['amount']} at {loan_tranx['bank_from']}")
        #print(self.balance_sheet())
        # Firm purchases capital using deposits
        environment.new_transaction(type_="deposits", asset='', from_= loan_tranx["from_"], to = loan_tranx["bank_from"], amount = loan_tranx["amount"], interest=environment.deposits_interest, maturity=0, time_of_default=-1)
        self.bank_accounts[loan_tranx["from_"]]["deposits"] -= loan_tranx["amount"]
        # Reduce reserves at CB
        reserves_tranx = {"type_": "reserves", "bank_from": self.identifier, "bank_to" : "central_bank", "amount" : loan_tranx["amount"], "time" : time}
        environment.get_agent_by_id("central_bank").rgts_payment(environment, reserves_tranx, time)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # issue_interbank_loan
    # bank issues loan to another bank
    # -------------------------------------------------------------------------
    def issue_interbank_loan(self, environment, loan_tranx, time):
        # Create loan agreement with bank
        type_ = "loans_interbank_" + loan_tranx["bank_from"]
        environment.new_transaction(type_= type_, asset='', from_= loan_tranx["bank_from"], to = self.identifier, amount = loan_tranx["amount"], interest=environment.loans_interbank_interest, maturity=0, time_of_default=-1)
        if loan_tranx["bank_from"] in self.bank_accounts:
            self.bank_accounts[loan_tranx["bank_from"]][type_] += loan_tranx["amount"]
        elif loan_tranx["bank_from"] not in loan_tranx:
            self.bank_accounts[loan_tranx["bank_from"]] = {type_: loan_tranx["amount"]}
        # Transfer reserves
        reserves_tranx = {"type_": "reserves", "amount" : loan_tranx["amount"], "bank_from":self.identifier, "bank_to":loan_tranx["bank_from"], "time" : time}
        environment.get_agent_by_id("central_bank").rgts_payment(environment, reserves_tranx, time)    
        #print(f"\n {loan_tranx['bank_from']} took out new loan of {loan_tranx['amount']} at {self.identifier}")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # settle_interbank_loan
    # bank settles loan with another bank
    # -------------------------------------------------------------------------
    def settle_interbank_loan(self, environment, time):
        # Repay loans agreement with bank
        # Loop through bank accounts
        for acc, values in dict(self.bank_accounts).items():
            if "bank" in acc: #If bank has account of other bank then it is owed an interbank loan from that bank
                type_ = list(self.bank_accounts[acc].keys())[0] # Create correct type
                amount = list(self.bank_accounts[acc].values())[0] # Record amount
                # Reserve loan transaction
                environment.new_transaction(type_= type_, asset='', from_= self.identifier, to = acc, amount = amount, interest=environment.loans_interbank_interest, maturity=0, time_of_default=-1)
                del self.bank_accounts[acc] # Remove loan account from bank balance sheet
                # Repay loan with RTGS
                reserves_tranx = {"type_": "reserves", "amount" : amount, "bank_from":acc, "bank_to":self.identifier, "time" : time}
                environment.get_agent_by_id("central_bank").rgts_payment(environment, reserves_tranx, time)    
                #print(f"\n {acc} repaid loan of {amount} to {self.identifier}")
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # make_payment
    # takes in transaction details from household or firms and makes payment
    # -------------------------------------------------------------------------
    def make_payment(self, environment, tranx, time):
		# We print the action of transferring deposits
        #print(f"\n{tranx['from_']}s paid {tranx['amount']} to {tranx['bank_from']} for {tranx['to']} at time {tranx['time']}.")
        # If payment is within bank, immediately debit and credit accounts
        if (tranx["bank_from"] == tranx["bank_to"]):
            # Transfer receipt from bank to household
            environment.new_transaction(type_="deposits", asset='', from_= tranx["from_"], to = tranx["to"], amount = tranx["amount"], interest=environment.deposits_interest, maturity=0, time_of_default=-1)
            self.bank_accounts[tranx["from_"]]["deposits"] -= tranx["amount"]
            self.bank_accounts[tranx["to"]]["deposits"] += tranx["amount"]
            #print(f"\n {self.identifier} paid {tranx['amount']} to {tranx['to']} \n")


        # It payment is between banks, send transaction to ACH or rapid payment
        elif (tranx["bank_from"] != tranx["bank_to"]):
            if environment.batch == 1:
                # If batching period is 1 then all payments occur via rapid payments through rtgs
                # Household or firm paying credits their deposit account and their bank debits their deposit account
                environment.new_transaction(type_="deposits", asset='', from_=tranx["from_"], to=tranx["bank_from"], amount=tranx["amount"], interest=environment.deposits_interest, maturity=0, time_of_default=-1)
                self.bank_accounts[tranx["from_"]]["deposits"] -= tranx["amount"]
                environment.get_agent_by_id("central_bank").rgts_payment(environment, tranx, time) # Reserves are paid via RTGS
                # Deposits are paid into receiving bank account
                environment.new_transaction(type_="deposits", asset='', from_= tranx["bank_to"], to = tranx["to"], amount = tranx["amount"], interest=environment.deposits_interest, maturity=0, time_of_default=-1)
                environment.get_agent_by_id(tranx["bank_to"]).bank_accounts[tranx["to"]]["deposits"] += tranx["amount"]
                #print(f"\n Rapid payment from {tranx['from_']} to {tranx['to']} of {tranx['amount']} at time {tranx['time']}")
                environment.number_of_cleared_payments += 1

            elif environment.batch > 1:
                # Household or firm paying credits their deposit account and their bank debits their deposit account
                environment.new_transaction(type_="deposits", asset='', from_=tranx["from_"], to=tranx["bank_from"], amount=tranx["amount"], interest=environment.deposits_interest, maturity=0, time_of_default=-1)
                self.bank_accounts[tranx["from_"]]["deposits"] -= tranx["amount"]
                # The transaction is sent to the ACH for batching
                environment.get_agent_by_id("ach").make_ach_payment(environment, tranx, time)
                #print(f"\n {self.identifier} paid {tranx['amount']} to {tranx['to']} \n")
        environment.total_payments += tranx["amount"]
        environment.total_deposit_payments += tranx["amount"]
        #logging.info("  payments made on step: %s",  time)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # settle_ach_payments
    # takes in transaction details from bank and makes payment to household
    # -------------------------------------------------------------------------
    def settle_ach_payments(self, environment, time):
        # Loop through bank accounts and determine which accounts have receivables
        for item in self.bank_accounts:
            if "bank" not in item: # Ensure that does not look for receivables account in interbank or CB loans
                receivables = self.bank_accounts[item]["receivables"]
                if receivables > 0:
                    environment.new_transaction(type_="deposits", asset='', from_= self.identifier, to = item, amount = receivables, interest=environment.deposits_interest, maturity=0, time_of_default=-1)
                    self.bank_accounts[item]["deposits"] += receivables
                    environment.new_transaction(type_="receivables", asset='', from_= item, to = self.identifier, amount = receivables, interest=0.00, maturity=0, time_of_default=-1)
                    self.bank_accounts[item]["receivables"] -= receivables
                    
            # Take in transaction details and transfer amount to deposits of household
                    #print(f"{self.identifier} settled payment of {receivables} to {item} at time {time}.")
        #print(self.balance_sheet())
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # check_required_reserves
    # bank determines whether reserve requirements are met and whether excess
    # or deficit of reserves
    # -------------------------------------------------------------------------
    def check_required_reserves(self):
        from numpy import floor
        # Determine reserves required
        required_reserves = self.get_account("deposits") * 0.025 # reserves requirements rule
        reserves_residual = self.get_account("reserves") - required_reserves
        return reserves_residual
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_notes_purchase
    # Household exchanges deposits at bank for cbdc at central bank
    # -------------------------------------------------------------------------
    def bank_notes_to_deposits(self, environment, tranx, time):
            # Create deposits for household
            environment.new_transaction(type_="deposits", asset='', from_=tranx["bank_from"], to=tranx["from_"], amount=tranx["amount"], interest=environment.deposits_interest, maturity=0, time_of_default=-1)
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
        assets["interbank_loans"] = 0
        liabilities = {}

        for item in self.assets:
            if "loans_interbank" in item:
                assets["interbank_loans"] += self.get_account(item)
            else:    
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
    # get_equity
    # calculates equity
    # -------------------------------------------------------------------------
    def get_equity(self):
        assets = {}
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
