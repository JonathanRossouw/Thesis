#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
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
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""


#-------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------
if __name__ == '__main__':
	import sys
	#sys.path.append('src/')

	if (len(sys.argv) != 3):
			print "Usage: ./generate_banks.py numBanks directory"
			sys.exit()

	numBanks = sys.argv[1]
	
	for i in range(int(float(numBanks))):
		fileName = sys.argv[2] + "bank_"+str(i)
		# the following code ensures leading zeros so filenames will be in the right order
		# for python to read in. Also, bank names are sorted properly in activeBanks of madfimas
		# this code is ugly, but works...
		fileName += ".xml"
		outFile = open(fileName,  'w')
		
		text = "<bank identifier= 'bank_" + str(i) + "'>\n"
		text = text + "    <parameter type='static' name='interest_rate_loans' value='0.00'></parameter>\n"
		text = text + "    <parameter type='static' name='interest_rate_deposits' value='0.00'></parameter>\n"
		text = text + "    <transaction type='deposits' asset='' from='household_test_config_id' to='bank_test_config_id' amount='0' interest='0.00' maturity='0' time_of_default='-1'></transaction>\n"
		text = text + "    <parameter name='bank_acc' value='bank_" + str(i) +"'></parameter>\n"
		text = text + "</bank>\n"
		outFile.write(text)
		outFile.close()