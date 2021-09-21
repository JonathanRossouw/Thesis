# Masters Thesis Log
This README serves as a log for changes made to the Agent Based Model I will be using for my thesis.

## 24 September

### Current Thesis Topic 
Using ABM to create a model for transactions between households and firms which use banks as intermediaries. The model should include realistic featuers of a modern payments system e.g. time delays when transfering funds between banks, costs of transactions, loans between banks at a market related interest rate. Then a CBDC should be introduced to the model following a realistic implementation of the technology. The improvements in total welfare as measured by increase in the sum of utility functions of the households and firms could be used to determine usefulness of CBDC.

### Structure

The model has 55 agents, 50 households and 5 banks. Each household is affiliated to a bank. The households are connected to each other through a random directed network. The network has an exogenous randomness parameter set to 0.2. Each household is randomly assigned as a customer of a bank.

In the initial period, each household is endowed with 24 units of "deposits" which is the deposited at the household's bank through a "deposits" transaction. The household balance consists of "deposits" plus the sum of "receipts" less the sum of  "payments". Each period, households are randomly selected following a bernoulli random variable to experience a payment shock. The shock forces the household to make a payment along a randomly selected edge to another household. The amount is a stochastic variable conisting of a proportion of positive current balance. The proportion is drawn from a uniform distribution between 0.2 and 0.7. The bank balance is determined by the sum of all the "deposits" plus the sum of all "settle" transactions received less the sum of all the "settle" transactions paid.

The payment shock is recorded as a "payment" transaction from the household to its bank. The bank settles the transaction by making a "receipt" transaction to the intended recipient household. If the household making the payment and the household receiving the payment bank with the same bank then the settlement takes place. Otherwise, the bank stores the payment for settlement when the period is a multiple of the "batch" length. Settlement is recorded by making a "settle" transaction from the bank to the recipient household's bank as well as a "receipt" transaction to the recipient household. This structure intends to model the automatic clearing house and RTGS mechanism in a modern payment system.

Households and banks can be randomly generated through the Br_Generate_Agents class. Generated households and banks can be deleted after simulation using the 12th Notebook cell with remove = True.

### Code Changes

The following lists the additions to the baseagents from Black Rhino ABM found at: https://github.com/blackrhinoabm/BlackRhino/tree/master

Network
* Methods
    - payment_shock_transaction (Method is now called in Updater class to loop through nodes in network. Transaction information is now stored at the bank rather than environment. Transaction now includes information of recipient household's bank.)
    - net_settle_transaction (Method is now called in Updater class to loop through banks. From transacionts between households at same bank, no changes are made to the bank balance. For transactions made between households at different banks, a "settle" transaction is made between banks while a "receipt" transaction is made between bank and recipient household)

Bank
* Variables
    - store (empty list that stores transactions)
    - households (empty list that stores identifiers for all households that are customers of bank)
* Methods
    - get_households (Loop through all households in network and appends household identifier to list if household is customer of bank)
    - balance (Set assets and liabilities equal to sum of "deposits". For all "settle" transaction, if tranaction is from bank then subtract from assets and liabilities. If transaction is to bank, then add to assets and liabilities. Balance is equal to assets which is equal to liabilities)

Updater
* Methods
    - endow_deposits (Create "deposits" transaction from households to bank where they are customers)
    - payment_shock (Loop through all nodes in network. Draw random bernoulli variable. If one then call Network class method payment_shock_transaction and perform payment shock. Otherwise pass to next node.)
    - net_settle (Loop through all banks and call Network class method net_settle_transaction)

Environment
* Methods 
    - initialize (Loop through all banks and call Bank class method get_households to record which households are customers to which banks)

Br_Generate_Agents
* Variables
    - numHouseholds (Number of households to generate)
    - numBanks (Number of banks to generate)
    - householdfileName (Directory where households xml files are stored)
    - bankfileName (Directory where banks xml files are stored)

* Methods 
    - generate_households (Read in number of households, banks and directory for household xml files. Give household name and randomly assign to bank. Create xml file and save to directory)
    - generate_banks (Read in number banks and directory for banks xml files. Give banks name. Create xml file and save to directory)

## 17 September 

### Current Thesis Topic 
Using ABM to create a model for transactions between households and firms which use banks as intermediaries. The model should include realistic featuers of a modern payments system e.g. time delays when transfering funds between banks, costs of transactions, loans between banks at a market related interest rate. Then a CBDC should be introduced to the model following a realistic implementation of the technology. The improvements in total welfare as measured by increase in the sum of utility functions of the households and firms could be used to determine usefulness of CBDC.

### Structure

The model has 10 agents, 8 households and 2 banks. Each household is affiliated to a bank. The households are connected to each other through a random directed network. The network has an exogenous randomness parameter set to 0.5. 

In the initial period, each household is endowed with 24 units of "deposits". The household balance consists of "deposits" plus the sum of "receipts" less the sum of  "payments". Each period, half of the households are randomly selected to experience a payment shock. The shock forces the household to make a payment along a randomly selected edge to another household. The amount is a stochastic variable conisting of a proportion of positive current balance. The proportion is drawn from a uniform distribution between 0.2 and 0.7. 

The payment shock is recorded as a "payment" transaction from the household to its bank. The bank settles the transaction by making a "receipt" transaction to the intended recipient household. If the household making the payment and the household receiving the payment bank with the same bank then the settlement takes place. Otherwise, the bank stores the payment for settlement when the period is a multiple of the "batch" length. This structure intends to model the automatic clearing house and RTGS mechanism in a modern payment system.

### Code Changes

The following lists the additions to the baseagents from Black Rhino ABM found at: https://github.com/blackrhinoabm/BlackRhino/tree/master

Network
* Variables
    - contracts (empty networkx directed graph)

* Methods
    - initialize_networks (Create random networkx directed graph with number of nodes equal to number of households. Randomness parameter is set exogenously. Node attributed set as the household identifier)

Environment 
* Variables
    - network (empty Network class instance)

* Methods
    - initialize_network (Initialize Network instance. Call initialize_networks method and set enivornment.network class variable as the network.)
    - initialize (Call initialize_network method)

Updater
* Variable
    - payment_shock (Changed random recipient of payment. Now recipient is randomly select household that has edge with payment shock household)

## 10 September

### Current Thesis Topic
Using ABM to create a model for transactions between households and firms which use banks as intermediaries. The model should include realistic featuers of a modern payments system e.g. time delays when transfering funds between banks, costs of transactions, loans between banks at a market related interest rate. Then a CBDC should be introduced to the model following a realistic implementation of the technology. The improvements in total welfare as measured by increase in the sum of utility functions of the households and firms could be used to determine usefulness of CBDC.


### Structure

The model has 6 agents, 4 households and 2 banks. Each household is affiliated to a bank. In the initial period, each household is endowed with 24 units of "deposits". The household balance consists of "deposits" plus "receipts" minus "payments". Each period, 2 households are randomly selected to experience a payment shock. The shock forces the household to make a payment to a random other household. The amount is a stochastic variable conisting of a proportion of positive current balance. The proportion is drawn from a uniform distribution between 0.1 and 0.3. The payment shock is recorded as a "payment" transaction from the household to its bank. The bank then either settles the transaction by making a "receipt" transaction to the intended recipient household. If the household making the payment and the household receiving the payment bank with the same bank then the settlement takes place. Otherwise, the bank stores the payment for settlement when the period is a multiple of the "batch" length. This structure intends to model the automatic clearing house and RTGS mechanism in a modern payment system.

### Code Changes

The following lists the additions to the baseagents from Black Rhino ABM found at: https://github.com/blackrhinoabm/BlackRhino/tree/master

Households
* Variables
    - bank_acc (bank that household banks with)

* Methods 
    - balance (Determines households available balance for payment shock. Calculated from the sum of deposits and receipt transactions less the sum of all payment shock transactions)

Banks
* Methods 
    - balance (Determines banks current stored balance for settlement. Calculated from the sum payment transactions less the sum of all receipts from settling transactions)

Updater 
* Methods 
    - net_deposits (At specified times, including time 0, transaction from household to itself of type "deposits" and amount equal to state variable "deposits" set in household config file.)
    - payment_shock (Each period, random propoertion of household receive payment shock. Shock is randomly drawn proportion from uniform(0.1, 0.3) times the current available balance of household. Recipient of payment is randomly selected from other households. Payment transaction from household to household's bank takes place. Details of transaction are stored for batching and settling.)
    - net_settle (For transactions involving households with same bank, settlement takes place each period. For transactions involving households that bank with different banks, transactions are settled after after a prespecified interval. Settlement consists of a transaction of receipt type from bank to household that matches payment shock transactions. Once transaction is settled, transaction details are removed from stored list of transactions.)

Measurements

* Methods 
    - wrapper (measure each households current available balance, the sum of all avaialble balances households, the sum of stored transactions at banks)

Environment
* Variables
    - store (list of dictionaries of transaction details)
    - batch (float value read from config files of frequency of batching settlement)

* Methods 
    - initialize (self.batch set equal to batch state variable read from config file)



## 30 August
### Current Thesis Topic
Using ABM to create a model for transactions between households and firms which use banks as intermediaries. The model should include realistic featuers of a modern payments system e.g. time delays when transfering funds between banks, costs of transactions, loans between banks at a market related interest rate. Then a CBDC should be introduced to the model following a realistic implementation of the technology. The improvements in total welfare as measured by increase in the sum of utility functions of the households and firms could be used to determine usefulness of CBDC.

### Setup
The model follows from the Solow growth model example from the Black Rhino ABM found at: https://github.com/blackrhinoabm/BlackRhino/tree/master/examples/solow 

* Agents
    - 2 housholds (Endowment 12. H1 with B1 and H2 with B2. Both H's work at F)
    - 2 banks (Initial transaction: H1 deposit 15 units at B1, H2 deposit 15 units at B2)
    - 1 firm (H1 and H2 each receive capital of 15 units from F)

### Code Changes

* Firm method: get_parameters_from_file (Altered template method such that class can read bank parameter from xml file)
* Household method: get_parameters_from_file (Altered template method such that class can read bank parameter from xml file)
* Measurement method: wrapper (Write H1, H2, F deposits and B1 and B2 loans)
* Updater method: net_loans_deposits (Firm and Households set random bank as their bank and determine bank for other party in transaction, if firm and household are same bank then transaction nets, if firm and household are not the same bank then transaction nets every second period i.e. when "time" is even)