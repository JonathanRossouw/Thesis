from os import environ
from src.market import Market
from src.central_bank import CentralBank

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

from abm_template.src.basemodel import BaseModel
import random
import logging
import datetime
import numpy as np
from src.transaction import Transaction
from src.market import Market
# -------------------------------------------------------------------------
#  class Updater
# -------------------------------------------------------------------------


class Updater(BaseModel):
    #
    #
    # VARIABLES
    #
    #

    identifier = ""
    model_parameters = {}
    interactions = None

    #
    #
    # METHODS
    #
    #

    def get_identifier(self):
        return self.identifier

    def get_store(self):
        return self.store

    def set_identifier(self, _value):
        super(Updater, self).set_identifier(_value)

    def get_model_parameters(self):
        return self.model_parameters

    def set_model_parameters(self, _value):
        super(Updater, self).set_model_parameters(_value)

    def get_interactions(self):
        return self.interactions

    def set_interactions(self, _value):
        super(Updater, self).set_interactions(_value)

    def __str__(self):
        return super(Updater, self).__str__()

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self,  environment):
        self.environment = environment
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # do_update
    # -------------------------------------------------------------------------
    def do_update(self,  environment,  time):
        # If time is 0, endow agents with endowments
        self.endow_agents(environment, time)
        # Accrue Interests
        self.accrue_interests(environment, time)
        # Every batch*2 + 1 periods settle central bank then interbank loans
        self.settle_central_bank_loans(environment, time)
        self.settle_interbank_loans(environment, time)
        self.settle_household_loans(environment, time)
        # For time > 0, initiate production
        self.initiate_production(environment, time)
        # Firms pay wages and households purchase and consume output
        self.output_consumption(environment, time)
        # Households demand and purchase services
        #self.payment_shock(environment, time)
        # Firms repay loans at end of month
        #self.repay_loans(environment, time)
        # Batching at ACH settles
        self.net_settle(environment, time)
        # CBDC transactions settle
        #self.write_cbdc_transactions(environment, time)
        # Loop through banks to determine which have excess reserves and deficit reserves
        self.check_reserve_requirements(environment, time)
        # Purging accounts at every step just in case
        self.update_equity(environment, time)
        self.write_agent_balance_sheets(environment, time)
        logging.info("  Period %s complete",  time)
        print(f"Period {time} complete")
        transaction = Transaction()
        transaction.purge_accounts(environment)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # endow_agents
    # Calls methods for households, firms and banks to allocate endowment
    # -------------------------------------------------------------------------
    def endow_agents(self, environment, time):
        # For eacn of households, firms and banks
        if time == 0:
            self.bank_initialize(environment, time)
            self.hh_allocate_assets(environment, time)
            self.firm_endow_assets(environment, time)
            self.bank_initialize_reserves(environment, time)
            self.ach_initialize(environment, time)
            self.firm_capital_initialize(environment, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # hh_allocate_assets
    # Households reallocate deposits to CBDC, bank notes and remaining deposits
    # -------------------------------------------------------------------------
    def hh_allocate_assets(self,  environment, time):
        # Call allocation method in Households class
        if time == 0:
            for household in environment.households:
                household.hh_asset_endowment(environment, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # firm_endow_assets
    # This function makes sure that all firms deposit bank notes received from 
    # households for firm capital at bank to create deposit accounts
    # -------------------------------------------------------------------------
    def firm_endow_assets(self,  environment, time):
        # Call endowment method in Firms class
        if time == 0:
            for firm in environment.firms:
                firm.firm_deposit_bank_notes(environment, time)
            logging.info("  deposit endowed on step: %s",  time)
        # Keep on the log with the number of step, for debugging mostly
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_initialize
    # banks create accounts for households and firms that are in their banking 
    # neighbourhood
    # -------------------------------------------------------------------------
    def bank_initialize(self,  environment, time):
        # Call endowment method in Households and Banks class
        if time == 0:
            for bank in environment.banks:
                bank.bank_initialize(environment)
            #logging.info("  deposit endowed on step: %s",  time)
        # Keep on the log with the number of step, for debugging mostly 
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_initialize_reserves
    # This function makes sure that all firms have the appropriate
    # deposit endowment for every step, in line with the parameters
    # -------------------------------------------------------------------------
    def bank_initialize_reserves(self,  environment, time):
        # Call allocation method in Firms class
        if time == 0:
            for bank in environment.banks:
                bank.initialize_reserves(environment, time)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # bank_initialize_reserves
    # This function makes sure that all firms have the appropriate
    # deposit endowment for every step, in line with the parameters
    # -------------------------------------------------------------------------
    def update_equity(self,  environment, time):
        # Call allocation method in Firms class
        if time > 0:# and time%(environment.batch*2) == 0:
            E = environment.employment_network
            for firm in environment.firms:
                for hh in E.adj[firm.identifier]:
                    equity_prop = firm.equity_households[hh]
                    environment.get_agent_by_id(hh).equity_firm = round(firm.get_equity() * equity_prop, 3)

            G = environment.bank_network
            for bank in environment.banks:
                for agent in G.adj[bank.identifier]:
                    if "household" in agent:
                        equity_prop = bank.equity_households[agent]
                        environment.get_agent_by_id(agent).equity_bank = round(bank.get_equity() * equity_prop, 3)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # ach_initialize
    # This function makes sure that all households have the appropriate
    # deposit endowment for every step, in line with the parameters
    # -------------------------------------------------------------------------
    def ach_initialize(self,  environment, time):
        # Call endowment method in Households and Banks class
        if time == 0:
            # Loop through banks to create batches
            for bank in environment.banks:
                environment.get_agent_by_id("ach").banks[bank.identifier] = 0
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # firm_capital_initialize
    # This function makes all firms take out loans for capital expenditure
    # from the bank they are connected to
    # -------------------------------------------------------------------------
    def firm_capital_initialize(self,  environment, time):
        if time == 0:
            # Loop through firms to take out loans
            for firm in environment.firms:
                firm.loan_capital(environment, time)
    # -------------------------------------------------------------------------
    

    # -------------------------------------------------------------------------
    # accrue_interests(environment, time)
    # This method accrues interest on all transaction
    # making sure we don't double count the transactions that are
    # on the books of multiple agents, interest is specified within the
    # transaction itself
    # -------------------------------------------------------------------------
    def accrue_interests(self,  environment, time):
        if time == 0:
            if isinstance(environment.interest_rate_list, str):
                environment.interest_rate_list = environment.interest_rate_list.split(',')
                if 'interbank_loans' in environment.interest_rate_list:
                    environment.interest_rate_list.remove('interbank_loans')
                    for bank in environment.banks:
                        environment.interest_rate_list.append("interbank_loans_" + bank.identifier)
        if time > 0:# and time%(environment.batch) == 0:
            environment.accrue_interests()
            logging.info("  Interest Accrued: %s",  time)
        #logging.info("  interest accrued on step: %s",  time)
        # Keep on the log with the number of step, for debugging mostly
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # production(environment, time)
    # This function calls for production to be initiated for the step. Households
    # provide labour to firms, which firms pay for. Firms use labour to produce
    # output. The households purchase output and the labour/output obligation is
    # cancelled out.
    # -------------------------------------------------------------------------
    def initiate_production(self, environment, time):
        # Set Date Time from time
        # year,julian = [2021,time]
        # date_time = datetime.datetime(year, 1, 1)+datetime.timedelta(days=julian -1)
        # # Year Month Day
        # year = int(date_time.strftime("%y"))
        # month = int(date_time.strftime("%m"))
        # day = date_time.strftime("%d")
        # # Find last day of month
        # end_day = (datetime.date(year + int(month/12), month%12+1, 1) -datetime.timedelta(days=1)).strftime("%d")
        # # Production on the first of the month
        if time > 0:
            E = environment.employment_network
            # Loop through firms in the network and initiate production
            for u in E.nodes(data=False):
                agent = environment.get_agent_by_id(u)
                if agent in environment.firms:
                    agent.production_function(environment, time)
                    #print(f"\n PRODUCTION {agent.identifier}!!! \n")

            # Wages on the 25th of the month
            # if (int(day) % 25) == 0:
            if time % 25 == 0:
                E = environment.employment_network
                # Loop through firms in the network and pay wages
                for u in E.nodes(data=False):
                    agent = environment.get_agent_by_id(u)
                    if agent in environment.firms:
                        agent.production_wage(environment, time)
                        #print(f"\n PAID WAGES {agent.identifier}!!! \n")
                        
    # ------------------------------------------------------------------------- 

    # -------------------------------------------------------------------------
    # output_consumption(self, environment, time)
    # Loop through nodes in consumption network and ration output for each 
    # household and all firms
    # -------------------------------------------------------------------------
    def output_consumption(self, environment, time):
        # # Set Date Time from time
        # year,julian = [2021,time]
        # date_time = datetime.datetime(year, 1, 1)+datetime.timedelta(days=julian -1)
        # # Year Month Day
        # year = int(date_time.strftime("%y"))
        # month = int(date_time.strftime("%m"))
        # day = date_time.strftime("%d")
        # # Find last day of month
        # end_day = (datetime.date(year + int(month/12), month%12+1, 1) -datetime.timedelta(days=1)).strftime("%d")
        # Production on the first of the month
        if time > 0:
            import numpy as np

            G = environment.consumption_network #Get consumption network

            for node in list(G.nodes(data=True)): # loop through nodes
                if node[1]["id"] == "firm": # for all firms
                    firm = environment.get_agent_by_id(node[0])
                    supply_frac = np.random.uniform(-1, 0.3, len(G.adj[node[0]]))
                    supply_frac[supply_frac<0] = 0
                    # If no house has positive demand, then randomly assign total consumption to a single household
                    if supply_frac.sum() == 0:
                       supply_frac[np.random.choice(np.array(range(len(supply_frac))), 1)[0]] = 1
                    supply_frac = np.round(firm.supply * supply_frac/(supply_frac.sum()), 6)
            # G = environment.consumption_network #Get consumption network
            # for node in list(G.nodes(data=True)): # loop through nodes
            #     if node[1]["id"] == "firm": # for all firms
            #         firm = environment.get_agent_by_id(node[0])
            #         supply_frac = []    # create empty list of fractional supply
            #         supply = range(firm.supply) # create list of units of output
            #         it = iter(supply)   # create iterable list of units of output
            #         hh_num = len(G.adj[node[0]]) # determine number of households that are connected to firm in consumption network
            #         from itertools import islice
            #         size = len(supply)  # determine number of units of output
            #         for i in range(hh_num-1,0,-1): # loop through n-1 households 
            #             s = random.randint(0, hh_num - i) # create min and max amount of consumption
            #             supply_frac.append(list(islice(it,0,s)))    # determine which units of output ith household consumes and add to supply list
            #             size -= s   # reduce number of units available
            #         supply_frac.append(list(it))    # add remaining units to final household
            #         supply_frac = [len(u) for u in  supply_frac]    # count number of units demanded per household
            #         print(f"{node[0]}: {supply_frac}")
            #         # Loop through households and number of units allocated and create deposit transaction
            #       for house, k in zip(list(G.adj[node[0]]), supply_frac):
                    for house, k in zip(list(G.adj[node[0]]), supply_frac):
                        if k == 0:
                            pass
                        elif k > 0:  
                            hh = environment.get_agent_by_id(house)
                            hh_bank_acc = list(environment.bank_network.adj[hh.identifier])[0]
                            firm_bank_acc = list(environment.bank_network.adj[firm.identifier])[0]
                            consumption_demand = {"type_": "deposit", "from_" : hh.identifier, "to" : firm.identifier, "amount" : k, "bank_from":hh_bank_acc, "bank_to":firm_bank_acc, "time" : time}
                            hh.deposits_payment(environment, consumption_demand, time)
                        #print(f"{hh.identifier} purchased {k} units of output from {firm.identifier}")
                # Set remaining supply at firm to zero.        
                    firm.supply -= supply_frac.sum()
                    firm.sales += supply_frac.sum()
        environment.deposits_period.append(environment.total_deposit_payments)
    # -------------------------------------------------------------------------
 

    # -------------------------------------------------------------------------
    # net_settles(environment, time)
    # This function settles the transactions following the shock. If from and 
    # to are at the same bank then transaction is settled. If different banks
    # then only every fourth period is settled.
    # -------------------------------------------------------------------------
    def net_settle(self, environment, time):
        if time > 0 and time%environment.batch == 0:
            environment.get_agent_by_id("ach").batch_settle(environment, time)
            # Loop through banks
            for bank in environment.banks:
                bank.settle_ach_payments(environment, time)
                #print(bank.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # settle_interbank_loans(environment, time)
    # This function settles all interbank loans at beginning of period
    # -------------------------------------------------------------------------
    def settle_interbank_loans(self, environment, time):
        if time > 0:# and time%(environment.batch + 1) == 0:
            for bank in environment.banks:
                bank.settle_interbank_loan(environment, time)
                #print(bank.balance_sheet())
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # settle_interbank_loans(environment, time)
    # This function settles all interbank loans at beginning of period
    # -------------------------------------------------------------------------
    def settle_central_bank_loans(self, environment, time):
        if time > 0:# and time%(environment.batch*2 + 1) == 0:
            for bank in environment.banks:
                central_bank_loans_amount = bank.get_account("loans_central_bank")
                if round(central_bank_loans_amount, 5) > 0:
                    central_bank_loan_settle_tranx = {"type_": "loans_central_bank", "bank_from": "central_bank", "bank_to" : bank.identifier, "amount" : central_bank_loans_amount, "time" : time}
                    environment.get_agent_by_id("central_bank").settle_central_bank_loan(environment, central_bank_loan_settle_tranx, time)
                #print(bank.balance_sheet())
    # ------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # settle_household_loans(environment, time)
    # This function settles all household loans at beginning of period
    # Households ensure that they either have deposits or loans and any excess 
    # deposits pay off loans
    # -------------------------------------------------------------------------
    def settle_household_loans(self, environment, time):
        if time > 0:
            for house in environment.households:
                deposits = house.get_account("deposits")
                loans = house.get_account("loans")
                if loans > 0 and deposits > 0:
                    if loans > deposits:
                        #print(f"{house.identifier} repaid {deposits} out of {loans} worth of loans")
                        house.loan_repay(environment, deposits, time) #Pay off as much loans as deposits
                        
                    elif loans < deposits:
                        #print(f"{house.identifier} repaid {loans} out of {loans} worth of loans")
                        house.loan_repay(environment, loans, time) #Pay off all loans
                        
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # check_reserve_requirements
    # determine which banks have reserve deficits and which have surplus deficients
    # for banks with deficits introduce interbank loans from surplus banks
    # once all surpluses are exhuasted banks take out loans from CB
    # -------------------------------------------------------------------------
    def check_reserve_requirements(self, environment, time):
        from random import shuffle
        #from numpy import floor
        # Required reserves initiation
        # At time 0, banks determine deposit level, 2% of deposits need to be held in reserves.
        # Remaining reserves drained through OMO with CB
        if time == 0:
            for bank in environment.banks:
                excess_reserves = bank.check_required_reserves()
                if excess_reserves > 0:
                    # Drain excess reserves through OMO purchase
                    sell_omo_tranx = {"type_": "open_market_operations", "bank_from": "central_bank", "bank_to" : bank.identifier, "amount" : excess_reserves, "time" : time}
                    environment.get_agent_by_id("central_bank").sell_open_market_operations(environment, sell_omo_tranx, time)

        # Required reserves during simulation
        if time > 0:# and time%(environment.batch) == 0:
            # Create list of banks and reserve status
            bank_deficit = {} # Deficit dict
            bank_surplus = {} # Surplus dict
            deposits = 0
            for bank in environment.banks:
                deposits += bank.get_account("deposits")
                excess_reserves = bank.check_required_reserves()
                if excess_reserves < 0:
                    bank_deficit[bank.identifier] = (abs(excess_reserves)) # Add bank to deficit dict if applicable
                elif excess_reserves > 0:
                    bank_surplus[bank.identifier] = (abs(excess_reserves)) # Add bank to surplus dict if applicable
            #print(f"Bank_Deficit \n {bank_deficit}")
            #print(f"Bank_Surplus \n {bank_surplus}")

            # Check if overall reserve requirement for banks met

            reserves_required = deposits * 0.025
            reserves_total = environment.get_agent_by_id("central_bank").get_account("reserves")
            reserve_residual = round(reserves_total - reserves_required, 6)

            #print(f"\n reserve_residual {reserve_residual} \n")

            # Loop through banks with surplus and drain surplus

            if reserve_residual > 0:
                reserve_residual = (abs(reserve_residual))
                #print(f"Overall excess reserves of {reserve_residual}")
                bank_surplus_keys = list(bank_surplus) # Create random order of banks with surplus for random matching
                shuffle(bank_surplus_keys)
                # Loop through banks with surplus and pay min of excess reserves or entire surplus
                while round(reserve_residual) > 1 and round(sum(bank_surplus.values()), 3) > 0:
                    res_paid = 0
                    for bank_surp in bank_surplus_keys:
                        amount = min(reserve_residual, bank_surplus[bank_surp])
                        sell_omo_tranx = {"type_": "open_market_operations", "bank_from": "central_bank", "bank_to" : bank_surp, "amount" : amount, "time" : time}
                        environment.get_agent_by_id("central_bank").sell_open_market_operations(environment, sell_omo_tranx, time)
                        bank_surplus[bank_surp] -= amount
                        res_paid += amount
                        if bank_surplus[bank_surp] == 0:
                            bank_surplus_keys.remove(bank_surp)
                            del bank_surplus[bank_surp]
                    reserve_residual -= res_paid


            # Loop through banks with deficit and increase reserves

            elif reserve_residual < 0:
                reserve_residual = abs(reserve_residual)
                #print(f"Overall deficit reserves of {reserve_residual}")
                bank_deficit_keys = list(bank_deficit) # Create random order of banks with deficit for random matching
                shuffle(bank_deficit_keys)
                # Loop through banks with deficits and pay min of average deficit reserves or entire deficit
                while round(reserve_residual) > 1:
                    res_paid = 0
                    for bank_def in bank_deficit_keys:
                        amount = min(reserve_residual, bank_deficit[bank_def])
                        purchase_omo_tranx = {"type_": "open_market_operations", "bank_from": "central_bank", "bank_to" : bank_def, "amount" : amount, "time" : time}
                        environment.get_agent_by_id("central_bank").purchase_open_market_operations(environment, purchase_omo_tranx, time)
                        bank_deficit[bank_def] -= amount
                        res_paid += amount
                        if bank_deficit[bank_def] == 0:
                            bank_deficit_keys.remove(bank_def)
                            del bank_deficit[bank_def]
                    reserve_residual -= res_paid
            
            # If any banks have deficit reserves, loop through deficit banks from largest to smallest
            # and create interbank loan from surplus banks that have largest surplus. Starts with largest 
            # deficit and largest surplus. If deficit is greater than surplus then all surplus is loaned to 
            # deficit banks and next surplus is used for further interbank loan. If surplus is larger than 
            # deficit, then interbank loan size of deficit is created and next deficit bank is called.
            # Loop continues until all deficits are overcome through interbank loans or no more surplus remains
            # and banks go to central bank for CB loans to ensure reserve requirements are met

            if len(bank_deficit) > 0: # Check if any deficit banks
                for bank, value in dict(bank_deficit).items():  # Loop through deficit bank dict
                    bank_neighbours = environment.interbank_network.adj[bank] # Determine which banks are in deficit banks funding neighbourhood
                    bank_surplus_keys = list(bank_surplus) # Create random order of banks with surplus for random matching
                    shuffle(bank_surplus_keys)
                    for bank_surp in bank_surplus_keys: # Loop through surplus banks
                        if bank_surp in bank_neighbours: # Check if surplus bank is in funding neighbourhood
                            res_def = bank_deficit[bank] - bank_surplus[bank_surp] # Determine deficit and surplus residual
                            if res_def < 0: # Check is surplus is larger than deficit
                                # Create interbank loan the size of entire deficit
                                interbank_loan_tranx = {"type_": "interbank_loan", "bank_from": bank, "bank_to" : bank_surp, "amount" : bank_deficit[bank], "time" : time}
                                environment.get_agent_by_id(bank_surp).issue_interbank_loan(environment, interbank_loan_tranx, time)
                                # Reduce bank surplus
                                bank_surplus[bank_surp] -= bank_deficit[bank]
                                # Remove deficit bank from deficit dict
                                bank_deficit.pop(bank)
                                # Break from inner loop of surplus banks to outer loop of deficit banks
                                break
                            elif res_def >= 0: # Check is deficit is larger than surplus
                                # Create interbank loan the size of entire surplus
                                interbank_loan_tranx = {"type_": "interbank_loan", "bank_from": bank, "bank_to" : bank_surp, "amount" : bank_surplus[bank_surp], "time" : time}
                                environment.get_agent_by_id(bank_surp).issue_interbank_loan(environment, interbank_loan_tranx, time)
                                # Reduce bank deficit
                                bank_deficit[bank] -= bank_surplus[bank_surp]
                                # Remove surplus bank from deficit dict
                                del bank_surplus[bank_surp]

            # If banks remain with deficits then take out CB loans through deposit facility for remaining deficits
            if len(bank_deficit) > 0:
                if sum(bank_deficit.values()) > 0:
                    for bank, value in dict(bank_deficit).items():
                        central_bank_loan_tranx = {"type_": "loans_central_bank", "bank_from": bank, "bank_to" : "central_bank", "amount" : bank_deficit[bank], "time" : time}
                        environment.get_agent_by_id("central_bank").issue_central_bank_loan(environment, central_bank_loan_tranx, time)
                        del bank_deficit[bank]

            # If banks remain with surplus then CB sells OMO to bank for remaining surplus
            if len(bank_surplus) > 0:
                if sum(bank_surplus.values()) > 0:
                    for bank, value in dict(bank_surplus).items():
                        sell_omo_tranx = {"type_": "open_market_operations", "bank_from": "central_bank", "bank_to" : bank, "amount" : bank_surplus[bank], "time" : time}
                        environment.get_agent_by_id("central_bank").sell_open_market_operations(environment, sell_omo_tranx, time)
                        del bank_surplus[bank]

        # for bank in environment.banks:
        #     print(bank.balance_sheet())

    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # write_agent_balance_sheets(environment, time)
    # Loop through each class of agent, call balance sheet method, record in 
    # json file
    # -------------------------------------------------------------------------
    def write_agent_balance_sheets(self,  environment, time):
        import json

        if time == 0:
            self.file_name_dict = {}
            for agent_list in environment.agents:
                id_ = agent_list[0].identifier.split("_")

                if self.environment.num_simulations > 1:
                    # And split the name into two parts, before .csv and .csv if it exists
                    # Then add a unique identifier in the middle
                    # (assuming the script does not run faster than a milisecond)
                    import datetime
                    import time as tm
                    timestamp = datetime.datetime.fromtimestamp(tm.time()).strftime('%Y_%m_%d_%H_%M_%S_%f')
                    file_output = str('measurements/' + id_[0] + '_output' + timestamp + '.json')
                    self.file_name_dict[id_[0]] = file_output

                else:
                    file_output = str('measurements/' + id_[0] + '_output' '.json')
                    self.file_name_dict[id_[0]] = file_output

        # Loop through agent types
        for agent_list in environment.agents:
            id_ = agent_list[0].identifier.split("_") # Split agent id to determine type of agent
            agent_balance_sheets = [] # Empty list for storing balance sheets
            for agent in agent_list: # Loop through different individual agents of same type
                agent_balance_sheets.append(agent.balance_sheet()) # Call balance sheet method and append list

            if time == 0: # If time 0, clear json file and write step time as key and list of balance sheets as values
                open(self.file_name_dict[id_[0]], 'w')
                with open(self.file_name_dict[id_[0]], 'w') as output:
                    output.write( "[{}]".format(json.dumps({time:agent_balance_sheets})))
            elif time > 0: # write step time as key and list of balance sheets as values with special formatting
                with open(self.file_name_dict[id_[0]], 'r+') as output:
                    output.seek(0,2)
                    position = output.tell() -1
                    output.seek(position)
                    output.write( ",{}]".format(json.dumps({time:agent_balance_sheets})))
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # write_cbdc_transactions(environment, time)
    # This function settles the transactions following the shock. If from and 
    # to are at the same bank then transaction is settled. If different banks
    # then only every fourth period is settled.
    # -------------------------------------------------------------------------
    # def write_cbdc_transactions(self,  environment, time):
    #     # Set Date Time from time
    #     year,julian = [2021,time]
    #     date_time = datetime.datetime(year, 1, 1)+datetime.timedelta(days=julian -1)
    #     # Year Month Day
    #     year = int(date_time.strftime("%y"))
    #     month = date_time.strftime("%m")
    #     day = date_time.strftime("%d")
    #     # Find last day of month
    #     end_day = (datetime.date(year + int(int(month)/12), int(month)%12+1, 1) -datetime.timedelta(days=1)).strftime("%d")

    #     if time > 0:
    #     # Repay loans and contracts expire on the last day of the month
    #         if end_day == day:
    #             # Record CBDC Transactions
    #             import json
    #             file_cbdc = str('cbdc_transactions/cbdc_dict_' + month + '.json')
    #             with open(file_cbdc, 'w') as cbdc:
    #                 json.dump(environment.cbdc_transactions, cbdc)
    #             environment.cbdc_transactions = []
    # -------------------------------------------------------------------------