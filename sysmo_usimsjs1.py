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


import sys
from card import *
from simcard import *
from utils import *

# Files (propritary)
SYSMO_USIMSJS1_EF_KI = [0x00, 0xFF]
SYSMO_USIMSJS1_EF_OPC = [0x00, 0xF7]
SYSMO_USIMSJS1_DF_AUTH = [0x7F, 0xCC] #FIXME: Manual does not mention name, just called it "DF_AUTH" might be wrong!
SYSMO_USIMSJS1_EF_AUTH = [0x6F, 0x00]
SYSMO_USIMSJS1_EF_MLNGC = [0x6F, 0x01]
SYSMO_USIMSJS1_EF_SQNC = [0x00, 0xFB] # ADF.USIM
SYSMO_USIMSJS1_EF_SQNA = [0x00, 0xFA] # ADF.USIM
SYSMO_USIMSJS1_EF_EFMLNG = [0x00, 0xFB] # ADF.USIM
SYSMO_USIMSJS1_EF_AC = [0x00, 0xFE] # ADF.USIM

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

class SYSMO_USIMSJS1_FILE_EF_SQNC:
	# Default parameters
	ind_size_bits = 5
	sqn_check_enabled = True
	sqn_age_limit_enabled = True
	sqn_max_delta_enabled = True
	sqnms_offset = 0
	max_delta = 0;
	age_limit = 2**28 << ind_size_bits

	def __init__(self, content = None):
		if content == None:
			return
		if len(content) != 15:
			raise ValueError("unexpected length of %u bytes", len(content))
		self.ind_size_bits = content[0] & 0xf
		self.sqn_check_enabled = bool(content[0] & 0x10)
		self.sqn_age_limit_enabled = bool(content[0] & 0x20)
		self.sqn_max_delta_enabled = bool(content[0] & 0x40)
		self.sqnms_offset = list_to_int(content[1:3])/6
		self.max_delta = list_to_int(content[3:9]) >> self.ind_size_bits
		self.age_limit = list_to_int(content[9:15]) >> self.ind_size_bits

	def __str__(self):
		pfx = "   "
		dump = ""

		dump += "%sIND (bits): %u\n" % (pfx, self.ind_size_bits)
		dump += "%sSQN Check enabled: %u\n" % (pfx, self.sqn_check_enabled)
		dump += "%sSQN Age Limit enabled: %u\n" % (pfx, self.sqn_age_limit_enabled)
		dump += "%sSQN Max Delta enabled: %u\n" % (pfx, self.sqn_max_delta_enabled)
		dump += "%sSQNms Offset (into SQN array): %u\n" % (pfx, self.sqnms_offset)
		dump += "%sMax Delta: %u\n" % (pfx, self.max_delta)
		dump += "%sAge Limit: %u\n" % (pfx, self.age_limit)
		return dump

class SYSMO_USIMSJS1_FILE_EF_SQNA:
	seq_array = []

	def __init__(self, content, ind = 5):
		if content == None:
			return
		if len(content) != 6*(2**ind):
			raise ValueError("unexpected length of %u bytes", len(content))
		# read in the SEQ array
		for i in range(0, 2**ind):
			offset = 6*i;
			self.seq_array.append(list_to_int(content[offset:offset+6]))

	def __str__(self):
		pfx = "   "
		dump = ""
		for i in range(len(self.seq_array)):
			dump += "%sSEQ[%03d]: %u\n" % (pfx, i, self.seq_array[i])
		return dump


# Initalize card (select master file)
def sysmo_usim_init(sim):
	print " * Initalizing..."
	sim.select(GSM_SIM_MF)


# Authenticate as administrator
def sysmo_usim_admin_auth(sim, adm1, force = False):
	rc = True
	rem_attemts = sim.chv_retrys(SYSMO_USIMSJS1_ADM1)

	print " * Remaining attempts: " + str(rem_attemts)

	# Stop if a decreased ADM1 retry counter is detected
	if(rem_attemts < 3) and force == False:
		print " * Error: Only two authentication attemts remaining, we don't"
		print "          want to risk another failed authentication attempt!"
		print "          (double check ADM1 and use option -f to override)"
		return False

	# Try to authenticate
	try:
		print " * Authenticating..."
		sim.verify_chv(adm1, SYSMO_USIMSJS1_ADM1)
		print " * Authentication successful"
	except:
		print " * Error: Authentication failed!"
		rc = False

	# Read back and display remaining attemts
	rem_attemts = sim.chv_retrys(SYSMO_USIMSJS1_ADM1)
	print " * Remaining attempts: " + str(rem_attemts)

	return rc

def sysmo_usim_algo_to_str(alg):
	if alg == 1:
	    return 'MILENAGE'
	elif alg == 3:
	    return 'COMP128v1'
	elif alg == 4:
	    return 'XOR-2G'
	elif alg == 5:
	    return 'GBA'
	elif alg == 6:
	    return 'COMP128v2'
	elif alg == 7:
	    return 'COMP128v3'
	elif alg == 8:
	    return 'XOR-3G'
	elif alg == 9:
	    return 'CIS-B'
	else:
	    return 'INVALID'

def sysmo_usim_str_to_algo(alg):
	if alg == 'MILENAGE' or alg == '1':
	    return 1
	elif alg == 'COMP128v1' or alg == '3':
	    return 3
	elif alg == 'XOR-2G' or alg == '4':
	    return 4
	elif alg == 'GBA' or alg == '5':
	    return 5
	elif alg == 'COMP128v2' or alg == '6':
	    return 6
	elif alg == 'COMP128v3' or alg == '7':
	    return 7
	elif alg == 'XOR-3G' or alg == '8':
	    return 8
	elif alg == 'CIS-B' or alg == '9':
	    return 9
	else:
	    raise ValueError('Unknown Algorithm %s', alg)

# Show current athentication parameters
# (Which algorithim is used for which rat?)
def sysmo_usim_show_auth_params(sim):
	sysmo_usim_init(sim)

	print " * Reading..."
	sim.select(SYSMO_USIMSJS1_DF_AUTH)
	sim.select(SYSMO_USIMSJS1_EF_AUTH)
	res = sim.read_binary(0x02)

	print " * Current algorithm setting:"
	print "   2G: " + sysmo_usim_algo_to_str(res.apdu[0])
	print "   3G: " + sysmo_usim_algo_to_str(res.apdu[1])


# Program new authentication parameters
def sysmo_usim_write_auth_params(sim, algo_2g_str, algo_3g_str):
	algo_2g = sysmo_usim_str_to_algo(algo_2g_str)
	algo_3g = sysmo_usim_str_to_algo(algo_3g_str)

	print " * New algorithm setting:"
	print "   2G: " + sysmo_usim_algo_to_str(algo_2g)
	print "   3G: " + sysmo_usim_algo_to_str(algo_3g)

	sysmo_usim_init(sim)

	print " * Programming..."
	sim.select(SYSMO_USIMSJS1_DF_AUTH)
	sim.select(SYSMO_USIMSJS1_EF_AUTH)
	sim.update_binary([algo_2g,algo_3g])

def sysmo_usim_get_auth_counter(sim):
	sim.select(SYSMO_USIMSJS1_EF_AC)
	res = sim.read_binary(4, offset=0)
	ctr = list_to_int(res.apdu[0:4])
	if ctr == 0:
		return "LOCKED"
	elif ctr == 0xFFFFFFFF:
		return "DISABLED"
        else:
		return ctr

def sysmo_usim_read_milenage_sqn_params(sim):
	sysmo_usim_init(sim)

	sim.card.SELECT_ADF_USIM()
	sim.select(SYSMO_USIMSJS1_EF_SQNC)

	res = sim.read_binary(15, offset = 0)
	ef_sqnc = SYSMO_USIMSJS1_FILE_EF_SQNC(res.apdu)
	print "* Current SQN Configuration: "
	print str(ef_sqnc)

	# SQN Array
	ind_pow = 2**ef_sqnc.ind_size_bits
	sim.select(SYSMO_USIMSJS1_EF_SQNA)
	res = sim.read_binary(ind_pow*6, offset=0)
	ef_sqna = SYSMO_USIMSJS1_FILE_EF_SQNA(res.apdu)
	print "* Current SQN Array: "
	print str(ef_sqna)

	auth_ctr = sysmo_usim_get_auth_counter(sim)
	print "* Authentication Counter: %s\n" % auth_ctr

# Show current milenage parameters
def sysmo_usim_show_milenage_params(sim):
	sysmo_usim_init(sim)

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
def sysmo_usim_write_milenage_params(sim, ef_mlngc):
	sysmo_usim_init(sim)

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


def sysmo_usim_opcmode2str(mode):
	if mode == 1:
		return 'OPc'
	elif mode == 0:
		return 'OP'
	else:
		raise ValueError('Unknown Mode ', mode)


# Show current OPc value
def sysmo_usim_show_opc_params(sim):
	sysmo_usim_init(sim)

	print " * Reading..."
	sim.card.SELECT_ADF_USIM()
	sim.select(SYSMO_USIMSJS1_EF_OPC)
	res = sim.read_binary(17)

	mode_str = sysmo_usim_opcmode2str(res.apdu[0])

	print " * Current OP/OPc setting:"
	print "   %s: %s" % (mode_str, hexdump(res.apdu[1:]))


# Program new OPc value
def sysmo_usim_write_opc_params(sim, select, op):
	print " * New OPc setting:"
	print "   %s: %s" % (sysmo_usim_opcmode2str(select), hexdump(op))
	print "   OP/OPc: " + hexdump(op)

	sysmo_usim_init(sim)

	sim.select(GSM_SIM_DF_GSM)
	sim.select(SYSMO_USIMSJS1_EF_OPC)

	print " * Programming..."
	sim.update_binary([select] + op)


# Show current KI value
def sysmo_usim_show_ki_params(sim):
	sysmo_usim_init(sim)

	print " * Reading..."
	sim.select(GSM_SIM_DF_GSM)
	sim.select(SYSMO_USIMSJS1_EF_KI)
	res = sim.read_binary(16)

	print " * Current KI setting:"
	print "   KI: " + hexdump(res.apdu)


# Program new KI value
def sysmo_usim_write_ki_params(sim, ki):
	print " * New KI setting:"
	print "   KI: " + hexdump(ki)

	sysmo_usim_init(sim)

	sim.select(GSM_SIM_DF_GSM)
	sim.select(SYSMO_USIMSJS1_EF_KI)

	print " * Programming..."
	sim.update_binary(ki)


# Show the enable status of the USIM application (app is enabled or disabled?)
def sysmo_usim_show_usim_status(sim):
	sysmo_usim_init(sim)

	print " * Reading..."
	sim.select(GSM_USIM_EF_DIR)
	res = sim.read_record(0x26, rec_no = 1)

	print " * Current status of Record No.1 in EF.DIR:"
	print "   " + hexdump(res.apdu)


# Show the enable status of the USIM application (app is enabled or disabled?)
def sysmo_usim_show_sim_mode(sim):
	sysmo_usim_init(sim)

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
def sysmo_usim_write_sim_mode(sim, usim_enabled = True):
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

	print " * Programming..."
	sim.select(GSM_USIM_EF_DIR)
	sim.update_record(new_record, rec_no = 1)


# Show current ICCID value
def sysmo_usim_show_iccid(sim):
	sysmo_usim_init(sim)

	print " * Reading..."
	sim.select(GSM_SIM_EF_ICCID)
	res = sim.read_binary(10)

	print " * Current ICCID setting:"
	print "   ICCID: " + hexdump(swap_nibbles(res.apdu))


# Program new ICCID value
def sysmo_usim_write_iccid(sim, iccid):
	print " * New ICCID setting:"
	print "   ICCID: " + hexdump(iccid)

	sysmo_usim_init(sim)

	sim.select(GSM_SIM_EF_ICCID)

	print " * Programming..."
	sim.update_binary(swap_nibbles(iccid))
