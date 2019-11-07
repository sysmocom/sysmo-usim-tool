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
from utils import *
from simcard import *
from sysmo_usimsjs1 import *


def banner():
	print "sysmoUSIM-SJS1 parameterization tool"
	print "Copyright (c)2017 Sysmocom s.f.m.c. GmbH"
	print ""


def helptext():
	print " * Commandline options:"
	print "   -a, --adm1 CHV ................. Administrator PIN (e.g 55538407)"
	print "   -u, --usim ..................... Enable USIM mode"
	print "   -c, --classic .................. Disable USIM mode (make classic-sim)"
	print "   -m, --mode ..................... Display mode (classic-sim or USIM?)"
	print "   -t, --auth ..................... Show Authentication algorithms"
	print "   -T, --set-auth list ............ List available algorithms"
	print "   -T, --set-auth 2G:3G ........... Set 2G/3G Auth algo (e.g. COMP128v1:COMP128v1)"
	print "   -l, --milenage ................. Show milenage parameters"
	print "   -L, --set-milenage HEXSTRING ... Set milenage parameters"
	print "   -o, --opc ...................... Show OP/c configuration"
	print "   -O, --set-op HEXSTRING ......... Set OP value"
	print "   -C, --set-opc HEXSTRING ........ Set OPc value"
	print "   -k, --ki ....................... Show KI value"
	print "   -K, --set-ki ................... Set KI value"
	print "   -s  --seq-parameters ........... Show MILENAGE SEQ/SQN parameters"
	print "   -S  --reset-seq-parameters...... Reset MILENAGE SEQ/SQN parameters to default"
	print "   -I, --set-iccid ................ Set ICCID value"
	print "   -J, --set-imsi ................. Set IMSI value"
	print "   -n, --mnclen ................... Show MNC length value"
	print "   -N, --set-mnclen ............... Set MNC length value"
	print ""


def main(argv):

	banner()
	getopt_adm1 = None
	getopt_write_sim_mode = None # True = USIM, False = classic SIM
	getopt_show_sim_mode = False
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
	getopt_seq_par = False
	getopt_reset_seq_par = False
	getopt_write_imsi = None
	getopt_show_mnclen = None
	getopt_write_mnclen = None

	# Analyze commandline options
	try:
		opts, args = getopt.getopt(argv,
			"ha:ucmtT:lL:oO:C:kK:fiI:sSJ:nN:",
				["help","adm1=","usim","classic",
				 "mode","auth","set-auth=","milenage",
				 "set-milenage","opc","set-op=","set-opc=",
				 "ki","set-ki=","force","iccid","set-iccid=",
				 "seq-parameters", "reset-seq-parameters",
                                 "set-imsi", "set-mnclen", "mnclen"])
	except getopt.GetoptError:
		print " * Error: Invalid commandline options"
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			helptext()
			sys.exit()
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
			if arg.upper() == 'LIST':
				print 'Valid -T arguments are algorithm number or string.'
				print 'Available:'
				print '\n'.join([' %d %s' % entry for entry in sysmo_usim_algorithms])
				sys.exit()
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
		elif opt in ("-s", "--sqe-parameters"):
			getopt_seq_par = True
		elif opt in ("-S", "--reset-sqe-parameters"):
			getopt_reset_seq_par = True
		elif opt in ("-J", "--set-imsi"):
			getopt_write_imsi = asciihex_to_list(pad_asciihex(arg, True, '9'))
		elif opt in ("-n", "--mnclen"):
			getopt_show_mnclen = True
		elif opt in ("-N", "--set-mnclen"):
			getopt_write_mnclen = asciihex_to_list(arg)


	if not getopt_adm1:
		print " * Error: adm1 parameter missing -- exiting..."
		print ""
		sys.exit(1)


	# Claim terminal
	sim = Sysmo_usimsjs1()

	# Authenticate
	if sim.admin_auth(getopt_adm1, getopt_force) == False:
		exit(1)

	# Execute tasks
	if getopt_write_sim_mode != None:
		sim.write_sim_mode(getopt_write_sim_mode)

	if getopt_show_sim_mode:
		sim.show_sim_mode()

	if getopt_write_auth:
		sim.write_auth_params(getopt_write_auth[0], getopt_write_auth[1])

	if getopt_show_auth:
		sim.show_auth_params()

	if getopt_write_milenage:
		ef_mlngc = SYSMO_USIMSJS1_FILE_EF_MLNGC(getopt_write_milenage)
		sim.write_milenage_params(ef_mlngc)

	if getopt_show_milenage:
		sim.show_milenage_params()

	if getopt_seq_par:
		sim.show_milenage_sqn_params()

	if getopt_write_op:
		sim.write_opc_params(0, getopt_write_op)

	if getopt_write_opc:
		sim.write_opc_params(1, getopt_write_opc)

	if getopt_show_opc:
		sim.show_opc_params()

	if getopt_write_ki:
		sim.write_ki_params(getopt_write_ki)

	if getopt_show_ki:
		sim.show_ki_params()

	if getopt_write_iccid:
		sim.write_iccid(getopt_write_iccid)

	if getopt_reset_seq_par:
		sim.reset_milenage_sqn_params()

	if getopt_write_imsi:
		sim.write_imsi(getopt_write_imsi)

	if getopt_show_mnclen:
		sim.show_mnclen()

	if getopt_write_mnclen:
		sim.write_mnclen(getopt_write_mnclen)

	print "Done!"


if __name__ == "__main__":
	main(sys.argv[1:])



