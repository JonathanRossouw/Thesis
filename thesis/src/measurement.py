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
from posix import environ
from abm_template.src.basemeasurement import BaseMeasurement

# ============================================================================
#
# class Measurement
#
# ============================================================================


class Measurement(BaseMeasurement):
    #
    # VARIABLES
    #

    # identifier for usual purposes
    identifier = ""
    # Now we set up a config for the measurements
    # see notes on the xml config file in the method below
    config = {}
    # environment for access
    environment = type('', (), {})()
    # filename for the output csv
    # runner for access
    runner = type('', (), {})()
    filename = ""
    # and the file we're writing to
    file = None
    # plus the csv writer
    csv_writer = None

    #
    # METHODS
    #

    def get_identifier(self):
        return self.identifier

    def set_identifier(self, identifier):
        super(Measurement, self).set_identifier(identifier)

    def get_config(self):
        return self.config

    def set_config(self, config):
        super(Measurement, self).set_config(config)

    def get_environment(self):
        return self.environment

    def set_environment(self, environment):
        super(Measurement, self).set_environment(environment)

    def get_runner(self):
        return self.runner

    def set_runner(self, runner):
        super(Measurement, self).set_runner(runner)

    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        super(Measurement, self).set_filename(filename)

    def get_file(self):
        return self.file

    def set_file(self, file):
        super(Measurement, self).set_file(file)

    def get_csv_writer(self):
        return self.csv_writer

    def set_csv_writer(self, csv_writer):
        super(Measurement, self).set_csv_writer(csv_writer)

    # -------------------------------------------------------------------------
    # __init__(self, environment, runner) 
    # Initialises the Measurements object and reads the config
    # -------------------------------------------------------------------------
    def __init__(self, environment, runner):
        super(Measurement, self).__init__(environment, runner)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # open_file(self)
    # Opens the file and writes the headers
    # -------------------------------------------------------------------------
    def open_file(self):
        super(Measurement, self).open_file()
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # write_to_file(self)
    # Writes a row of values for to store the state of the system
    # at the time of calling this method
    # -------------------------------------------------------------------------
    def write_to_file(self):
        super(Measurement, self).write_to_file()
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # close_file(self, filename)
    # Closes the file so we don't have issues with the disk and the file
    # -------------------------------------------------------------------------
    def close_file(self):
        super(Measurement, self).close_file()
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # read_xml_config_file(self, config_file_name)
    # Read the xml config file specifying the config file
    # which is a list of lists
    # We need to specify the filename
    # We also need to specify each output:
    # - type: 'output'
    # - column: integer specifying which column will be used for this
    # - header: string written as header in the csv file in the column
    # - value: string or number, identifier for the wrapper function
    # specifying what the wrapper function returns
    # Thus:
    # {column_number: [header, output, wrapper_id],...:[...]]
    # [int: [string, string, string],...:[...]]
    #
    # Now we pass this on to the Measurement class through an xml file
    # which should look like this
    #
    # <measurement identifier='test_output'>
    #     <parameter type='filename' value='TestMeasurement.csv'></parameter>
    #     <parameter type='output' column='1' header='Step' value='current_step'></parameter>
    #     <parameter type='output' column='2' header='Deposits' value='household_deposits' ></parameter>
    # </measurement>
    #
    # -------------------------------------------------------------------------
    def read_xml_config_file(self, config_file_name):
        super(Measurement, self).read_xml_config_file(config_file_name)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # wrapper(self, id)
    # Wrapper for functions returning the desired values to be written
    # -------------------------------------------------------------------------
    def wrapper(self, ident):
        if ident == "current_step":
            return self.runner.current_step+1

        else:
            method = getattr(self.environment, ident)
            return method

        
        deposits_balance = 0
        cbdc_balance = 0
        for tranx in self.environment.central_bank[0].accounts:
            if tranx.type_ == "cbdc":
                cbdc_balance += tranx.amount

        
            
        if ident == "total_output":
            return self.environment.total_output

        if ident == "total_deposit_payments":
            return self.environment.total_deposit_payments

        if ident == "deposit_payments":
            if len(self.environment.deposits_period) == 1:
                return self.environment.deposits_period[0]
            # elif len(self.environment.deposits_period) == 2:
            #     return self.environment.deposits_period[1]
            else:
                return self.environment.deposits_period[-1] - self.environment.deposits_period[-2]

        banks = []
        for bank in self.environment.banks:
            banks.append(bank.identifier)

        if ident in banks:
            deposits = 0
            bank_acc = self.environment.get_agent_by_id(ident).bank_accounts
            for acc in bank_acc:
                if "bank" not in acc:
                    deposits += bank_acc[acc]["deposits"]
            return deposits


        if ident == "total_deposits":
            total_deposits = 0
            for bank in self.environment.banks:
                total_deposits += bank.get_account("deposits")
            return total_deposits

        if ident == "receivables":
            total_receivables = 0
            for bank in self.environment.banks:
                total_receivables += bank.get_account("receivables")
            return total_receivables

        if ident == "loans":
            total_loans = 0
            for bank in self.environment.banks:
                total_loans += bank.get_account("loans")
            return total_loans

        if ident == "cbdc_payments":
            return cbdc_balance

        banks_reserves = {}
        for bank in self.environment.banks:
            banks_reserves[bank.identifier + "_reserves"] = bank.get_account("reserves")

        if ident in banks_reserves:
            return banks_reserves[ident]

        banks_interbank_loans = {}
        for bank in self.environment.banks:
            banks_interbank_loans[bank.identifier + "_interbank_loans"] = bank.balance_sheet()[bank.identifier]["assets"]["interbank_loans"]

        if ident in banks_interbank_loans:
            return banks_interbank_loans[ident]

        if ident == "open_market_operations":
            return self.environment.central_bank[0].get_account("open_market_operations")

        if ident == "interbank_loans":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["assets"]["interbank_loans"]

        if ident == "loans":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["assets"]["loans"]

        if ident == "reserves":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["assets"]["reserves"]

        if ident == "bank_notes":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["assets"]["bank_notes"]

        if ident == "open_market_operations_0":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["assets"]["open_market_operations"]

        if ident == "ach_payee_bank_0":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["assets"]["ach_payee_bank_0"]

        if ident == "deposits":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["liabilities"]["deposits"]

        if ident == "receivables_0":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["liabilities"]["receivables"]

        if ident == "loans_central_bank_0":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["liabilities"]["loans_central_bank"]

        if ident == "ach_payer_bank_0":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["liabilities"]["ach_payer_bank_0"]

        if ident == "loans_interbank_bank_0":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["liabilities"]["loans_interbank_bank_0"]

        if ident == "equity_0":
            bank = self.environment.banks[0]
            return bank.balance_sheet()[bank.identifier]["liabilities"]["equity"]    
    # -------------------------------------------------------------------------
