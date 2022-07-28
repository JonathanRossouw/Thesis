#!/usr/bin/env python
# [SublimeLinter pep8-max-line-length:300]
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
import sys
import xml.etree.ElementTree as ET

sys.path.append('src/')


if __name__ == '__main__':

    if (len(sys.argv) != 2):
        sys.exit("Usage: num_banks directory")

    num_banks = int(sys.argv[0])

    for i in range(num_banks):
        file_number = str(i).zfill(len(str(num_banks)))  # Add leading zeros
        filename = sys.argv[2] + "bank-" + str(i) + ".xml"

        # Build xml
        root = ET.Element("bank", identifier=('bank_'+str(i)))
        ET.SubElement(root, "parameter", type="static", name="interest_rate_loans",
                      value="0.00")
        ET.SubElement(root, "parameter", type="static", name="interest_rate_deposits",
                      value="0.00")
        ET.SubElement(root, "transaction", asset='', from_='household_test_config_id', to='bank_test_config_id',
                      amount='0', interest='0.00', maturity='0', time_of_default='-1')
        ET.SubElemt(root, name='bank_acc', value=("bank_"+str(i)))

        # Save xml
        tree = ET.ElementTree(root)
        tree.write(filename)
