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
# class ACH
#
# ============================================================================


class ACH(BaseAgent):
    #
    #
    # VARIABLES
    #
    #

    identifier = ""  # identifier of the ACH
    parameters = {}  # parameters of the ACH
    state_variables = {}  # state variables of the ACH
    accounts = []  # all accounts of the ACH (filled with transactions)
    assets = []
    liabilities = []

    batches = {}  # Store transactions for batching
    collateral = {} # Record bank collateral
    banks = []

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
        super(ACH, self).set_identifier(value)

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, value):
        super(ACH, self).set_parameters(value)

    def get_state_variables(self):
        return self.state_variables

    def set_state_variables(self, value):
        super(ACH, self).set_state_variables(value)

    def append_parameters(self, value):
        super(ACH, self).append_parameters(value)

    def append_state_variables(self, value):
        super(ACH, self).append_state_variables(value)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # functions needed to make ACH() hashable
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
        self.identifier = ""  # identifier of the ACH
        self.parameters = {}  # parameters of the ACH
        self.state_variables = {}  # state variables of the ACH
        self.accounts = []  # all accounts of the bank (filled with transactions)
        # DO NOT EVER ASSIGN PARAMETERS BY HAND AS DONE BELOW IN PRODUCTION CODE
        # ALWAYS READ THE PARAMETERS FROM CONFIG FILES
        # OR USE THE FUNCTIONS FOR SETTING / CHANGING VARIABLES
        # CONVERSELY, IF YOU WANT TO READ THE VALUE, DON'T USE THE FULL NAMES
        # INSTEAD USE __getattr__ POWER TO CHANGE THE COMMAND FROM
        # instance.static_parameters["xyz"] TO instance.xyz - THE LATTER IS PREFERRED
        self.assets = ["ach_payer", "reserves"]
        self.liabilities = ["ach_payee", "clearing_house_fee"]
        self.batches = {}
        self.collateral = {}
        self.banks = []

        
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __del__
    # -------------------------------------------------------------------------
    def __del__(self):
        pass
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __str__
    # returns a string describing the ACH and its properties
    # based on the implementation in the abstract class BaseAgent
    # but adds the type of agent (bank) and lists all transactions
    # -------------------------------------------------------------------------
    def __str__(self):
        bank_string = super(ACH, self).__str__()
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
        super(ACH, self).get_parameters_from_file(bank_filename, environment)
    # ------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # make_ach_payment
    # takes in transaction details from household or firms and makes payment
    # -------------------------------------------------------------------------
    def make_ach_payment(self, environment, tranx, time):
        # Payers bank debits on ACH account
        tranx_payer = "ach_payer_" + tranx["bank_from"]
        environment.new_transaction(type_=tranx_payer, asset='', from_= tranx["bank_from"], to = "ach", amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)

        # Payees bank credits on ACH account

        tranx_payee = "ach_payee_" + tranx["bank_to"]
        environment.new_transaction(type_=tranx_payee, asset='', from_= "ach", to = tranx["bank_to"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)

        # Payees bank debits ACH account and credits payees receivables account

        environment.new_transaction(type_="receivables", asset='', from_= tranx["bank_to"], to = tranx["to"], amount = tranx["amount"], interest=0.00, maturity=0, time_of_default=-1)
        environment.get_agent_by_id(tranx["bank_to"]).bank_accounts[tranx["to"]]["receivables"] += tranx["amount"]
        #print(f"{tranx['amount']} paid from {tranx['from_']} to {tranx['to']} via ach and {tranx['bank_from']} and {tranx['bank_to']}")
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # batch_settle
    # determine which banks have positive and negative batch accounts
    # -------------------------------------------------------------------------
    def batch_settle(self, environment, time):
        # Determine net payers and net payees
        payer = {}
        payee = {}
        for bank in self.banks:
            #print(environment.get_agent_by_id(bank).balance_sheet())
            balance = self.get_account("ach_payer_" + bank) - self.get_account("ach_payee_" + bank)
            if balance > 0:
                payer[bank] = balance
            elif balance < 0:
                payee[bank] = abs(balance)
        
        # Loop through ACH_payer accounts, call rtgs payment from bank to ACH
        for item in payer:
            # Reverse ach transactions at banks
            bank_payee = self.get_account("ach_payee_" + item)
            bank_payer = self.get_account("ach_payer_" + item)
            environment.new_transaction(type_="ach_payee_"+item, asset='', from_=item, to="ach", amount=bank_payee, interest=0.00, maturity=0, time_of_default=-1)
            environment.new_transaction(type_="ach_payer_"+item, asset='', from_="ach", to=item, amount=bank_payer, interest=0.00, maturity=0, time_of_default=-1)
            # Bank pays clearing house fee
            ACH_fee_amount = environment.clearing_house_fee * payer[item]
            ACH_fee_tranx = {"type_": "clearing_house_fee", "amount" : ACH_fee_amount, "bank_from":'ach', "bank_to":item, "time" : time}
            environment.new_transaction(type_=ACH_fee_tranx['type_'], asset='', from_=ACH_fee_tranx['bank_from'], to=ACH_fee_tranx['bank_to'], amount=ACH_fee_tranx['amount'], interest=0.00, maturity=0, time_of_default=-1)
            # Transfer balance of reserves from bank to ach
            reserve_amount = payer[item] + ACH_fee_amount
            payer_tranx = {"type_": "reserves", "amount" : reserve_amount, "bank_from":item, "bank_to":"ach", "time" : time}
            environment.get_agent_by_id("central_bank").rgts_payment(environment, payer_tranx, time)        
        # Loop through ACH_payee accounts, call rtgs payment from ACH to bank
        for item in payee:
            # Reverse ach transactions at banks
            bank_payee = self.get_account("ach_payee_" + item)
            bank_payer = self.get_account("ach_payer_" + item)
            environment.new_transaction(type_="ach_payee_"+item, asset='', from_=item, to="ach", amount=bank_payee, interest=0.00, maturity=0, time_of_default=-1)
            environment.new_transaction(type_="ach_payer_"+item, asset='', from_="ach", to=item, amount=bank_payer, interest=0.00, maturity=0, time_of_default=-1)
            # Transfer balance of reserves from ach to bank
            payee_tranx = {"type_": "reserves", "amount" : payee[item], "bank_from":"ach", "bank_to":item, "time" : time}
            environment.get_agent_by_id("central_bank").rgts_payment(environment, payee_tranx, time)
    # -------------------------------------------------------------------------


    # # -------------------------------------------------------------------------
    # # batch_settle
    # # determine which banks have positive and negative batch accounts
    # # -------------------------------------------------------------------------
    # def batch_settle(self, environment, time):
    #     # Import market
    #     from src.market import Market
    #     # Aggregate payments and determine balances
    #     for banks in self.batches:
    #         self.batches[banks] = sum(self.batches[banks])
    #     # Create list of balances for rationing
    #     batches_ration = []
    #     for key, value in self.batches.items():
    #         batches_ration.append([key, value])
    #     # Perform rationing
    #     mark = Market(environment)
    #     ach_settle = mark.rationing(batches_ration)
    #     # Loop through rationing tranactions and call interbank settlement mtheod to net reserve payments
    #     for tranx in ach_settle:
    #         # Transfer Reserves between banks
    #         rgts_tranx = {"bank_from":tranx[0], "bank_to":tranx[1], "amount":tranx[2]}
    #         environment.get_agent_by_id("central_bank").rgts_payment(environment, rgts_tranx, time)
    #         print(f"\n {tranx[0]} settled {tranx[1]} worth of reserves to {tranx[2]} \n")
    #     for bank in environment.banks:
    #     # Transfer ACH deposits
    #         ach_deposits = bank.get_account("ach_deposits")
    #         bank_id = bank.identifier
    #         environment.new_transaction(type_="ach_deposits", asset='', from_="ach", to=bank_id, amount=ach_deposits, interest=0.00, maturity=0, time_of_default=-1)
    #         print(f"\n ACH settled {-ach_deposits} worth of ACH deposits to {bank_id} \n")
    #     # Return bank collateral
    #     for bank in self.collateral:
    #         collateral_amount = self.collateral[bank]
    #         environment.new_transaction(type_="loans", asset='', from_=self.identifier, to=bank, amount=collateral_amount, interest=0.00, maturity=0, time_of_default=-1)
    #         self.collateral[bank] = 0
    #     # Reset batches
    #     for bank in self.batches:
    #         # Transfer collateral 
    #         self.batches[bank] = []
    # # -------------------------------------------------------------------------



    # -------------------------------------------------------------------------
    # balance_sheet
    # returns balance sheet of agent
    # -------------------------------------------------------------------------
    def balance_sheet(self):
        balance_sheet = {}
        assets = {}
        liabilities = {}
        for item in self.assets:
            assets[item] = 0
            if "ach" in item:
                for bank in self.banks:
                    account = "ach_payer_" + bank
                    assets[item] += self.get_account(account)
            else:
                assets[item] += self.get_account(item)

        for item in self.liabilities:
            liabilities[item] = 0
            if "ach" in item:
                for bank in self.banks:
                    account = "ach_payee_" + bank
                    liabilities[item] += self.get_account(account)
            else:
                liabilities[item] += self.get_account(item)

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

        assets = []
        for item in self.assets:
            if "ach" in item:
                for bank in self.banks:
                    account_payer = item + "_" + bank
                    assets.append(account_payer)
            else:
                assets.append(item)

        liabilities = []
        for item in self.liabilities:
            if "ach" in item:
                for bank in self.banks:
                    account_payee = item + "_" + bank
                    liabilities.append(account_payee)
            else:
                liabilities.append(item)

        for transaction in self.accounts:
            if transaction.type_ in assets:
                if (transaction.type_ == type_) & (transaction.from_.identifier == self.identifier):
                    volume = volume - float(transaction.amount)
                elif (transaction.type_ == type_) & (transaction.from_.identifier!= self.identifier):
                    volume = volume + float(transaction.amount)
            elif transaction.type_ in liabilities:
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
        return super(ACH, self).get_account_num_transactions(type_)
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
    # removes all transactions from ACH's accounts
    # only for testing, the one in transaction should be used in production
    # -------------------------------------------------------------------------
    def clear_accounts(self, environment):
        super(ACH, self).clear_accounts(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # purge_accounts
    # removes worthless transactions from ACH's accounts
    # -------------------------------------------------------------------------
    def purge_accounts(self, environment):
        super(ACH, self).purge_accounts(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # get_transactions_from_file
    # reads transactions from the config file to the ACH's accounts
    # -------------------------------------------------------------------------
    def get_transactions_from_file(self, filename, environment):
        super(ACH, self).get_transactions_from_file(filename, environment)
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
        return super(ACH, self).__getattr__(attr)
    # -------------------------------------------------------------------------
