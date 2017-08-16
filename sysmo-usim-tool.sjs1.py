#!/usr/bin/env python
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
from card import *
from simcard import *
from sysmo_usimsjs1 import *


def banner():
	print "sysmoUSIM-SJS1 parameterization tool"
	print "Copyright (c)2017 Sysmocom s.f.m.c. GmbH"
	print ""


def helptext():
	print " * Commandline options:"
	print "   -v, --verbose .................. Enable debug output (trace APDUs)"
	print "   -a, --adm1 CHV ................. Administrator PIN (e.g 55538407)"
	print "   -u, --usim ..................... Enable USIM mode"
	print "   -c, --classic .................. Disable USIM mode (make classic-sim)"
	print "   -m, --mode ..................... Display mode (classic-sim or USIM?)"
	print "   -t, --auth ..................... Show Authentication algorithms"
	print "   -T, --set-auth 2G:3G ........... Set 2G/3G Auth algo (e.g. 3:3)"
	print "   -l, --milenage ................. Show milenage parameters"
	print "   -L, --set-milenage HEXSTRING ... Set milenage parameters"
	print "   -o, --opc ...................... Show OP/c configuration"
	print "   -O, --set-op HEXSTRING ......... Set OP value"
	print "   -C, --set-opc HEXSTRING ........ Set OPc value"
	print "   -k, --ki ....................... Show KI value"
	print "   -K, --set-ki ................... Set KI value"
	print ""


def main(argv):

	banner()
	getopt_adm1 = None
	getopt_write_sim_mode = None # True = USIM, False = classic SIM
	getopt_show_sim_mode = False
	getopt_verbose = False
	getopt_show_auth = False
	getopt_write_auth = None
	getopt_show_milenage = False
	getopt_write_milenage = None
	getopt_show_opc = False
	getopt_write_op = None
	getopt_write_opc = None
	getopt_show_ki = None
	getopt_write_ki = None
	getopt_force = False
	getopt_write_iccid = None

	# Analyze commandline options
	try:
		opts, args = getopt.getopt(argv,
			"hva:ucmtT:lL:oO:C:kK:fiI:",
				["help","verbose","adm1=","usim","classic",
				 "mode","auth","set-auth=","milenage",
				 "set-milenage","opc","set-op=","set-opc=",
				 "ki","set-ki=","force","iccid","set-iccid="])
	except getopt.GetoptError:
		print " * Error: Invalid commandline options"
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			helptext()
			sys.exit()
		elif opt in ("-v", "--verbose"):
			getopt_verbose = True
		elif opt in ("-a", "--adm1"):
			getopt_adm1 = ascii_to_list(arg)
		elif opt in ("-u", "--usim"):
			getopt_write_sim_mode = True
		elif opt in ("-c", "--classic"):
			getopt_write_sim_mode = False
		elif opt in ("-m", "--mode"):
			getopt_show_sim_mode = True
		elif opt in ("-t", "--auth"):
			getopt_show_auth = True
		elif opt in ("-T", "--set-auth"):
			getopt_write_auth = arg.split(':',1)
		elif opt in ("-l", "--milenage"):
			getopt_show_milenage = True
		elif opt in ("-L", "--set-milenage"):
			getopt_write_milenage = asciihex_to_list(arg)
		elif opt in ("-o", "--opc"):
			getopt_show_opc = True
		elif opt in ("-O", "--set-op"):
			getopt_write_op = asciihex_to_list(arg)
		elif opt in ("-C", "--set-opc"):
			getopt_write_opc = asciihex_to_list(arg)
		elif opt in ("-k", "--ki"):
			getopt_show_ki = True
		elif opt in ("-K", "--set-ki"):
			getopt_write_ki = asciihex_to_list(arg)
		elif opt in ("-f", "--force"):
			getopt_force = True
		elif opt in ("-I", "--set-iccid"):
			getopt_write_iccid = asciihex_to_list(pad_asciihex(arg))


	if not getopt_adm1:
		print " * Error: adm1 parameter missing -- exiting..."
		print ""
		sys.exit(1)


	# Claim terminal
	print "Initializing smartcard terminal..."
	c = Card(getopt_verbose)
	sim = Simcard(c)
	print("")

	print "Detected Card ICCID: ", sim.card.get_ICCID()
	print ""

	# Authenticate
	print "Authenticating..."
	if sysmo_usim_admin_auth(sim, getopt_adm1, getopt_force) == False:
		print ""
		print "   ===  Authentication problem! The Card will permanently   ==="
		print "   === lock down after 3 failed attemts! Double check ADM1! ==="
		print ""
		exit(1)
	print("")

	sim.card.SELECT_ADF_USIM()
	print "Detected Card IMSI: ", sim.card.get_imsi()
	print ""

	# Execute tasks
	if getopt_write_sim_mode != None:
		print "Programming SIM-Mode..."
		sysmo_usim_write_sim_mode(sim, getopt_write_sim_mode)
		print("")

	if getopt_show_sim_mode:
		print "Reading SIM-Mode..."
		sysmo_usim_show_sim_mode(sim)
		print("")

	if getopt_write_auth:
		print "Programming Authentication parameters..."
		sysmo_usim_write_auth_params(sim,
			int(getopt_write_auth[0]),
			int(getopt_write_auth[1]))
		print("")

	if getopt_show_auth:
		print "Reading Authentication parameters..."
		sysmo_usim_show_auth_params(sim)
		print("")

	if getopt_write_milenage:
		print "Programming Milenage parameters..."
		ef_mlngc = SYSMO_USIMSJS1_FILE_EF_MLNGC(getopt_write_milenage)
		sysmo_usim_write_milenage_params(sim, ef_mlngc)
		print("")

	if getopt_show_milenage:
		print "Reading Milenage parameters..."
		sysmo_usim_show_milenage_params(sim)
		print("")

	if getopt_write_op:
		print "Writing OP value..."
		sysmo_usim_write_opc_params(sim, 0, getopt_write_op)
		print("")

	if getopt_write_opc:
		print "Writing OPC value..."
		sysmo_usim_write_opc_params(sim, 1, getopt_write_opc)
		print("")

	if getopt_show_opc:
		print "Reading OP/C value..."
		sysmo_usim_show_opc_params(sim)
		print("")

	if getopt_write_ki:
		print "Writing KI value..."
		sysmo_usim_write_ki_params(sim, getopt_write_ki)
		print("")

	if getopt_show_ki:
		print "Reading KI value..."
		sysmo_usim_show_ki_params(sim)
		print("")

	if getopt_write_iccid:
		print "Writing ICCID value..."
		sysmo_usim_write_iccid(sim, getopt_write_iccid)
		print("")

	print "Done!"


if __name__ == "__main__":
	main(sys.argv[1:])



