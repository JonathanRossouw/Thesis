import sys
import logging
import os
import networkx as nx
import matplotlib.pyplot as plt

from src.environment import Environment
from src.runner import Runner

#!/usr/bin/env python
# [SublimeLinter pep8-max-line-length:300]
# -*- coding: utf-8 -*-

"""
This is a minimal example.

black_rhino is a multi-agent simulator for financial network analysis
Copyright (C) 2012 Co-Pierre Georg (co-pierre.georg@keble.ox.ac.uk)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>

The development of this software has been supported by the ERA-Net
on Complexity through the grant RESINEE.
"""

args = ['./sim_script.py',  "environments/", "CBDC_parameters",  "log/"]
# args = sys.argv

if len(args) != 4:
    print("Usage: ./sim_script environment_directory/ environment_identifier log_directory/")
    sys.exit()

#
# INITIALIZATION
#


environment_directory = str(args[1])
identifier = str(args[2])
log_directory = str(args[3])

# Create Logger

if not os.path.exists('log'):
    os.makedirs('log')
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S',
                    filename=log_directory + identifier + ".log", level=logging.INFO)
logging.info('START logging for run: %s',  environment_directory + identifier + ".xml")

# Create Environment
environment = Environment(environment_directory,  identifier)
# importing the module
import json
  
# Opening JSON file
with open('gdp.json') as json_file:
    data = json.load(json_file)
environment.gdp_calibrate = data

# Create Runner
runner = Runner(environment)


#
# UPDATE STEP
#
for i in range(int(environment.num_simulations)):
    logging.info('  STARTED with run %s',  str(i))
    environment.initialize(environment_directory,  identifier)
    runner.initialize(environment)
    # do the run
    runner.do_run(environment)
    logging.info('  DONE')


# Check if balance sheets are consistent

house = True
for houses in environment.households:
    house *= houses.check_consistency()
if house:
    print("All households have consistent balance sheets")
else:
    print("Not all households have consistent balance sheets")

firm = True
for firms in environment.firms:
    firm *= firms.check_consistency()
if firm:
    print("All firms have consistent balance sheets")
else:
    print("Not all firms have consistent balance sheets")

bank = True
for banks in environment.banks:
    bank *= banks.check_consistency()
if bank:
    print("All banks have consistent balance sheets")
else:
    print("Not all banks have consistent balance sheets")

if environment.central_bank[0].check_consistency():
    print("Central Bank has consistent balance sheets")
elif environment.central_bank[0].check_consistency() is False:
    print("Central Bank does not consistent balance sheets")



# Save plot social network
nx.draw_shell(environment.social_network)
plt.savefig('figures/social_network.png')

# Save plot employment network
nx.draw_shell(environment.employment_network)
plt.savefig('figures/employment_network.png')

# Save plot consumption network
nx.draw_shell(environment.consumption_network)
plt.savefig('figures/consumption_network.png')

# Save plot bank network
nx.draw_shell(environment.bank_network)
plt.savefig('figures/bank_network.png')
