#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Commandline interface for sysmoUSIM-SJS1

(C) 2017 by Sysmocom s.f.m.c. GmbH
All Rights Reserved

Author: Philipp Maier

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, getopt
from utils import *
from simcard import *
from sysmo_usim_sjs1 import *
from common import *

class Application(Common):

	write_iccid = None
	write_sim_mode = None # True = USIM, False = classic SIM
	show_sim_mode = False
	write_iccid = None
	write_imsi = None


	# Automatically executed by superclass
	def _banner(self):
		print("sysmoUSIM-SJS1 parameterization tool")
		print("Copyright (c)2017-2019 Sysmocom s.f.m.c. GmbH")
		print("")


	# Automatically executed by superclass
	def _options(self, opts):

		for opt, arg in opts:
			if opt in ("-I", "--set-iccid"):
				self.write_iccid = asciihex_to_list(pad_asciihex(arg))
			elif opt in ("-u", "--usim"):
				self.write_sim_mode = True
			elif opt in ("-c", "--classic"):
				self.write_sim_mode = False
			elif opt in ("-m", "--mode"):
				self.show_sim_mode = True


	# Automatically executed by superclass when -h or --help is supplied as option
	def _helptext(self):
		print("   -I, --set-iccid ................ Set ICCID value")
		print("   -u, --usim ..................... Enable USIM mode")
		print("   -c, --classic .................. Disable USIM mode (make classic-sim)")
		print("   -m, --mode ..................... Display mode (classic-sim or USIM?)")
		print("")
		print("   For Option -T, the following algorithms are valid:")
		print('\n'.join(['   %d %s' % entry for entry in sysmo_usim_algorithms]))
		print("")


	# Automatically executed by superclass before _execute() is called
	def _init(self):
		self.sim = Sysmo_usim_sjs1()


	# Automatically executed by superclass
	def _execute(self):

		if self.write_iccid:
			self.sim.write_iccid(self.write_iccid)

		if self.write_sim_mode != None:
			self.sim.write_sim_mode(self.write_sim_mode)

		if self.show_sim_mode:
			self.sim.show_sim_mode()


def main(argv):

	Application(argv, "ucmI:", ["usim", "classic", "mode", "set-iccid="])

if __name__ == "__main__":
	main(sys.argv[1:])



