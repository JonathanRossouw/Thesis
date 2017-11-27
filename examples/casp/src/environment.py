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

import os
import logging

from xml.etree import ElementTree
from abm_template.src.baseconfig import BaseConfig

# -------------------------------------------------------------------------
#
#  class Environment
#
# -------------------------------------------------------------------------


class Environment(BaseConfig):
    from state import State
    from parameters import Parameters
    #
    #
    # VARIABLES
    #
    #
    identifier = ""  # identifier of the environment
    static_parameters = {}  # a dictionary containing all environmenet parameters

    static_parameters["num_simulations"] = 0  # number of simulations
    static_parameters["num_sweeps"] = 0  # numbers of runs in a single simulation
    static_parameters["num_agents"] = 0  # number of agents in a simulation
    static_parameters["fund_directory"] = ""  # directory containing agent xmls

    agents = []
    funds = []
    variable_parameters = {}
    parameters = Parameters()
    state = State()
    #
    # CODE
    #

    def __getattr__(self, attr):
        return super(Environment, self).__getattr__(attr)

    def get_identifier(self):
        return self.identifier

    def set_identifier(self, value):
        super(Environment, self).set_identifier(value)

    def __str__(self):
        return super(Environment, self).__str__()

    def accrue_interests(self):
        super(Environment, self).accrue_interests()

    def add_shock(self, shock):
        super(Environment, self).add_shock()

    def add_static_parameter(self, params):
        super(Environment, self).add_static_parameters(params)

    def get_static_parameters(self):
        return self.static_parameters

    def set_static_parameters(self, params):
        super(Environment, self).set_static_parameters(params)

    def add_variable_parameter(self, params):
        super(Environment, self).add_static_parameters(params)

    def get_variable_parameters(self):
        return self.variable_parameters

    def set_variable_parameters(self, params):
        super(Environment, self).set_variable_parameters(params)

    def get_assets(self):
        return self.assets

    def set_assets(self, params):
        super(Environment, self).set_assets(params)

    def get_shocks(self):
        return self.shocks

    def set_shocks(self, params):
        super(Environment, self).set_shocks(params)

    def agents_generator(self):
        super(Environment, self).agents_generator()

    def get_agent_by_id(self, ident):
        super(Environment, self).get_agent_by_id(ident)

    def check_global_transaction_balance(self, _type):
        super(Environment, self).check_global_transaction_balance(_type)

    def write_environment_file(self, file_name):
        super(Environment, self).write_environment_file()

    def print_parameters(self):
        super(Environment, self).print_parameters()

    def update_asset_returns(self):
        super(Environment, self).update_asset_returns()

    def __init__(self, environment_directory, identifier):

        self.initialize(environment_directory, identifier)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # read_xml_config_file(self, config_file_name)
    # reads an xml file with config and sets identifier and parameters
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def read_xml_config_file(self, env_filename):

        try:
            xmlText = open(env_filename).read()
            element = ElementTree.XML(xmlText)  # we tell python it's an xml
            self.identifier = element.attrib['identifier']

            # loop over all entries in the xml file
            for subelement in element:

                try:  # we see whether the value is a int
                    if subelement.attrib['type'] == 'variable_parameters':
                        value = float(subelement.attrib['value'])
                        name = subelement.attrib['name']
                        self.variable_parameters[name] = value

                    else:
                        value = int(subelement.attrib['value'])
                        type_ = subelement.attrib['type']
                        self.static_parameters[type_] = value

                except:  # if not, it is a string
                    value = str(subelement.attrib['value'])
                    type_ = subelement.attrib['type']
                    self.static_parameters[type_] = value

        except:
            logging.error("    ERROR: %s could not be parsed", env_filename)
    # -------------------------------------------------------------------------
    # the next function
    # initializes the environment, initializing all the variables
    # reading the env_config file from supplied environment_directory and
    # identifier, and initializes all agents from the directories
    # supplied in the main config file
    # -------------------------------------------------------------------------

    def initialize(self, environment_directory, identifier):
        self.identifier = identifier

        self.static_parameters = {}
        self.static_parameters["num_simulations"] = 0
        self.static_parameters["num_sweeps"] = 0
        self.static_parameters["num_agents"] = 0
        self.static_parameters["fund_directory"] = ""
        self.variable_parameters["sum_ame_funds"] = 0
        self.variable_parameters["sum_eme_funds"] = 0

        # first, read in the environment file
        environment_filename = environment_directory + identifier + ".xml"
        self.read_xml_config_file(environment_filename)
        logging.info(" environment file read: %s", environment_filename)
        # then read in all the agents
        self.initialize_funds_from_files(self.static_parameters['fund_directory'], 0)
        self.agents = [self.funds]

        self.count_ame_funds()
        self.count_eme_funds()

    # -------------------------------------------------------------------------
    def initialize_funds_from_files(self, fund_directory, time):

        from src.fund import Fund
        while len(self.funds) > 0:
            self.funds.pop()

        agent_files = os.listdir(fund_directory)

        for each_agent_file in agent_files:

            if '.xml' in each_agent_file:
                agent = Fund()
                agent_filename = fund_directory + each_agent_file
                agent.get_parameters_from_file(agent_filename, self)
                self.funds.append(agent)
        # check if agents were read in correctly
        # for i in self.funds:
        #     print i.identifier
        #     print i.print_variables()
        #     print i

    def initialize_ame_returns(self):
        import numpy as np
        import random

        random.seed(900)
        mu_ame, sigma_ame = self.mu_ame, 0.01 # mean and standard deviation
        s = np.random.normal(mu_ame, sigma_ame, (self.variable_parameters['sum_ame_funds']+self.variable_parameters['sum_eme_funds']))
        return s

    def initialize_eme_returns(self):
        import numpy as np
        import random

        random.seed(900)
        mu_eme, sigma_eme = self.mu_eme, 0.01 # mean and standard deviation
        e = np.random.normal(mu_eme, sigma_eme, (self.variable_parameters['sum_ame_funds']+self.variable_parameters['sum_eme_funds']))
        return e

    def count_ame_funds(self):
        sum_ame = 0

        for fund in self.funds:
            if fund.parameters['domicile'] == 0:
                sum_ame += 1
        self.variable_parameters['sum_ame_funds'] = sum_ame


    def count_eme_funds(self):
        sum_eme = 0
        for fund in self.funds:
            if fund.parameters['domicile'] == 0:
                sum_eme += 1
        self.variable_parameters['sum_eme_funds'] = sum_eme