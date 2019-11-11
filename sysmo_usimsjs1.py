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
#      |
#      +--[EF_IMSI 0x6F07]

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

	def encode(self):
		out = self.C1 + self.C2 + self.C3 + self.C4 + self.C5
		out += [self.R1, self.R2, self.R3, self.R4, self.R5]
		return out


class SYSMO_USIMSJS1_FILE_EF_SQNC:
	# Default parameters
	ind_size_bits = 5
	sqn_check_enabled = True
	sqn_age_limit_enabled = False
	sqn_max_delta_enabled = True
	sqnms_offset = 0
	max_delta = 2**28 << ind_size_bits
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

	def encode(self):
		out = list(range(0, 3))
		out[0] = self.ind_size_bits & 0x0f
		if self.sqn_check_enabled:
			out[0] |= 0x10
		if self.sqn_age_limit_enabled:
			out[0] |= 0x20
		if self.sqn_max_delta_enabled:
			out[0] |= 0x40
		out[1] = (self.sqnms_offset*6) & 0xff
		out[2] = (self.sqnms_offset*6) >> 8
		out += int_to_list(self.max_delta, 6)
		out += int_to_list(self.age_limit, 6)
		return out

class SYSMO_USIMSJS1_FILE_EF_SQNA:
	seq_array = []

	def __init__(self, content, ind = 5):
		if content == None:
			for i in range(0, 2**ind):
				self.seq_array.append(0)
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

	def encode(self):
		out = []
		for i in self.seq_array:
			out += int_to_list(i, 6)
		return out

sysmo_usim_algorithms = (
		(1, 'MILENAGE'),
		(3, 'COMP128v1'),
		(4, 'XOR-2G'),
		(5, 'GBA'),
		(6, 'COMP128v2'),
		(7, 'COMP128v3'),
		(8, 'XOR-3G'),
		(9, 'CIS-B'),
	)

sysmo_usim_opcmodes = (
		(0, 'OP'),
		(1, 'OPc'),
	)

class Sysmo_usimsjs1:

	sim = None

	def __init__(self):
		print("Initializing smartcard terminal...")
		self.sim = Simcard(GSM_USIM, toBytes("3B 9F 96 80 1F C7 80 31 A0 73 BE 21 13 67 43 20 07 18 00 00 01 A5"))
		print(" * Detected Card ICCID: %s" % self.sim.card.get_ICCID())
		self.sim.card.SELECT_ADF_USIM()
		print(" * Detected Card IMSI:  %s" % self.sim.card.get_imsi())
		print("")


	def __warn_failed_auth(self, attempts = 3, keytype = "ADM1"):
		print("   ===  Authentication problem! The Card will permanently   ===")
		print("   === lock down after %d failed attemts! Double check %s! ===" % (attempts, keytype))
		print("")


	# Authenticate as administrator
	def admin_auth(self, adm1, force = False):
		print("Authenticating...")
		rc = True
		rem_attemts = self.sim.chv_retrys(SYSMO_USIMSJS1_ADM1)

		print(" * Remaining attempts: " + str(rem_attemts))

		# Stop if a decreased ADM1 retry counter is detected
		if(rem_attemts < 3) and force == False:
			print(" * Error: Only two authentication attempts remaining, we don't")
			print("          want to risk another failed authentication attempt!")
			print("          (double check ADM1 and use option -f to override)")
			print("")
			self.__warn_failed_auth()
			return False

		if(len(adm1) != 8):
			print(" * Error: Short ADM1, a valid ADM1 is 8 digits long!")
			print("")
			self.__warn_failed_auth()
			return False

		# Try to authenticate
		try:
			print(" * Authenticating...")
			self.sim.verify_chv(adm1, SYSMO_USIMSJS1_ADM1)
			print(" * Authentication successful")
		except:
			print(" * Error: Authentication failed!")
			self.__warn_failed_auth()
			rc = False

		# Read back and display remaining attemts
		rem_attemts = self.sim.chv_retrys(SYSMO_USIMSJS1_ADM1)
		print(" * Remaining attempts: " + str(rem_attemts))
		print("")

		if rc == False:
			self.__warn_failed_auth()
		return rc


	# Initalize card (select master file)
	def __init(self):
		print " * Initalizing..."
		self.sim.select(GSM_SIM_MF)


	# Show the enable status of the USIM application (app is enabled or disabled?)
	def show_sim_mode(self):
		print("Reading SIM-Mode...")
		self.__init()

		print(" * Reading...")
		self.sim.select(GSM_USIM_EF_DIR)
		res = self.sim.read_record(0x26, rec_no = 1)

		print(" * Current status of Record No. 1 in EF.DIR:")
		print("   " + hexdump(res.apdu))

		if hexdump(SYSMO_USIM_AID) in hexdump(res.apdu):
			print("   ==> USIM application enabled")
		else:
			print("   ==> USIM application disabled")
		print("")


	# Show the enable status of the USIM application (app is enabled or disabled?)
	def write_sim_mode(self, usim_enabled = True):
		print("Programming SIM-Mode...")
		self.__init()

		if usim_enabled:
			new_record = SYSMO_USIM_EF_DIR_REC_1_CONTENT
		else:
			new_record = [0xFF] * len(SYSMO_USIM_EF_DIR_REC_1_CONTENT)

		print(" * New status of Record No.1 in EF.DIR:")
		print("   " + hexdump(new_record))
		if hexdump(SYSMO_USIM_AID) in hexdump(new_record):
			print("   ==> USIM application enabled")
		else:
			print("   ==> USIM application disabled")

		print(" * Programming...")
		self.sim.select(GSM_USIM_EF_DIR)
		self.sim.update_record(new_record, rec_no = 1)
		print("")


	# Show current athentication parameters
	# (Which algorithim is used for which rat?)
	def show_auth_params(self):
		print("Programming Authentication parameters...")
		self.__init()

		print(" * Reading...")
		self.sim.select(SYSMO_USIMSJS1_DF_AUTH)
		self.sim.select(SYSMO_USIMSJS1_EF_AUTH)
		res = self.sim.read_binary(0x02)

		algo_2g, algo_3g = res.apdu[:2]

		print(" * Current algorithm setting:")
		print("   2G: %d=%s" % (algo_2g, id_to_str(sysmo_usim_algorithms, algo_2g)))
		print("   3G: %d=%s" % (algo_3g, id_to_str(sysmo_usim_algorithms, algo_3g)))
		print("")


	# Program new authentication parameters
	def write_auth_params(self, algo_2g_str, algo_3g_str):
		print("Reading Authentication parameters...")
		self.__init()

		if algo_2g_str.isdigit():
			algo_2g = int(algo_2g_str)
		else:
			algo_2g = str_to_id(sysmo_usim_algorithms, algo_2g_str)

		if algo_3g_str.isdigit():
			algo_3g = int(algo_3g_str)
		else:
			algo_3g = str_to_id(sysmo_usim_algorithms, algo_3g_str)

		print(" * New algorithm setting:")
		print("   2G: %d=%s" % (algo_2g, id_to_str(sysmo_usim_algorithms, algo_2g)))
		print("   3G: %d=%s" % (algo_3g, id_to_str(sysmo_usim_algorithms, algo_3g)))

		print(" * Programming...")
		self.sim.select(SYSMO_USIMSJS1_DF_AUTH)
		self.sim.select(SYSMO_USIMSJS1_EF_AUTH)
		self.sim.update_binary([algo_2g,algo_3g])
		print("")


	# Show current milenage parameters
	def show_milenage_params(self):
		print("Reading Milenage parameters...")
		self.__init()

		self.sim.select(SYSMO_USIMSJS1_DF_AUTH)
		self.sim.select(SYSMO_USIMSJS1_EF_MLNGC)

		print(" * Reading...")
		res = self.sim.read_binary(85)
		ef_mlngc = SYSMO_USIMSJS1_FILE_EF_MLNGC(res.apdu)

		print(" * Current Milenage Parameters in (EF.MLNGC):")
		print str(ef_mlngc)
		print("")


	# Write new milenage parameters
	def write_milenage_params(self, ef_mlngc):
		print("Programming Milenage parameters...")
		self.__init()

		print(" * New Milenage Parameters for (EF.MLNGC):")
		print str(ef_mlngc)

		self.sim.select(SYSMO_USIMSJS1_DF_AUTH)
		self.sim.select(SYSMO_USIMSJS1_EF_MLNGC)

		print(" * Programming...")
		self.sim.update_binary(ef_mlngc.encode())
		print("")


	def __get_auth_counter(self):
		self.sim.select(SYSMO_USIMSJS1_EF_AC)
		res = self.sim.read_binary(4, offset=0)
		ctr = list_to_int(res.apdu[0:4])
		if ctr == 0:
			return "LOCKED"
		elif ctr == 0xFFFFFFFF:
			return "DISABLED"
		else:
			return ctr


	def __set_auth_counter(self, ctr):
		if ctr == "LOCKED":
			ctr = 0
		elif ctr == "DISABLED":
			ctr = 0xFFFFFFFF
		data = int_to_list(ctr, 4)
		self.sim.select(SYSMO_USIMSJS1_EF_AC)
		res = self.sim.update_binary(data, offset=0)
		if ctr == 0:
			return "LOCKED"
		elif ctr == 0xFFFFFFFF:
			return "DISABLED"
		else:
			return ctr


	# Show current milenage SQN parameters
	def show_milenage_sqn_params(self):
		print("Reading Milenage Sequence parameters...")
		self.__init()

		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_USIMSJS1_EF_SQNC)

		res = self.sim.read_binary(15, offset = 0)
		ef_sqnc = SYSMO_USIMSJS1_FILE_EF_SQNC(res.apdu)
		print(" * Current SQN Configuration:")
		print str(ef_sqnc)

		# SQN Array
		ind_pow = 2**ef_sqnc.ind_size_bits
		self.sim.select(SYSMO_USIMSJS1_EF_SQNA)
		res = self.sim.read_binary(ind_pow*6, offset=0)
		ef_sqna = SYSMO_USIMSJS1_FILE_EF_SQNA(res.apdu)
		print(" * Current SQN Array:")
		print str(ef_sqna)

		auth_ctr = self.__get_auth_counter()
		print("* Authentication Counter: %s" % auth_ctr)
		print("")


	# Reset milenage SQN configuration
	def reset_milenage_sqn_params(self):
		print(" * Resetting SQN Configuration to defaults...")
		self.__init()

		print(" * Resetting...")
		self.sim.card.SELECT_ADF_USIM()
		ef_sqnc = SYSMO_USIMSJS1_FILE_EF_SQNC(None)
		self.sim.select(SYSMO_USIMSJS1_EF_SQNC)
		res = self.sim.update_binary(ef_sqnc.encode())

		ef_sqna = SYSMO_USIMSJS1_FILE_EF_SQNA(None, ef_sqnc.ind_size_bits)
		self.sim.select(SYSMO_USIMSJS1_EF_SQNA)
		res = self.sim.update_binary(ef_sqna.encode())

		self.__set_auth_counter("DISABLED")
		print("")		


	# Show current OPc value
	def show_opc_params(self):
		print("Reading OP/c value...")
		self.__init()

		print(" * Reading...")
		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_USIMSJS1_EF_OPC)
		res = self.sim.read_binary(17)

		mode_str = id_to_str(sysmo_usim_opcmodes, res.apdu[0])

		print(" * Current OP/OPc setting:")
		print("   %s: %s" % (mode_str, hexdump(res.apdu[1:])))
		print("")


	# Program new OPc value
	def write_opc_params(self, select, op):
		if op:
			print("Writing OP value...")
		else:
			print("Writing OPc value...")
		self.__init()

		print(" * New OPc setting:")
		print("   %s: %s" % (id_to_str(sysmo_usim_opcmodes, select), hexdump(op)))

		self.sim.select(GSM_SIM_DF_GSM)
		self.sim.select(SYSMO_USIMSJS1_EF_OPC)

		print(" * Programming...")
		self.sim.update_binary([select] + op)
		print("")


	# Show current KI value
	def show_ki_params(self):
		print("Reading KI value...")
		print(" * Reading...")
		self.sim.select(GSM_SIM_DF_GSM)
		self.sim.select(SYSMO_USIMSJS1_EF_KI)
		res = self.sim.read_binary(16)

		print(" * Current KI setting:")
		print("   KI: " + hexdump(res.apdu))
		print("")


	# Program new KI value
	def write_ki_params(self, ki):
		print("Writing KI value...")
		self.__init()

		print(" * New KI setting:")
		print("   KI: " + hexdump(ki))

		self.sim.select(GSM_SIM_DF_GSM)
		self.sim.select(SYSMO_USIMSJS1_EF_KI)

		print(" * Programming...")
		self.sim.update_binary(ki)
		print("")


	# Program new ICCID value
	def write_iccid(self, iccid):
		print("Writing ICCID value...")
		self.__init()

		print(" * New ICCID setting:")
		print("   ICCID: " + hexdump(iccid))

		self.sim.select(GSM_SIM_EF_ICCID)

		print(" * Programming...")
		self.sim.update_binary(swap_nibbles(iccid))
		print("")


	# Program new IMSI value
	def write_imsi(self, imsi):
		print("Writing IMSI value...")
		self.__init()

		print(" * New ISMI setting:")
		print("   IMSI: " + hexdump(imsi))

		self.sim.select(GSM_SIM_DF_GSM)
		self.sim.select(GSM_SIM_EF_IMSI)

		imsi = [len(imsi)] + swap_nibbles(imsi)

		print(" * Programming...")
		self.sim.update_binary(imsi)
		print("")


	# Show current KI value
	def show_mnclen(self):
		print("Reading MNCLEN value...")
		self.__init()

		print(" * Reading...")
		self.sim.select(GSM_SIM_DF_GSM)
		self.sim.select(GSM_SIM_EF_AD)
		res = self.sim.read_binary(4)

		print(" * Current MNCLEN setting:")
		print("   MNCLEN: " + "0x%02x" % res.apdu[3])
		print("")


	# Program new MNCLEN value
	def write_mnclen(self, mnclen):
		print("Writing MNCLEN value...")
		self.__init()

		print(" * New MNCLEN setting:")
		print("   MNCLEN: " + "0x" + hexdump(mnclen))

		if len(mnclen) != 1:
			print(" * Error: mnclen value must consist of a single byte!")
			return

		self.sim.select(GSM_SIM_DF_GSM)
		self.sim.select(GSM_SIM_EF_AD)

		res = self.sim.read_binary(4)
		new_ad = res.apdu[0:3] + mnclen

		print(" * Programming...")
		self.sim.update_binary(new_ad)
		print("")
