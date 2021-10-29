#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gadgets to modify SYSMO USIM SJA2 parameters

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

import sys
from utils import *
from sysmo_usim import *
import math

# Partial File tree:
# The following tree is incomplete, it just contains the propritary files we
# need to perform the tasks implemented below:
#
# [MF 0x3F00]
#  |
#  +--[DF_SYSTEM 0xA515]
#  |   |
#  |   +--[EF_SIM_AUTH_KEY 0x6F20] (regular file)
#  |
#  +--[ADF_USIM]
#  |   |
#  |   +--[USIM_AUTH_KEY 0xAF20] (regular file)
#  |   |
#  |   +--[EF_USIM_AUTH_KEY_2G 0xAF22] (link to DF_SYSTEM/EF_SIM_AUTH_KEY)
#  |
#  +--[ADF_ISIM]
#      |
#      +--[USIM_AUTH_KEY 0xAF20] (regular file)
#      |
#      +--[EF_USIM_AUTH_KEY_2G 0xAF22] (link to DF_SYSTEM/EF_SIM_AUTH_KEY)
#
# Note: EF_MILENAGE_CFG and EF_USIM_SQN not yet listed here.

# Propritary files
SYSMO_ISIMSJA2_DF_SYSTEM = [0xA5, 0x15]
SYSMO_ISIMSJA2_EF_SIM_AUTH_KEY = [0x6F, 0x20] # DF_SYSTEM
SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY = [0xAF, 0x20] # ADF.USIM
SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY_2G = [0xAF, 0x22] # ADF.USIM
SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY_GBA = [0xAF, 0x23] # ADF.USIM
SYSMO_ISIMSJA2_EF_MILENAGE_CFG = [0xAF, 0x21] # ADF.USIM
SYSMO_ISIMSJA2_EF_USIM_SQN = [0xAF, 0x30] # ADF.USIM
SYSMO_ISIMSJA2_EF_GBA_SK = [0xAF, 0x31] # ADF.USIM
SYSMO_ISIMSJA2_EF_GBA_REC_LIST = [0xAF, 0x32] # ADF.USIM
SYSMO_ISIMSJA2_EF_GBA_INT_KEY = [0xAF, 0x32] # ADF.USIM

# Authentication algorithms
SYSMO_ISIMSJA2_ALGO_COMP12V1 = 0x01
SYSMO_ISIMSJA2_ALGO_COMP12V2 = 0x02
SYSMO_ISIMSJA2_ALGO_COMP12V3 = 0x03
SYSMO_ISIMSJA2_ALGO_MILENAGE = 0x04
SYSMO_ISIMSJA2_ALGO_SHA1AKA = 0x05
SYSMO_ISIMSJA2_ALGO_XOR = 0x0F

sysmo_isimsja2_algorithms = (
	(SYSMO_ISIMSJA2_ALGO_COMP12V1, 'COMP128v1'),
	(SYSMO_ISIMSJA2_ALGO_COMP12V2, 'COMP128v2'),
	(SYSMO_ISIMSJA2_ALGO_COMP12V3, 'XOR-2G'),
	(SYSMO_ISIMSJA2_ALGO_MILENAGE, 'MILENAGE'),
	(SYSMO_ISIMSJA2_ALGO_SHA1AKA , 'SHA1-AKA'),
	(SYSMO_ISIMSJA2_ALGO_XOR, 'XOR'),
)

class SYSMO_ISIMSJA2_FILE_EF_XSIM_AUTH_KEY:
	"""
	Superclass model that generates that handles the header byte of
	SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY, SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY_2G
	and SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY_GBA.
	"""

	algo = SYSMO_ISIMSJA2_ALGO_COMP12V1
	use_opc = False
	sres_dev_func = 1

	def __init__(self, content = None):
		if content == None:
			return

		header = content[0]
		self.algo = header & 0x0F
		self.use_opc = bool((header >> 4) & 1)

		if (header >> 5) & 1:
			self.sres_dev_func = 2
		else:
			self.sres_dev_func = 1


	def __str__(self):
		dump = ""
		pfx = "   "

		dump += pfx + "Algorithm: "
		dump += id_to_str(sysmo_isimsja2_algorithms, self.algo)
		dump += "\n"

		if self.use_opc == True:
			dump += pfx + "Milenage: use OPc\n"
		else:
			dump += pfx + "Milenage: use OP\n"

		dump += pfx + "Milenage: use SRES deviation function " + str(self.sres_dev_func) + "\n"

		return dump


	def encode(self):
		out = [0x00]
		out[0] = self.algo & 0x0F
		if self.use_opc == True:
			out[0] |= 1 << 4
		out[0] |= ((self.sres_dev_func-1) & 1) << 5
		return out


class SYSMO_ISIMSJA2_FILE_EF_SIM_AUTH_KEY(SYSMO_ISIMSJA2_FILE_EF_XSIM_AUTH_KEY):

	key = [0xAA] * 16
	opc = [0xBB] * 16

	def __init__(self, content = None):
		if content == None:
			return

		SYSMO_ISIMSJA2_FILE_EF_XSIM_AUTH_KEY.__init__(self, content)
		self.key = content[1:17]
		self.opc = content[17:33]


	def __str__(self):
		dump = ""
		pfx = "   "

		dump += SYSMO_ISIMSJA2_FILE_EF_XSIM_AUTH_KEY.__str__(self)

		if self.algo == SYSMO_ISIMSJA2_ALGO_MILENAGE:
			dump += pfx + "Key: " + hexdump(self.key) + "\n"
			dump += pfx + "OPc: " + hexdump(self.opc)
		elif self.algo == SYSMO_ISIMSJA2_ALGO_XOR:
			dump += pfx + "Key: " + hexdump(self.key) + "\n"
			dump += pfx + "OPc: " + hexdump(self.opc)
		elif self.algo == SYSMO_ISIMSJA2_ALGO_SHA1AKA:
			dump += pfx + "Root key: " + hexdump(self.key) + "\n"
			dump += pfx + "OPc: " + hexdump(self.opc) + " (unused)"
		else:
			dump += pfx + "Key: " + hexdump(self.key) + "\n"
			dump += pfx + "OPc: " + hexdump(self.opc) + " (unused)"

		return dump


	def encode(self):
		out = SYSMO_ISIMSJA2_FILE_EF_XSIM_AUTH_KEY.encode(self)
		out += self.key + self.opc
		return out


class SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(SYSMO_ISIMSJA2_FILE_EF_XSIM_AUTH_KEY):

	full_res = True # Return full 8-byte RES or first 4 bytes only
	ext_res = False # Return 16 byte RES (ignores full_res, only valid with 3G XOR)

	key = [0x00] * 16
	opc = [0x00] * 16 # Only for Milenage

	def __init__(self, content = None):
		if content == None:
			return

		SYSMO_ISIMSJA2_FILE_EF_XSIM_AUTH_KEY.__init__(self, content)
		header = content[0]

		self.full_res = bool((header >> 6) & 1)
		self.ext_res = bool((header >> 7) & 1)

		self.key = content[1:17]
		if len(content) > 17:
			self.opc = content[17:33]


	def __str__(self):
		dump = ""
		pfx = "   "

		dump += SYSMO_ISIMSJA2_FILE_EF_XSIM_AUTH_KEY.__str__(self)
		if self.full_res == True and self.ext_res == False:
			dump += pfx + "3G: Return full 8-byte RES\n"
		elif self.full_res == False and self.ext_res == False:
			dump += pfx + "3G: Return first four bytes of RES\n"
		elif self.ext_res == True:
			dump += pfx + "3G: Return 16-byte RES (XOR 3G only)\n"
		else:
			dump += pfx + "(invalid RES length setting)"

		if self.algo != SYSMO_ISIMSJA2_ALGO_XOR and self.ext_res:
			dump += pfx + "Warning: 16-byte RES is only valid with XOR 3G!\n"

		if self.algo == SYSMO_ISIMSJA2_ALGO_MILENAGE:
			dump += pfx + "Key: " + hexdump(self.key) + "\n"
			dump += pfx + "OPc: " + hexdump(self.opc)
		elif self.algo == SYSMO_ISIMSJA2_ALGO_XOR:
			dump += pfx + "Key: " + hexdump(self.key) + "\n"
			dump += pfx + "OPc: " + hexdump(self.opc)
		elif self.algo == SYSMO_ISIMSJA2_ALGO_SHA1AKA:
			dump += pfx + "Root key: " + hexdump(self.key) + "\n"
			dump += pfx + "OPc: " + hexdump(self.opc) + " (unused)"
		else:
			dump += pfx + "Key: " + hexdump(self.key) + "\n"
			dump += pfx + "OPc: " + hexdump(self.opc) + " (unused)"
		return dump


	def encode(self):
		out = SYSMO_ISIMSJA2_FILE_EF_XSIM_AUTH_KEY.encode(self)
		if self.full_res == True:
			out[0] |= 1 << 6
		if self.ext_res == True:
			out[0] |= 1 << 7
		out += self.key

		# Note: Normally an OPc is only used with milenage, but lets
		# write the value anyway, even if it is not used.
		out += self.opc
		return out


# EF_USIM_AUTH_KEY_2G and EF_USIM_AUTH_KEY_GBA have the same layout as
# EF_USIM_AUTH_KEY, so there is nothing to specialize other than the class name
class SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G(SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY):
	pass


class SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_GBA(SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY):
	pass


class SYSMO_ISIMSJA2_FILE_EF_MILENAGE_CFG:
	R1 = 0x40
	R2 = 0x00
	R3 = 0x20
	R4 = 0x40
	R5 = 0x60
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


	def __init__(self, content = None):
		if content == None:
			return
		if len(content) != 85:
			return
		self.R1 = content[0]
		self.R2 = content[1]
		self.R3 = content[2]
		self.R4 = content[3]
		self.R5 = content[4]
		self.C1 = content[5:5+16]
		self.C2 = content[21:37]
		self.C3 = content[37:53]
		self.C4 = content[53:69]
		self.C5 = content[69:85]


	def __str__(self):
		dump = "   R1: " + str(hex(self.R1)) + "\n"
		dump += "   R2: " + str(hex(self.R2)) + "\n"
		dump += "   R3: " + str(hex(self.R3)) + "\n"
		dump += "   R4: " + str(hex(self.R4)) + "\n"
		dump += "   R5: " + str(hex(self.R5)) + "\n"
		dump += "   C1: " + hexdump(self.C1) + "\n"
		dump += "   C2: " + hexdump(self.C2) + "\n"
		dump += "   C3: " + hexdump(self.C3) + "\n"
		dump += "   C4: " + hexdump(self.C4) + "\n"
		dump += "   C5: " + hexdump(self.C5)
		return dump


	def encode(self):
		out = [self.R1, self.R2, self.R3, self.R4, self.R5]
		out += self.C1 + self.C2 + self.C3 + self.C4 + self.C5
		return out


class SYSMO_ISIMSJA2_FILE_EF_USIM_SQN:

	# Flag1:
	ind_size_bits = 5 # speficy file length by 2^ind_len
	sqn_check_enabled = True # perform SQN checks below
	sqn_age_limit_enabled = False # perform age limit check: (SQNms-SQN) <= AGE_LIMIT)
	sqn_max_delta_enabled = True # perform delta max check: (SWN-SQNms) <= DELTA MAX)
	sqn_check_skip_first = True # accept any SQN on the first authentication

	# Flag2:
	conceal_autn = True # Conceal the value of AUTN
	conceal_auts = True # Conceal the value of AUTS
	no_amf_clear = False # Do not clear AMF when computing MAC-S

	# Data:
	max_delta = 2**28 << ind_size_bits
	age_limit = 2**28 << ind_size_bits
	freshness_data = [0x00] * (6*2**ind_size_bits) # initalize to zero

	def __init__(self, content = None):
		if content == None:
			return

		# Check if we have at least the header
		if len(content) <= 2:
			raise ValueError("unexpected length of %u bytes", len(content))

		flag1 = content[0]
		self.ind_size_bits = flag1 & 0xf

		# The parameter ind_size_bits is not user configurable,
		# its a fixed configuration that is specific to the
		# card profile and it can be determined by looking at the
		# file length (length of the freshness data). If we find
		# an ind_size_bits that is intconstant to the file length,
		# we automatically set the value to the correct length
		ind_size_bits_calculated = int(math.log((len(content) - 14) / 6, 2))
		if ind_size_bits_calculated != self.ind_size_bits:
			print("   Warning: SQN Parameter ind_size_bits is set to " + str(self.ind_size_bits) + ", resetting it to " + str(ind_size_bits_calculated) + "!")
			self.ind_size_bits = ind_size_bits_calculated

		self.reset() #ensure freshness data is correctly reset
		self.sqn_check_enabled = bool((flag1 >> 4) & 1)
		self.sqn_age_limit_enabled = bool((flag1 >> 5) & 1)
		self.sqn_max_delta_enabled = bool((flag1 >> 6) & 1)
		self.sqn_check_skip_first = bool((flag1 >> 7) & 1)

		flag2 = content[1]
		self.conceal_autn = bool(flag2 & 1)
		self.conceal_auts = bool((flag2 >> 1) & 1)
		self.no_amf_clear = bool((flag2 >> 2) & 1)

		# Check if the data body is complete
		if len(content) < 14+(6*2**self.ind_size_bits):
			raise ValueError("unexpected length of %u bytes" % len(content))

		self.max_delta = list_to_int(content[2:8])
		self.age_limit = list_to_int(content[8:14])
		self.freshness_data = content[15:(6*2**self.ind_size_bits)]


	def __str__(self):
		pfx = "   "
		dump = ""

		dump += "%sIND (bits): %u\n" % (pfx, self.ind_size_bits)
		if self.sqn_check_enabled:
			dump += "%sSQN Check enabled\n" % pfx
		else:
			dump += "%sSQN Check disabled\n" % pfx
		if self.sqn_age_limit_enabled:
			dump += "%sSQN Age Limit enabled\n" % pfx
		else:
			dump += "%sSQN Age Limit disabled\n" % pfx
		if self.sqn_max_delta_enabled:
			dump += "%sSQN Max Delta enabled\n" % pfx
		else:
			dump += "%sSQN Max Delta disabled\n" % pfx
		if self.sqn_check_skip_first:
			dump += "%sSQN Skip first enabled\n" % pfx
		else:
			dump += "%sSQN Skip first disabled\n" % pfx
		if self.conceal_autn:
			dump += "%sSQN Conceal AUTN enabled\n" % pfx
		else:
			dump += "%sSQN Conceal AUTN disabled\n" % pfx
		if self.conceal_auts:
			dump += "%sSQN Conceal AUTS enabled\n" % pfx
		else:
			dump += "%sSQN Conceal AUTS disabled\n" % pfx
		if self.no_amf_clear:
			dump += "%sSQN No AMF clear enabled\n" % pfx
		else:
			dump += "%sSQN No AMF clear disabled\n" % pfx
		dump += "%sMax Delta: %u\n" % (pfx, self.max_delta)
		dump += "%sAge Limit: %u\n" % (pfx, self.age_limit)
		dump += pfx + "Freshness Data:\n" + hexdump(self.freshness_data, True)

		return dump


	def encode(self):
		out = [0x00, 0x00]

		# Flag1:
		out[0] = self.ind_size_bits & 0x0f
		if self.sqn_check_enabled:
			out[0] |= 1 << 4
		if self.sqn_age_limit_enabled:
			out[0] |= 1 << 5
		if self.sqn_max_delta_enabled:
			out[0] |= 1 << 6
		if self.sqn_check_skip_first:
			out[0] |= 1 << 7

		# Flag2:
		if self.conceal_autn:
			out[1] |= 1 << 0
		if self.conceal_auts:
			out[1] |= 1 << 1
		if self.no_amf_clear:
			out[1] |= 1 << 2

		# Data:
		out += int_to_list(self.max_delta, 6)
		out += int_to_list(self.age_limit, 6)
		out += self.freshness_data
		return out


	def reset(self):
		self.freshness_data = [0x00] * (6*2**self.ind_size_bits)



class Sysmo_isim_sja2(Sysmo_usim):

	def __init__(self):
		card_detected = False

		# Try card model #1
		try:
			atr = "3B 9F 96 80 1F 87 80 31 E0 73 FE 21 1B 67 4A 4C 75 30 34 05 4B A9"
			print("Trying to find card with ATR: " + atr)
			Sysmo_usim.__init__(self, atr)
			card_detected = True
		except:
			print(" * Card not detected!")

		if card_detected == True:
			return


		# Try card model #2
		try:
			atr = "3B 9F 96 80 1F 87 80 31 E0 73 FE 21 1B 67 4A 4C 75 31 33 02 51 B2"
			print("Trying to find card with ATR: " + atr)
			Sysmo_usim.__init__(self, atr)
			card_detected = True
		except:
			print(" * Card not detected!")

		if card_detected == True:
			return

		# Try card model #3 (sysmoTSIM)
		try:
			atr = "3B 9F 96 80 1F 87 80 31 E0 73 FE 21 1B 67 4A 4C 52 75 31 04 51 D5"
			print("Trying to find card with ATR: " + atr)
			Sysmo_usim.__init__(self, atr)
			card_detected = True
		except:
			print(" * Card not detected!")

		if card_detected == True:
			return


		# Exit when we are not able to detect the card
		if card_detected != True:
			sys.exit(1)


	# Show current milenage parameters
	def show_milenage_params(self):
		print("Reading Milenage parameters...")
		self._init()

		print(" * Reading...")
		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_ISIMSJA2_EF_MILENAGE_CFG)
		res = self._read_binary(85)
		ef = SYSMO_ISIMSJA2_FILE_EF_MILENAGE_CFG(res.apdu)

		print(" * Current Milenage Parameters:")
		print(str(ef))
		print("")


	# Write new milenage parameters
	def write_milenage_params(self, params):

		print("Programming Milenage parameters...")

		if (len(params) < 85):
			print("Error: Short milenage parameters!")
			return
		params_swapped = params[80:85] + params[0:80]

		self._init()

		print(" * New Milenage Parameters for (EF.MILENAGE_CFG):")
		ef_milenage_cfg = SYSMO_ISIMSJA2_FILE_EF_MILENAGE_CFG(params_swapped)
		print(str(ef_milenage_cfg))

		print(" * Programming...")
		# Note: The milenage configuration file in ADF_USIM and
		# ADF_ISIM are linked, however we write to both locations,
		# just to be sure.
		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_ISIMSJA2_EF_MILENAGE_CFG)
		self.sim.update_binary(ef_milenage_cfg.encode())
		if self.sim.has_isim:
		    self.sim.card.SELECT_ADF_ISIM()
		    self.sim.select(SYSMO_ISIMSJA2_EF_MILENAGE_CFG)
		    self.sim.update_binary(ef_milenage_cfg.encode())
		print("")


	# Select DF_SYSTEM/EF_SIM_AUTH_KEY
	def __select_ef_sim_auth_key(self):
		self.sim.select(GSM_SIM_MF)
		self.sim.select(SYSMO_ISIMSJA2_DF_SYSTEM)
		self.sim.select(SYSMO_ISIMSJA2_EF_SIM_AUTH_KEY)


	# Authentication keys exist in various different files, which are
	# similar, thie method simplifies the selection of those files
	def __select_xsim_auth_key(self, isim = False, _2G = False):
		self.sim.select(GSM_SIM_MF)
		if isim:
			self.sim.card.SELECT_ADF_ISIM()
		else:
			self.sim.card.SELECT_ADF_USIM()

		if _2G:
			self.sim.select(SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY_2G)
		else:
			self.sim.select(SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY)


	# In the SJA2 model the key material and the algorithm configuration
	# is distributed over multiple files, which may also have redundant
	# contents. Files can also be hard linked to other files so that
	# changes in one file may appear in another file as well. The dump
	# method provides an overview of contents of all files at once in
	# order to help debugging problems
	def dump(self):
		print("Reading propritary files...")
		self._init()

		# DF_SYSTEM/EF_SIM_AUTH_KEY:
		self.__select_ef_sim_auth_key()
		res = self._read_binary(self.sim.filelen)
		print(" * DF_SYSTEM/EF_SIM_AUTH_KEY:")
		print(SYSMO_ISIMSJA2_FILE_EF_SIM_AUTH_KEY(res.apdu))

		# ADF_USIM/EF_USIM_AUTH_KEY_2G:
		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		print(" * ADF_USIM/EF_USIM_AUTH_KEY_2G:")
		print(SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G(res.apdu))

		if self.sim.has_isim:
		    # ADF_ISIM/EF_ISIM_AUTH_KEY_2G:
		    self.__select_xsim_auth_key(isim = True, _2G = True)
		    res = self._read_binary(self.sim.filelen)
		    print(" * ADF_ISIM/EF_ISIM_AUTH_KEY_2G:")
		    print(SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G(res.apdu))

		# ADF_USIM/EF_USIM_AUTH_KEY:
		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		print(" * ADF_USIM/EF_USIM_AUTH_KEY:")
		print(SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu))

		if self.sim.has_isim:
		    # ADF_ISIM/EF_ISIM_AUTH_KEY:
		    self.__select_xsim_auth_key(isim = True, _2G = False)
		    res = self._read_binary(self.sim.filelen)
		    print(" * ADF_ISIM/EF_ISIM_AUTH_KEY:")
		    print(SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu))

		# ADF_USIM/EF_MILENAGE_CFG:
		self.sim.select(GSM_SIM_MF)
		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_ISIMSJA2_EF_MILENAGE_CFG)
		res = self._read_binary(self.sim.filelen)
		print(" * ADF_USIM/EF_MILENAGE_CFG:")
		print(SYSMO_ISIMSJA2_FILE_EF_MILENAGE_CFG(res.apdu))

		if self.sim.has_isim:
		    # ADF_ISIM/EF_MILENAGE_CFG:
		    self.sim.select(GSM_SIM_MF)
		    self.sim.card.SELECT_ADF_ISIM()
		    self.sim.select(SYSMO_ISIMSJA2_EF_MILENAGE_CFG)
		    res = self._read_binary(self.sim.filelen)
		    print(" * ADF_ISIM/EF_MILENAGE_CFG:")
		    print(SYSMO_ISIMSJA2_FILE_EF_MILENAGE_CFG(res.apdu))

		# ADF_USIM/EF_USIM_SQN:
		self.sim.select(GSM_SIM_MF)
		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
		res = self._read_binary(self.sim.filelen)
		print(" * ADF_USIM/EF_USIM_SQN:")
		print(SYSMO_ISIMSJA2_FILE_EF_USIM_SQN(res.apdu))

		if self.sim.has_isim:
		    # ADF_USIM/EF_ISIM_SQN:
		    self.sim.select(GSM_SIM_MF)
		    self.sim.card.SELECT_ADF_ISIM()
		    self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
		    res = self._read_binary(self.sim.filelen)
		    print(" * ADF_ISIM/EF_ISIM_SQN:")
		    print(SYSMO_ISIMSJA2_FILE_EF_USIM_SQN(res.apdu))


	# Show current KI value
	def show_ki_params(self):
		print("Reading KI value...")
		self._init()

		# Note: The KI is expected to be the same in all eligible files
		print(" * Reading...")
		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G(res.apdu)

		print(" * Current KI setting:")
		print("   KI: " + hexdump(ef.key))
		print("")


	# Program new KI value
	def write_ki_params(self, ki):
		print("Writing KI value...")
		self._init()

		print(" * New KI setting:")
		print("   KI: " + hexdump(ki))

		print(" * Programming...")

		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G(res.apdu)
		ef.key = ki
		self.sim.update_binary(ef.encode())

		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu)
		ef.key = ki
		self.sim.update_binary(ef.encode())

		if self.sim.has_isim:
		    self.__select_xsim_auth_key(isim = True, _2G = False)
		    res = self._read_binary(self.sim.filelen)
		    ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu)
		    ef.key = ki
		    self.sim.update_binary(ef.encode())

		print("")


	# Show current athentication parameters
	# (Which algorithim is used for which rat?)
	def show_auth_params(self):
		print("Reading Authentication parameters...")
		self._init()

		print(" * Reading...")
		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G(res.apdu)
		algo_2g = ef.algo

		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu)
		algo_3g = ef.algo

		print(" * Current algorithm setting:")
		print("   2G: %d=%s" % (algo_2g, id_to_str(sysmo_isimsja2_algorithms, algo_2g)))
		print("   3G: %d=%s" % (algo_3g, id_to_str(sysmo_isimsja2_algorithms, algo_3g)))
		print("")


	# Program new authentication parameters
	def write_auth_params(self, algo_2g_str, algo_3g_str):
		print("Programming Authentication parameters...")
		self._init()

		if algo_2g_str.isdigit():
			algo_2g = int(algo_2g_str)
		else:
			algo_2g = str_to_id(sysmo_isimsja2_algorithms, algo_2g_str)

		if algo_3g_str.isdigit():
			algo_3g = int(algo_3g_str)
		else:
			algo_3g = str_to_id(sysmo_isimsja2_algorithms, algo_3g_str)

		print(" * New algorithm setting:")
		print("   2G: %d=%s" % (algo_2g, id_to_str(sysmo_isimsja2_algorithms, algo_2g)))
		print("   3G: %d=%s" % (algo_3g, id_to_str(sysmo_isimsja2_algorithms, algo_3g)))

		print(" * Programming...")

		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G(res.apdu)
		ef.algo = algo_2g
		self.sim.update_binary(ef.encode())

		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu)
		ef.algo = algo_3g
		self.sim.update_binary(ef.encode())

		if self.sim.has_isim:
		    self.__select_xsim_auth_key(isim = True, _2G = False)
		    res = self._read_binary(self.sim.filelen)
		    ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu)
		    ef.algo = algo_3g
		    self.sim.update_binary(ef.encode())

		print("")


	# Show current OPc value
	def show_opc_params(self):
		print("Reading OP/c value...")
		self._init()

		# Note: The OPc is expected to be the same in all eligible files
		print(" * Reading...")
		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu)

		if ef.use_opc:
			mode_str = "OPc"
		else:
			mode_str = "OP"

		print(" * Current OP/OPc setting:")
		print("   %s: %s" % (mode_str, hexdump(ef.opc)))
		print("")


	# Program new OPc value
	def write_opc_params(self, select, op):
		if select:
			print("Writing OPc value...")
			mode_str = "OPc"
		else:
			print("Writing OP value...")
			mode_str = "OP"
		self._init()

		print(" * New OPc setting:")
		print("   %s: %s" % (mode_str, hexdump(op)))

		print(" * Programming...")

		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY_2G(res.apdu)
		ef.opc = op
		ef.use_opc = bool(select)
		self.sim.update_binary(ef.encode())

		if self.sim.has_isim:
		    self.__select_xsim_auth_key(isim = True, _2G = False)
		    res = self._read_binary(self.sim.filelen)
		    ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu)
		    ef.opc = op
		    ef.use_opc = bool(select)
		    self.sim.update_binary(ef.encode())

		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_AUTH_KEY(res.apdu)
		ef.opc = op
		ef.use_opc = bool(select)
		self.sim.update_binary(ef.encode())

		print("")


	# Show current milenage SQN parameters
	def show_milenage_sqn_params(self):
		print("Reading Milenage Sequence parameters...")
		self._init()

		print(" * Current SQN Configuration for ADF_USIM:")
		self.sim.select(GSM_SIM_MF)
		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
		res = self._read_binary(self.sim.filelen)
		print(SYSMO_ISIMSJA2_FILE_EF_USIM_SQN(res.apdu))

		if self.sim.has_isim:
		    print(" * Current SQN Configuration for ADF_ISIM:")
		    self.sim.select(GSM_SIM_MF)
		    self.sim.card.SELECT_ADF_ISIM()
		    self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
		    res = self._read_binary(self.sim.filelen)
		    print(SYSMO_ISIMSJA2_FILE_EF_USIM_SQN(res.apdu))

		print("")


	# Reset milenage SQN configuration
	def reset_milenage_sqn_params(self):
		print(" * Resetting SQN Configuration to defaults...")
		self._init()

		print(" * Resetting...")
		self.sim.select(GSM_SIM_MF)

		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
		ef = SYSMO_ISIMSJA2_FILE_EF_USIM_SQN()
		self.sim.update_binary(ef.encode())

		if self.sim.has_isim:
		    self.sim.card.SELECT_ADF_ISIM()
		    self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
		    ef = SYSMO_ISIMSJA2_FILE_EF_USIM_SQN()
		    self.sim.update_binary(ef.encode())

		print("")
