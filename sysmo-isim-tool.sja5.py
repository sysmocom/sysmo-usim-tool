#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Commandline interface for sysmoISIM-SJA5

(C) 2023 by sysmocom - s.f.m.c. GmbH
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
from sysmo_isim_sja2 import *
from common import *

class Application(Common):

	getopt_dump = False
	getopt_show_tuak_cfg = False
	getopt_write_tuak_cfg = None

	# Automatically executed by superclass
	def _banner(self):
		print("sysmoISIM-SJA5 parameterization tool")
		print("Copyright (c) 2023 sysmocom - s.f.m.c. GmbH")
		print("")


	# Automatically executed by superclass
	def _options(self, opts):
		for opt, arg in opts:
			if opt in ("-d", "--dump"):
				self.getopt_dump = True
			elif opt in ("-w", "--tuak-cfg"):
				self.getopt_show_tuak_cfg = True
			elif opt in ("-W", "--set-tuak-cfg"):
				self.getopt_write_tuak_cfg = arg.split(':', 3)

	# Automatically executed by superclass when -h or --help is supplied as option
	def _helptext(self):
		print("   -d, --dump ..................... Dump propritary file contents")
		print("   -w, --tuak-cfg ................. Show TUAK configuration")
		print("   -W, --set-tuak-cfg R:M:C:K ..... Set TUAK configuration")
		print("")
		print("   For Option -T, the following algorithms are valid:")
		print('\n'.join(['   %d %s' % entry for entry in sysmo_isimsja5_algorithms]))
		print("")
		print("   For Option -W, the following values are applicable:")
		print("   R = RES-Size in bits: 32, 64, 128 or 256")
		print("   M = MAC-A and MAC-S size in bits: 64, 128 or 256")
		print("   C = CK and IK size in bits: 128 or 256")
		print("   K = Number of Keccak iterations: 1-255")
		print("")

	# Automatically executed by superclass before _execute() is called
	def _init(self):
		self.sim = Sysmo_isim_sja5()


	# Automatically executed by superclass
	def _execute(self):

		if self.getopt_dump:
			self.sim.dump()
		elif self.getopt_show_tuak_cfg:
			self.sim.show_tuak_cfg()
		elif self.getopt_write_tuak_cfg:
			self.sim.write_tuak_cfg(self.getopt_write_tuak_cfg[0], self.getopt_write_tuak_cfg[1], \
						self.getopt_write_tuak_cfg[2], self.getopt_write_tuak_cfg[3])

def main(argv):

	Application(argv, "dwW:", ["dump"], True)


if __name__ == "__main__":
	main(sys.argv[1:])
