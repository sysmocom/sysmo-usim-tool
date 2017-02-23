#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gadgets to modify SYSMO USIM SJS1 parameters

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

# Some gadgets to handle functions specific to Sysmo USIM SJS1. The gadgets are
# organized as a loose collection of python functions. Each function serves
# a specific task (e.g. modifiying the auth parameters). For each task two
# functions are implemented sysmo_usim_show_...() to inspect the data that is
# intended to be modified and sysmo_usim_write_...() to perform the actual
# modification task.

# Partial File tree:
# The following tree is incomplete, it just contains the propritary files we
# need to perform the tasks implemented below:
#
# [MF 0x3F00]
#  |
#  +--[DF_AUTH 0x7FCC]
#  |   |
#  |   +--[EF_AUTH 0x6F00]
#  |   |
#  |   +--[EF_MLNGC 0x6F01]
#  |
#  +--[DF_GSM 0x7F20]
#      |
#      +--[EF_OPC 0x00F7]
#      |
#      +--[EF_KI 0x00FF]


from card import *
from simcard import *

# Files (propritary)
SYSMO_USIMSJS1_EF_KI = [0x00, 0xFF]
SYSMO_USIMSJS1_EF_OPC = [0x00, 0xF7]
SYSMO_USIMSJS1_DF_AUTH = [0x7F, 0xCC] #FIXME: Manual does not mention name, just called it "DF_AUTH" might be wrong!
SYSMO_USIMSJS1_EF_AUTH = [0x6F, 0x00]
SYSMO_USIMSJS1_EF_MLNGC = [0x6F, 0x01]

# CHV Types
SYSMO_USIMSJS1_ADM1 = 0x0A

# Authentication algorithms (See sysmousim.pdf cap. 8.5)
SYSMO_USIMSJS1_ALGO_MILENAGE = 0x01
SYSMO_USIMSJS1_ALGO_COMP12V1 = 0x03
SYSMO_USIMSJS1_ALGO_XOR2G = 0x04
SYSMO_USIMSJS1_ALGO_COMP128V2 = 0x06
SYSMO_USIMSJS1_ALGO_COMP128V3 = 0x07
SYSMO_USIMSJS1_ALGO_XOR3G = 0x08

# Application identifier
SYSMO_USIM_AID = [0xa0, 0x00, 0x00, 0x00, 0x87, 0x10, 0x02]

# Default content of record No.1 in EF.DIR
SYSMO_USIM_EF_DIR_REC_1_CONTENT = [0x61, 0x19, 0x4f, 0x10] + SYSMO_USIM_AID + \
	[0xff, 0xff, 0xff, 0xff, 0x89, 0x07, 0x09, 0x00, 0x00, 0x50, 0x05,
	 0x55, 0x53, 0x69, 0x6d, 0x31, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
	 0xff, 0xff, 0xff, 0xff, 0xff]

# Abstraction for the file structure of EF.MLNGC, which holds the
# parameters of the milenage authentication algorithm
class SYSMO_USIMSJS1_FILE_EF_MLNGC:
	# Default parameters, see also sysmousim-manual.pdf,
	# cap. 8.6 "Milenage Configuration (Ci/Ri)
	C1 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
	C2 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01]
	C3 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02]
	C4 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04]
	C5 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08]
	R1 = 0x40
	R2 = 0x00
	R3 = 0x20
	R4 = 0x40
	R5 = 0x60

	def __init__(self, content = None):
		if content == None:
			return
		if len(content) != 85:
			return
		self.C1 = content[0:16]
		self.C2 = content[16:32]
		self.C3 = content[32:48]
		self.C4 = content[48:64]
		self.C5 = content[64:80]
		self.R1 = content[80]
		self.R2 = content[81]
		self.R3 = content[82]
		self.R4 = content[83]
		self.R5 = content[84]
		
	def __str__(self):
		dump = "   C1: " + hexdump(self.C1) + "\n"
		dump += "   C2: " + hexdump(self.C2) + "\n"
		dump += "   C3: " + hexdump(self.C3) + "\n"
		dump += "   C4: " + hexdump(self.C4) + "\n"
		dump += "   C5: " + hexdump(self.C5) + "\n"
		dump += "   R1: " + str(hex(self.R1)) + "\n"
		dump += "   R2: " + str(hex(self.R2)) + "\n"
		dump += "   R3: " + str(hex(self.R3)) + "\n"
		dump += "   R4: " + str(hex(self.R4)) + "\n"
		dump += "   R5: " + str(hex(self.R5))
		return dump


# Initalize card (select master file)
def sysmo_usim_init(sim):
	print " * Initalizing..."
	sim.select(GSM_SIM_MF)


# Authenticate as administrator
def sysmo_usim_admin_auth(sim, adm1):
	print " * Authenticating at card as adminstrator..."
	sim.verify_chv(adm1, SYSMO_USIMSJS1_ADM1)


# Show current athentication parameters
# (Which algorithim is used for which rat?)
def sysmo_usim_show_auth_params(sim, adm1):
	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)

	print " * Reading..."
	sim.select(SYSMO_USIMSJS1_DF_AUTH)
	sim.select(SYSMO_USIMSJS1_EF_AUTH)
	res = sim.read_binary(0x02)

	print " * Current algorithm setting:"
	print "   2G: " + str(hex(res.apdu[0]))
	print "   3G: " + str(hex(res.apdu[1]))


# Program new authentication parameters
def sysmo_usim_write_auth_params(sim, adm1, algo_2g, algo_3g):
	print " * New algorithm setting:"
	print "   2G: " + str(hex(algo_2g))
	print "   3G: " + str(hex(algo_3g))

	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)

	print " * Programming..."
	sim.select(SYSMO_USIMSJS1_DF_AUTH)
	sim.select(SYSMO_USIMSJS1_EF_AUTH)
	sim.update_binary([algo_2g,algo_3g])


# Show current milenage parameters
def sysmo_usim_show_milenage_params(sim, adm1):
	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)


# Show current milenage parameters
def sysmo_usim_show_milenage_params(sim, adm1):
	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)

	sim.select(SYSMO_USIMSJS1_DF_AUTH)
	sim.select(SYSMO_USIMSJS1_EF_MLNGC)

	print " * Reading..."
	ef_mlngc = SYSMO_USIMSJS1_FILE_EF_MLNGC()
	res = sim.read_binary(16, offset = 0)
	ef_mlngc.C1 = res.apdu
	res = sim.read_binary(16, offset = 16)
	ef_mlngc.C2 = res.apdu
	res = sim.read_binary(16, offset = 32)
	ef_mlngc.C3 = res.apdu
	res = sim.read_binary(16, offset = 48)
	ef_mlngc.C4 = res.apdu
	res = sim.read_binary(16, offset = 64)
	ef_mlngc.C5 = res.apdu
	res = sim.read_binary(1, offset = 80)
	ef_mlngc.R1 = res.apdu[0]
	res = sim.read_binary(1, offset = 81)
	ef_mlngc.R2 = res.apdu[0]
	res = sim.read_binary(1, offset = 82)
	ef_mlngc.R3 = res.apdu[0]
	res = sim.read_binary(1, offset = 83)
	ef_mlngc.R4 = res.apdu[0]
	res = sim.read_binary(1, offset = 84)
	ef_mlngc.R5 = res.apdu[0]

	print " * Current Milenage Parameters in (EF.MLNGC):"
	print str(ef_mlngc)


# Write new milenage parameters
def sysmo_usim_write_milenage_params(sim, adm1, ef_mlngc):
	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)

	print " * New Milenage Parameters for (EF.MLNGC):"
	print str(ef_mlngc)

	sim.select(SYSMO_USIMSJS1_DF_AUTH)
	sim.select(SYSMO_USIMSJS1_EF_MLNGC)

	print " * Programming..."
	sim.update_binary(ef_mlngc.C1, offset = 0)
	sim.update_binary(ef_mlngc.C2, offset = 16)
	sim.update_binary(ef_mlngc.C3, offset = 32)
	sim.update_binary(ef_mlngc.C4, offset = 48)
	sim.update_binary(ef_mlngc.C5, offset = 64)
	sim.update_binary([ef_mlngc.R1], offset = 80)
	sim.update_binary([ef_mlngc.R2], offset = 81)
	sim.update_binary([ef_mlngc.R3], offset = 82)
	sim.update_binary([ef_mlngc.R4], offset = 83)
	sim.update_binary([ef_mlngc.R5], offset = 84)


# Show current OPc value
def sysmo_usim_show_opc_params(sim, adm1):
	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)

	print " * Reading..."
	sim.select(GSM_SIM_DF_GSM)
	sim.select(SYSMO_USIMSJS1_EF_OPC)
	res = sim.read_binary(17)

	print " * Current OPc setting:"
	print "   OP: " + str(hex(res.apdu[0]))
	print "   OP/OPc: " + hexdump(res.apdu[1:])


# Program new OPc value
def sysmo_usim_write_opc_params(sim, adm1, select, op):
	print " * New OPc setting:"
	print "   OP: " + str(hex(select))
	print "   OP/OPc: " + hexdump(op)

	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)

	sim.select(GSM_SIM_DF_GSM)
	sim.select(SYSMO_USIMSJS1_EF_OPC)

	print " * Programming..."
	sim.update_binary([select] + op)


# Show the enable status of the USIM application (app is enabled or disabled?)
def sysmo_usim_show_usim_status(sim, adm1):
	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)

	print " * Reading..."
	sim.select(GSM_USIM_EF_DIR)
	res = sim.read_record(0x26, rec_no = 1)

	print " * Current status of Record No.1 in EF.DIR:"
	print "   " + hexdump(res.apdu)


# Show the enable status of the USIM application (app is enabled or disabled?)
def sysmo_usim_show_sim_mode(sim, adm1):
	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)

	print " * Reading..."
	sim.select(GSM_USIM_EF_DIR)
	res = sim.read_record(0x26, rec_no = 1)

	print " * Current status of Record No. 1 in EF.DIR:"
	print "   " + hexdump(res.apdu)

	if hexdump(SYSMO_USIM_AID) in hexdump(res.apdu):
		print "   ==> USIM application enabled"
	else:
		print "   ==> USIM application disabled"


# Show the enable status of the USIM application (app is enabled or disabled?)
def sysmo_usim_write_sim_mode(sim, adm1, usim_enabled = True):
	if usim_enabled:
		new_record = SYSMO_USIM_EF_DIR_REC_1_CONTENT
	else:
		new_record = [0xFF] * len(SYSMO_USIM_EF_DIR_REC_1_CONTENT)

	print " * New status of Record No.1 in EF.DIR:"
	print "   " + hexdump(new_record)
	if hexdump(SYSMO_USIM_AID) in hexdump(new_record):
		print "   ==> USIM application enabled"
	else:
		print "   ==> USIM application disabled"

	sysmo_usim_init(sim)
	sysmo_usim_admin_auth(sim, adm1)

	print " * Programming..."
	sim.select(GSM_USIM_EF_DIR)
	sim.update_record(new_record, rec_no = 1)


