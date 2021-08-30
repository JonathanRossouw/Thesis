# Masters Thesis Log
This README serves as a log for changes made to the Agent Based Model I will be using for my thesis.

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