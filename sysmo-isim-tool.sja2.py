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
from sysmo_isim_sja2 import *
from common import *

class Application(Common):

	getopt_dump = False


	# Automatically executed by superclass
	def _banner(self):
		print("sysmoISIM-SJA2 parameterization tool")
		print("Copyright (c)2019 Sysmocom s.f.m.c. GmbH")
		print("")


	# Automatically executed by superclass
	def _options(self, opts):
		for opt, arg in opts:
			if opt in ("-d", "--dump"):
				self.getopt_dump = True


	# Automatically executed by superclass when -h or --help is supplied as option
	def _helptext(self):
		print("   -d, --dump ..................... Dump propritary file contents")
		print("")
		print("   For Option -T, the following algorithms are valid:")
		print('\n'.join(['   %d %s' % entry for entry in sysmo_isimsja2_algorithms]))
		print("")


	# Automatically executed by superclass before _execute() is called
	def _init(self):
		self.sim = Sysmo_isim_sja2()


	# Automatically executed by superclass
	def _execute(self):

		if self.getopt_dump:
			self.sim.dump()


def main(argv):

	Application(argv, "d", ["dump"])


if __name__ == "__main__":
	main(sys.argv[1:])
