# Masters Thesis Log
This README serves as a log for changes made to the Agent Based Model I will be using for my thesis.


## 10 September

### Current Thesis Topic
Using ABM to create a model for transactions between households and firms which use banks as intermediaries. The model should include realistic featuers of a modern payments system e.g. time delays when transfering funds between banks, costs of transactions, loans between banks at a market related interest rate. Then a CBDC should be introduced to the model following a realistic implementation of the technology. The improvements in total welfare as measured by increase in the sum of utility functions of the households and firms could be used to determine usefulness of CBDC.


### Structure

The model has 6 agents, 4 households and 2 banks. Each household is affiliated to a bank. In the initial period, each household is endowed with 24 units of "deposits". The household balance consists of "deposits" plus "receipts" minus "paymets". Each period, 2 households are randomly selected to experience a payment shock. The shock forces the household to make a payment to a random other household. The amount is a stochastic variable conisting of a proportion of positive current balance. The proportion is drawn from a uniform distribution between 0.1 and 0.3. The payment shock is recorded as a "payment" transaction from the household to its bank. The bank then either settles the transaction by making a "receipt" transaction to the intended recipient household. If the household making the payment and the household receiving the payment bank with the same bank then the settlement takes place. Otherwise, the bank stores the payment for settlement when the period is a multiple of the "batch" length. This structure intends to model the automatic clearing house and RTGS mechanism in a modern payment system.

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