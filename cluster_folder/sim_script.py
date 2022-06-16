import sys
import logging
import os
import networkx as nx
import matplotlib.pyplot as plt

from src.environment import Environment
from src.runner import Runner
from src.br_generate_agents import Generate_Agents

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

# Read in directory for agents
remove = True

bank_dir = os.getcwd()+'/agents/gen_banks/'
house_dir = os.getcwd()+'/agents/gen_households/'
firm_dir = os.getcwd()+'/agents/gen_firms/'

bank_list = [ f for f in os.listdir(bank_dir) if f.startswith("bank") ]
house_list = [ f for f in os.listdir(house_dir) if f.startswith("house") ]
firm_list = [ f for f in os.listdir(firm_dir) if f.startswith("firm") ]

# Remove existing agents
for f in bank_list:
    os.remove(os.path.join(bank_dir, f))
for f in house_list:
    os.remove(os.path.join(house_dir, f))
for f in firm_list:
    os.remove(os.path.join(firm_dir, f))


# Create random agents

gen_agents = Generate_Agents()

gen_agents.generate_households(environment.static_parameters['num_households'], "./agents/gen_households/")

gen_agents.generate_firms(environment.static_parameters['num_firms'], "./agents/gen_firms/")

gen_agents.generate_banks(environment.static_parameters['num_banks'], "./agents/gen_banks/")

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

npv = 0.0
wealth = 0.0
for houses in environment.households:
    npv += houses.check_npv()[houses.identifier]["npv"]
    wealth += houses.wealth

print(f"Household NPV is {round(npv, 2)} and wealth is {wealth}")

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

if environment.ach[0].check_consistency():
    print("ACH has consistent balance sheets")
elif environment.ach[0].check_consistency() is False:
    print("ACH does not consistent balance sheets")

print(f"Central Bank reserves are {environment.central_bank[0].get_account('reserves')}")

# Plot consumption network
C = environment.consumption_network
color_map_C = ['red' if "firm" in node else 'green' for node in C]        
nx.draw(C, node_color=color_map_C)
plt.title("Consumption Network", size=20)
plt.savefig('figures/consumption_network.png')

# Plot bank network
B = environment.bank_network
color_map_B = ['red' if "bank" in node else 'yellow' if "firm" in node else 'green' for node in B]        
nx.draw(B, node_color=color_map_B)
plt.title("Bank Network", size=20)
plt.savefig('figures/bank_network.png')

# Plot interbank network
I = environment.interbank_network    
nx.draw(I, node_color="g")
plt.title("Interbank Network", size=20)
plt.savefig('figures/interbank_network.png')

