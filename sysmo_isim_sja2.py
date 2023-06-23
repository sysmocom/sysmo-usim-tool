#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gadgets to modify sysmoISIM-SJA2/sysmoISIM-SJA5 parameters

(C) 2017-2023 by sysmocom - s.f.m.c. GmbH
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
#  |   +--[EF_USIM_AUTH_KEY 0xAF20] (regular file)
#  |   |
#  |   +--[EF_USIM_AUTH_KEY_2G 0xAF22] (link to DF_SYSTEM/EF_SIM_AUTH_KEY)
#  |
#  +--[ADF_ISIM]
#      |
#      +--[EF_ISIM_AUTH_KEY 0xAF20] (regular file)
#      |
#      +--[EF_ISIM_AUTH_KEY_2G 0xAF22] (link to DF_SYSTEM/EF_SIM_AUTH_KEY)
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
SYSMO_ISIMSJA5_ALGO_TUAK = 0x06
SYSMO_ISIMSJA5_ALGO_XOR_2G = 0x0E
SYSMO_ISIMSJA2_ALGO_XOR = 0x0F

# Algorithms that are supported by sysmo-isim-sja2 (and also sysmo-isim-sja5)
sysmo_isimsja2_algorithms = [
	(SYSMO_ISIMSJA2_ALGO_COMP12V1, 'COMP128v1'),
	(SYSMO_ISIMSJA2_ALGO_COMP12V2, 'COMP128v2'),
	(SYSMO_ISIMSJA2_ALGO_COMP12V3, 'COMP128v3'),
	(SYSMO_ISIMSJA2_ALGO_MILENAGE, 'MILENAGE'),
	(SYSMO_ISIMSJA2_ALGO_SHA1AKA , 'SHA1-AKA'),
	(SYSMO_ISIMSJA2_ALGO_XOR, 'XOR'),
]

# Algorithms that are supported by sysmo-isim-sja5. This also includes all
# algorithms supported by sysmo-isim-sja2y
sysmo_isimsja5_algorithms = sysmo_isimsja2_algorithms + [
	(SYSMO_ISIMSJA5_ALGO_XOR_2G, 'XOR-2G'),
	(SYSMO_ISIMSJA5_ALGO_TUAK, 'TUAK'),
	]

# Algorithms that use a 16 byte Key in the familiar format of sysmo-isim-sja2
sysmo_isimsjax_16_byte_key_algorithms = [
	SYSMO_ISIMSJA2_ALGO_COMP12V1,
	SYSMO_ISIMSJA2_ALGO_COMP12V2,
	SYSMO_ISIMSJA2_ALGO_COMP12V3,
	SYSMO_ISIMSJA2_ALGO_MILENAGE,
	SYSMO_ISIMSJA2_ALGO_SHA1AKA,
	SYSMO_ISIMSJA2_ALGO_XOR,
	SYSMO_ISIMSJA5_ALGO_XOR_2G,
	]

# TUAK configuration byte
SYSMO_ISIMSJA5_TUAK_RES_SIZE_32_BIT = 0
SYSMO_ISIMSJA5_TUAK_RES_SIZE_64_BIT = 1
SYSMO_ISIMSJA5_TUAK_RES_SIZE_128_BIT = 2
SYSMO_ISIMSJA5_TUAK_RES_SIZE_256_BIT = 3
SYSMO_ISIMSJA5_TUAK_MAC_SIZE_64_BIT = 0
SYSMO_ISIMSJA5_TUAK_MAC_SIZE_128_BIT = 1
SYSMO_ISIMSJA5_TUAK_MAC_SIZE_256_BIT = 2
SYSMO_ISIMSJA5_TUAK_CKIK_SIZE_128_BIT = 0
SYSMO_ISIMSJA5_TUAK_CKIK_SIZE_256_BIT = 1
sysmo_isimsja5_res_sizes = [
	(SYSMO_ISIMSJA5_TUAK_RES_SIZE_32_BIT, "32"),
	(SYSMO_ISIMSJA5_TUAK_RES_SIZE_64_BIT, "64"),
	(SYSMO_ISIMSJA5_TUAK_RES_SIZE_128_BIT, "128"),
	(SYSMO_ISIMSJA5_TUAK_RES_SIZE_256_BIT, "256")
	]
sysmo_isimsja5_mac_sizes = [
	(SYSMO_ISIMSJA5_TUAK_MAC_SIZE_64_BIT, "64"),
	(SYSMO_ISIMSJA5_TUAK_MAC_SIZE_128_BIT, "128"),
	(SYSMO_ISIMSJA5_TUAK_MAC_SIZE_256_BIT, "256")
	]
sysmo_isimsja5_ckik_sizes = [
	(SYSMO_ISIMSJA5_TUAK_CKIK_SIZE_128_BIT, "128"),
	(SYSMO_ISIMSJA5_TUAK_CKIK_SIZE_256_BIT, "256")
	]


sysmo_isimsjax_op_opc = [
	(True, 'OPc'),
	(False, 'OP'),
	]
sysmo_isimsja5_top_topc = [
	(True, 'TOPc'),
	(False, 'TOP'),
	]

class SYSMO_ISIMSJAX_ALGO_PARS_MILENAGE:
	use_opc = False
	sres_dev_func = 1
	four_byte_res = 0 #sysmo-usim-sja5 only

	def __init__(self, content = None):
		if content == None:
			return
		header = content[0]
		self.use_opc = bool((header >> 4) & 1)
		if (header >> 5) & 1:
			self.sres_dev_func = 2
		self.four_byte_res = bool((header >> 6) & 1)

	def __str__(self) -> str:
		dump = ""
		pfx = "   "
		if self.use_opc == True:
			dump += pfx + "use OPc\n"
		else:
			dump += pfx + "use OP\n"
		dump += pfx + "use SRES deviation function " + str(self.sres_dev_func) + "\n"
		if self.four_byte_res:
			dump += pfx + "Return 4 byte RES\n"
		else:
			dump += pfx + "Return full 8 byte RES\n"
		return dump

	def encode(self) -> int:
		out = 0x00
		if self.use_opc == True:
			out |= 1 << 4
		out |= ((self.sres_dev_func-1) & 1) << 5
		out |= ((self.four_byte_res) & 1) << 6
		return out


class SYSMO_ISIMSJAX_ALGO_PARS_SHA1AKA:
	four_byte_res = 0 #sysmo-usim-sja5 only

	def __init__(self, content = None):
		if content == None:
			return
		header = content[0]
		self.four_byte_res = bool((header >> 6) & 1)

	def __str__(self) -> str:
		dump = ""
		pfx = "   "
		if self.four_byte_res:
			dump += pfx + "Return 4 byte RES\n"
		else:
			dump += pfx + "Return full 8 byte RES (default)\n"
		return dump

	def encode(self) -> int:
		out = 0x00
		out |= ((self.four_byte_res) & 1) << 6
		return out


class SYSMO_ISIMSJAX_ALGO_PARS_XOR:
	sres_dev_func = 1
	four_byte_res = 0
	sixteen_byte_res = 0 #Return 16 byte RES (ignores full_res)

	def __init__(self, content = None):
		if content == None:
			return
		header = content[0]
		if (header >> 5) & 1:
			self.sres_dev_func = 2
		self.four_byte_res = bool((header >> 6) & 1)
		self.sixteen_byte_res = bool((header >> 7) & 1)

	def __str__(self) -> str:
		dump = ""
		pfx = "   "
		dump += pfx + "use SRES deviation function" + str(self.sres_dev_func) + "\n"
		if self.sixteen_byte_res:
			dump += pfx + "Return extended 16 byte RES\n"
		elif self.four_byte_res:
			dump += pfx + "Return 4 byte RES\n"
		else:
			dump += pfx + "Return full 8 byte RES (default)\n"
		return dump

	def encode(self) -> int:
		out = 0x00
		out |= ((self.sres_dev_func-1) & 1) << 5
		out |= ((self.four_byte_res) & 1) << 6
		out |= ((self.sixteen_byte_res) & 1) << 7
		return out


class SYSMO_ISIMSJA5_ALGO_PARS_TUAK:
	use_topc = False
	sres_dev_func = 1
	use_256_bit_key = False

	def __init__(self, content = None):
		if content == None:
			return
		header = content[0]
		self.use_topc = bool((header >> 4) & 1)
		if (header >> 5) & 1:
			self.sres_dev_func = 2
		self.use_256_bit_key = bool((header >> 6) & 1)

	def __str__(self) -> str:
		dump = ""
		pfx = "   "
		if self.use_topc == True:
			dump += pfx + "use TOPc\n"
		else:
			dump += pfx + "use TOP\n"
		dump += pfx + "use SRES deviation function " + str(self.sres_dev_func) + "\n"
		if self.use_256_bit_key:
			dump += pfx + "256 bit key length\n"
		else:
			dump += pfx + "128 bit key length\n"
		return dump


	def encode(self) -> int:
		out = 0x00
		if self.use_topc == True:
			out |= 1 << 4
		out |= ((self.sres_dev_func-1) & 1) << 5
		out |= ((self.use_256_bit_key) & 1) << 6
		return out


class SYSMO_ISIMSJAX_FILE_EF_XSIM_AUTH_KEY:
	"""
	Superclass model that generates and parses the header byte of
	SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY, SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY_2G
	and SYSMO_ISIMSJA2_EF_USIM_AUTH_KEY_GBA.
	"""

	algo = SYSMO_ISIMSJA2_ALGO_COMP12V1
	algo_pars = None

	def __init__(self, content = None):
		if content == None:
			return
		header = content[0]
		self.algo = header & 0x0F
		if self.algo == SYSMO_ISIMSJA2_ALGO_MILENAGE:
			self.algo_pars = SYSMO_ISIMSJAX_ALGO_PARS_MILENAGE(content)
		elif self.algo == SYSMO_ISIMSJA2_ALGO_SHA1AKA:
			self.algo_pars = SYSMO_ISIMSJAX_ALGO_PARS_SHA1AKA(content)
		elif self.algo == SYSMO_ISIMSJA2_ALGO_XOR:
			self.algo_pars = SYSMO_ISIMSJAX_ALGO_PARS_XOR(content)
		elif self.algo == SYSMO_ISIMSJA5_ALGO_TUAK:
			self.algo_pars = SYSMO_ISIMSJA5_ALGO_PARS_TUAK(content)

	def __str__(self) -> str:
		dump = ""
		pfx = "   "
		dump += pfx + "Algorithm: "
		dump += id_to_str(sysmo_isimsja5_algorithms, self.algo)
		dump += "\n"
		if self.algo_pars:
			dump += str(self.algo_pars)
		return dump

	def encode(self):
		out = [0x00]
		out[0] = self.algo & 0x0F
		if self.algo_pars:
			out[0] |= self.algo_pars.encode()
		return out

class SYSMO_ISIMSJAX_ALGO_KEY_COMP128:

	ki = [0x00] * 16

	def __init__(self, content = None):
		if content == None:
			return
		self.ki = content[1:17]

	def __str__(self) -> str:
		dump = ""
		pfx = "   "
		dump += pfx + "Ki: " + hexdump(self.ki)
		return dump

	def encode(self) -> list:
		return self.ki


#XOR has the same key length COMP128 (16 byte, no extra data)
class SYSMO_ISIMSJAX_ALGO_KEY_XOR(SYSMO_ISIMSJAX_ALGO_KEY_COMP128):
	pass


#SHA1AKA has the same key length COMP128 (16 byte, no extra data)
class SYSMO_ISIMSJAX_ALGO_KEY_SHA1AKA(SYSMO_ISIMSJAX_ALGO_KEY_COMP128):
	pass


#Milenage adds a 16 byte OP/c
class SYSMO_ISIMSJAX_ALGO_KEY_MILENAGE(SYSMO_ISIMSJAX_ALGO_KEY_COMP128):

	opc = [0x00] * 16

	def __init__(self, content = None):
		if content == None:
			return
		super().__init__(content)
		self.opc = content[17:33]

	def __str__(self) -> str:
		dump = ""
		pfx = "   "
		dump += super().__str__()
		dump += "\n"
		dump += pfx + "OPc: " + hexdump(self.opc)
		return dump

	def encode(self) -> list:
		return super().encode() + self.opc


class SYSMO_ISIMSJAX_ALGO_KEY_TUAK:

	res_size = 0 #3 bit value
	mac_size = 0 #3 bit value
	ckik_size = 0 #1 bit value
	num_keccak = 0 #1 byte value
	topc = [0x00] * 32
	key = [0x00] * 32

	def __init__(self, content = None):
		if content == None:
			return
		self.res_size = int(content[1] & 7)
		self.mac_size = int((content[1] >> 3) & 7)
		self.ckik_size = bool((content[1] >> 6) & 1)
		self.num_keccak =  content[2]
		self.topc = content[3:35]
		self.key = content[35:67]

	def __str__(self) -> str:
		dump = ""
		pfx = "   "
		dump += pfx + "RES size: %s bit" % id_to_str(sysmo_isimsja5_res_sizes, self.res_size) + "\n"
		dump += pfx + "MAC-A/MAC-S size: %s bit" % id_to_str(sysmo_isimsja5_mac_sizes, self.mac_size) + "\n"
		dump += pfx + "Keccak iterations: %d" % self.num_keccak + "\n"
		dump += pfx + "TOPc: " + hexdump(self.topc) + "\n"
		#TODO: Keys may be 128 or 256 bits long. The key length is defined
		#in the header of the file, which means we cannot access this bit
		#from here but it would be nice to display the key in its correct
		#length though.
		dump += pfx + "Key: " + hexdump(self.key)
		return dump

	def encode(self) -> list:
		param_byte = self.res_size & 7
		param_byte |= (self.res_size & 7) << 3
		param_byte |= (self.ckik_size & 1) << 6
		out = [param_byte]
		out += [self.num_keccak]
		out += self.topc
		out += self.key
		return out


class SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(SYSMO_ISIMSJAX_FILE_EF_XSIM_AUTH_KEY):

	algo_key = None

	def __init__(self, content = None):
		# The superclass constructor must ensure that a valid algo and
		# algo parameters are set since we need this information to pick
		# the key configuration below.
		super().__init__(content)
		if self.algo == SYSMO_ISIMSJA2_ALGO_COMP12V1 or \
		   self.algo == SYSMO_ISIMSJA2_ALGO_COMP12V2 or \
		   self.algo == SYSMO_ISIMSJA2_ALGO_COMP12V3:
			self.algo_key = SYSMO_ISIMSJAX_ALGO_KEY_COMP128(content)
		elif self.algo == SYSMO_ISIMSJA2_ALGO_MILENAGE:
			self.algo_key = SYSMO_ISIMSJAX_ALGO_KEY_MILENAGE(content)
		elif self.algo == SYSMO_ISIMSJA2_ALGO_SHA1AKA:
			self.algo_key = SYSMO_ISIMSJAX_ALGO_KEY_SHA1AKA(content)
		elif self.algo == SYSMO_ISIMSJA2_ALGO_XOR or \
		     self.algo == SYSMO_ISIMSJA5_ALGO_XOR_2G:
			self.algo_key = SYSMO_ISIMSJAX_ALGO_KEY_XOR(content)
		elif self.algo == SYSMO_ISIMSJA5_ALGO_TUAK:
			self.algo_key = SYSMO_ISIMSJAX_ALGO_KEY_TUAK(content)

	def __str__(self) -> str:
		dump = ""
		dump += super().__str__()
		dump += str(self.algo_key)
		return dump

	def encode(self) -> list:
		out = super().encode()
		if self.algo_key:
			out += self.algo_key.encode()
		else:
			raise ValueError("key data encoding not supported for selected algorithm!")
		return out


# EF_USIM_AUTH_KEY_2G, EF_SIM_AUTH_KEY and EF_USIM_AUTH_KEY_GBA have the same layout as
# EF_USIM_AUTH_KEY, so there is nothing to specialize other than the class name
class SYSMO_ISIMSJA2_FILE_EF_SIM_AUTH_KEY(SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY):
	pass


class SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY_2G(SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY):
	pass


class SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY_GBA(SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY):
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

	def __str__(self) -> str:
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

	def encode(self) -> list:
		out = [self.R1, self.R2, self.R3, self.R4, self.R5]
		out += self.C1 + self.C2 + self.C3 + self.C4 + self.C5
		return out


class SYSMO_ISIMSJAX_FILE_EF_USIM_SQN:

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

	def __str__(self) -> str:
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

	def encode(self) -> list:
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
	algorithms = sysmo_isimsja2_algorithms

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

	def show_milenage_params(self):
		"""
		Show current milenage parameters
		"""
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

	def write_milenage_params(self, params):
		"""
		Write new milenage parameters
		"""
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
		print(SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY_2G(res.apdu))

		if self.sim.has_isim:
			# ADF_ISIM/EF_ISIM_AUTH_KEY_2G:
			self.__select_xsim_auth_key(isim = True, _2G = True)
			res = self._read_binary(self.sim.filelen)
			print(" * ADF_ISIM/EF_ISIM_AUTH_KEY_2G:")
			print(SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY_2G(res.apdu))

		# ADF_USIM/EF_USIM_AUTH_KEY:
		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		print(" * ADF_USIM/EF_USIM_AUTH_KEY:")
		print(SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu))

		if self.sim.has_isim:
			# ADF_ISIM/EF_ISIM_AUTH_KEY:
			self.__select_xsim_auth_key(isim = True, _2G = False)
			res = self._read_binary(self.sim.filelen)
			print(" * ADF_ISIM/EF_ISIM_AUTH_KEY:")
			print(SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu))

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
		print(SYSMO_ISIMSJAX_FILE_EF_USIM_SQN(res.apdu))

		if self.sim.has_isim:
			# ADF_USIM/EF_ISIM_SQN:
			self.sim.select(GSM_SIM_MF)
			self.sim.card.SELECT_ADF_ISIM()
			self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
			res = self._read_binary(self.sim.filelen)
			print(" * ADF_ISIM/EF_ISIM_SQN:")
			print(SYSMO_ISIMSJAX_FILE_EF_USIM_SQN(res.apdu))

	def __display_key(self, ef, gen:str):
		"""
		Helper method to display key
		"""
		if ef.algo in sysmo_isimsjax_16_byte_key_algorithms:
			print("   %s: Key: %s" % (gen, hexdump(ef.algo_key.ki)))
		elif ef.algo is SYSMO_ISIMSJA5_ALGO_TUAK:
			if not ef.algo_pars.use_256_bit_key:
				print("   %s: Key: %s" % (gen, hexdump(ef.algo_key.key[0:16])))
			else:
				print("   %s: Key: %s" % (gen,  hexdump(ef.algo_key.key)))
		else:
			print(" * %s: Key not applicable for selected algorithm." % gen)

	def show_key_params(self):
		"""
		Show current Key value
		"""
		print("Reading Key value...")
		self._init()

		print(" * Reading...")
		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef_2g = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)

		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef_3g = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)

		if self.sim.has_isim:
			self.__select_xsim_auth_key(isim = True, _2G = False)
			res = self._read_binary(self.sim.filelen)
			ef_4g5g = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
		else:
			ef_4g5g = None

		print(" * Current Key setting:")
		self.__display_key(ef_2g, "2g")
		self.__display_key(ef_3g, "3g")
		if ef_4g5g:
			self.__display_key(ef_4g5g, "4g5g")

		print("")

	def __program_key(self, key, gen:str):
		"""
		Helper method to program key, EF must be selected first
		"""
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
		if ef.algo in sysmo_isimsjax_16_byte_key_algorithms:
			ef.algo_key.ki = key
			self.sim.update_binary(ef.encode())
			print(" * %s: Key programmed." % gen)
		elif ef.algo is SYSMO_ISIMSJA5_ALGO_TUAK:
			ef.algo_key.key = key
			ef.algo_pars.use_256_bit_key = False
			if len(key) > 16:
				ef.algo_pars.use_256_bit_key = True
			self.sim.update_binary(ef.encode())
			print(" * %s: Key programmed." % gen)
		else:
			print(" * %s: Key not applicable for selected algorithm." % gen)

	def write_key_params(self, key):
		"""
		Program new Key value
		"""
		print("Writing Key value...")
		self._init()
		print(" * New Key setting:")
		print("   Key: " + hexdump(key))
		print(" * Programming...")
		self.__select_xsim_auth_key(isim = False, _2G = True)
		self.__program_key(key, "2g")
		self.__select_xsim_auth_key(isim = False, _2G = False)
		self.__program_key(key, "3g")
		if self.sim.has_isim:
			self.__select_xsim_auth_key(isim = True, _2G = False)
			self.__program_key(key, "4g5g")

		print("")

	def show_auth_params(self):
		"""
		Show current authentication parameters
		"""
		print("Reading Authentication parameters...")
		self._init()

		print(" * Reading...")
		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY_2G(res.apdu)
		algo_2g = ef.algo

		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
		algo_3g = ef.algo

		if self.sim.has_isim:
			self.__select_xsim_auth_key(isim = True, _2G = False)
			res = self._read_binary(self.sim.filelen)
			ef = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
			algo_4g5g = ef.algo
		else:
			algo_4g5g = algo_3g

		print(" * Current algorithm setting:")
		print("   2g: %d=%s" % (algo_2g, id_to_str(self.algorithms, algo_2g)))
		print("   3g: %d=%s" % (algo_3g, id_to_str(self.algorithms, algo_3g)))
		print("   4g5g: %d=%s" % (algo_3g, id_to_str(self.algorithms, algo_4g5g)))
		print("")

	def write_auth_params(self, algo_2g_str, algo_3g_str, algo_4g5g_str = None):
		"""
		Write new authentication parameters
		"""
		print("Programming Authentication parameters...")
		self._init()

		if algo_2g_str.isdigit():
			algo_2g = int(algo_2g_str)
		else:
			algo_2g = str_to_id(self.algorithms, algo_2g_str)

		if algo_3g_str.isdigit():
			algo_3g = int(algo_3g_str)
		else:
			algo_3g = str_to_id(self.algorithms, algo_3g_str)

		if algo_4g5g_str:
			if algo_4g5g_str.isdigit():
				algo_4g5g = int(algo_4g5g_str)
			else:
				algo_4g5g = str_to_id(self.algorithms, algo_4g5g_str)
		else:
			algo_4g5g = algo_3g

		print(" * New algorithm setting:")
		print("   2g: %d=%s" % (algo_2g, id_to_str(self.algorithms, algo_2g)))
		print("   3g: %d=%s" % (algo_3g, id_to_str(self.algorithms, algo_3g)))
		print("   4g5g: %d=%s" % (algo_4g5g, id_to_str(self.algorithms, algo_4g5g)))

		print(" * Programming...")

		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
		ef.algo = algo_2g
		self.sim.update_binary(ef.encode())

		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
		ef.algo = algo_3g
		self.sim.update_binary(ef.encode())

		if self.sim.has_isim:
			self.__select_xsim_auth_key(isim = True, _2G = False)
			res = self._read_binary(self.sim.filelen)
			ef = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
			ef.algo = algo_4g5g
			self.sim.update_binary(ef.encode())

		print("")

	def __display_opc(self, ef, gen:str):
		"""
		Helper method to display OP/OPc
		"""
		if ef.algo is SYSMO_ISIMSJA2_ALGO_MILENAGE:
			print("   %s: %s: %s" % (gen, id_to_str(sysmo_isimsjax_op_opc, ef.algo_pars.use_opc), \
						 hexdump(ef.algo_key.opc)))
		elif ef.algo is SYSMO_ISIMSJA5_ALGO_TUAK:
			print("   %s: %s: %s" % (gen, id_to_str(sysmo_isimsja5_top_topc, ef.algo_pars.use_topc), \
						 hexdump(ef.algo_key.topc)))
		else:
			print(" * %s: OP/OPc not applicable for selected algorithm." % gen)

	def show_opc_params(self):
		"""
		Show OP/OPc current configuration. (see also method: write_opc_params).
		"""
		print("Reading OP/c value...")
		self._init()

		print(" * Reading...")
		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef_2g = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)

		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef_3g = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)

		if self.sim.has_isim:
			self.__select_xsim_auth_key(isim = True, _2G = False)
			res = self._read_binary(self.sim.filelen)
			ef_4g5g = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
		else:
			ef_4g5g = None

		print(" * Current OP/OPc setting:")
		self.__display_opc(ef_2g, "2g")
		self.__display_opc(ef_3g, "3g")
		if ef_4g5g:
			self.__display_opc(ef_4g5g, "4g5g")

		print("")

	def __program_opc(self, select:bool, op, gen:str):
		"""
		Helper method to program OP/OPc, EF must be selected first
		"""
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
		if ef.algo is SYSMO_ISIMSJA2_ALGO_MILENAGE:
			ef.algo_key.opc = op
			ef.algo_pars.use_opc = bool(select)
			self.sim.update_binary(ef.encode())
			print("   %s %s programmed." % (gen, id_to_str(sysmo_isimsjax_op_opc, bool(select))));
		elif ef.algo is SYSMO_ISIMSJA5_ALGO_TUAK and len(op) is 32:
			ef.algo_key.topc = op
			ef.algo_pars.use_topc = bool(select)
			self.sim.update_binary(ef.encode())
			print("   %s %s programmed." % (gen, id_to_str(sysmo_isimsja5_top_topc, bool(select))));
		else:
			print("   %s OP/OPc not applicable for selected algorithm, skipping..." % gen)

	def write_opc_params(self, select:bool, op):
		"""
		Program new OP/OPc value. The new OP/OPc value is programmed into all files where the algorithm is
		configured to Milenage. When Milenage is not configured, then the respective file is not touched.
		As a simplification we program the same OP/OPc configuration to all files (2G, 3G, 4G/5G). Even though
		the cards would permit a different setting in each file, it is extremly unlikely that any HLR/HSS would
		use such a configuration.
		"""
		print("Writing %s value..." % id_to_str(sysmo_isimsjax_op_opc, bool(select)))
		self._init()

		print(" * New OPc setting:")
		print("   %s: %s" % (id_to_str(sysmo_isimsjax_op_opc, bool(select)), hexdump(op)))

		print(" * Programming...")
		self.__select_xsim_auth_key(isim = False, _2G = True)
		self.__program_opc(select, op, "2g")
		self.__select_xsim_auth_key(isim = False, _2G = False)
		self.__program_opc(select, op, "3g")
		if self.sim.has_isim:
			self.__select_xsim_auth_key(isim = True, _2G = False)
			self.__program_opc(select, op, "4g5g")

		print("")

	def show_milenage_sqn_params(self):
		"""
		Show current milenage SQN parameters
		"""
		print("Reading Milenage Sequence parameters...")
		self._init()

		print(" * Current SQN Configuration for ADF_USIM:")
		self.sim.select(GSM_SIM_MF)
		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
		res = self._read_binary(self.sim.filelen)
		print(SYSMO_ISIMSJAX_FILE_EF_USIM_SQN(res.apdu))

		if self.sim.has_isim:
			print(" * Current SQN Configuration for ADF_ISIM:")
			self.sim.select(GSM_SIM_MF)
			self.sim.card.SELECT_ADF_ISIM()
			self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
			res = self._read_binary(self.sim.filelen)
			print(SYSMO_ISIMSJAX_FILE_EF_USIM_SQN(res.apdu))

		print("")

	def reset_milenage_sqn_params(self):
		"""
		Reset milenage SQN configuration
		"""
		print(" * Resetting SQN Configuration to defaults...")
		self._init()

		print(" * Resetting...")
		self.sim.select(GSM_SIM_MF)

		self.sim.card.SELECT_ADF_USIM()
		self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
		ef = SYSMO_ISIMSJAX_FILE_EF_USIM_SQN()
		self.sim.update_binary(ef.encode())

		if self.sim.has_isim:
			self.sim.card.SELECT_ADF_ISIM()
			self.sim.select(SYSMO_ISIMSJA2_EF_USIM_SQN)
			ef = SYSMO_ISIMSJAX_FILE_EF_USIM_SQN()
			self.sim.update_binary(ef.encode())

		print("")

	def __display_tuak_cfg(self, ef, gen:str):
		"""
		Helper method to display key
		"""
		if ef.algo is SYSMO_ISIMSJA5_ALGO_TUAK:
			print("   %s: TUAK configuration:" % gen)
			print("      RES size: %s bit" % id_to_str(sysmo_isimsja5_res_sizes, ef.algo_key.res_size))
			print("      MAC-A/MAC-S size: %s bit" % id_to_str(sysmo_isimsja5_mac_sizes,  ef.algo_key.mac_size))
			print("      CK/IK size: %s bit" % id_to_str(sysmo_isimsja5_ckik_sizes,  ef.algo_key.ckik_size))
			print("      Keccak iterations: %d" %  ef.algo_key.num_keccak)
		else:
			print(" * %s: TUAK configuration not applicable for selected algorithm." % gen)

	def show_tuak_cfg(self):
		print("Reading TUAK configuration...")
		self._init()

		print(" * Reading...")
		self.__select_xsim_auth_key(isim = False, _2G = True)
		res = self._read_binary(self.sim.filelen)
		ef_2g = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)

		self.__select_xsim_auth_key(isim = False, _2G = False)
		res = self._read_binary(self.sim.filelen)
		ef_3g = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)

		if self.sim.has_isim:
			self.__select_xsim_auth_key(isim = True, _2G = False)
			res = self._read_binary(self.sim.filelen)
			ef_4g5g = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY(res.apdu)
		else:
			ef_4g5g = None

		print(" * Current TUAK configuration:")
		self.__display_tuak_cfg(ef_2g, "2g")
		self.__display_tuak_cfg(ef_3g, "3g")
		if ef_4g5g:
			self.__display_tuak_cfg(ef_4g5g, "4g5g")
		print("")

	def __program_tuak_cfg(self, res_size:int, mac_size:int, ckik_size:int, num_keccak:int, gen:str):
		"""
		Helper method to program key, EF must be selected first
		"""
		res = self._read_binary(self.sim.filelen)
		ef = SYSMO_ISIMSJAX_FILE_EF_USIM_AUTH_KEY_2G(res.apdu)
		if ef.algo is SYSMO_ISIMSJA5_ALGO_TUAK:
			ef.algo_key.res_size = res_size
			ef.algo_key.mac_size = mac_size
			ef.algo_key.ckik_size = bool(ckik_size)
			ef.algo_key.num_keccak = num_keccak
			self.sim.update_binary(ef.encode())
			print("   %s TUAK configuration programmed." % gen);
		else:
			print("   %s TUAK configuration not applicable for selected algorithm, skipping..." % gen)

	def write_tuak_cfg(self, res_size_str:str, mac_size_str:str, ckik_size_str:str, num_keccak_str:str):

		print("Writing TUAK configuration...")
		self._init()

		print(" * New TUAK configuration:")

		res_size = str_to_id(sysmo_isimsja5_res_sizes, res_size_str, -1)
		if res_size < 0:
			print(" * Invalid TUAK configuration, RES-Size must be 32, 64, 128 or 256 bit!")
			print("")
			return

		mac_size = str_to_id(sysmo_isimsja5_mac_sizes, mac_size_str, -1)
		if mac_size < 0:
			print(" * Invalid TUAK configuration, MAC-Size must be 64, 128 or 256 bit!")
			print("")
			return

		ckik_size = str_to_id(sysmo_isimsja5_ckik_sizes, ckik_size_str, -1)
		if ckik_size < 0:
			print(" * Invalid TUAK configuration, MAC-Size must be 128 or 256 bit!")
			print("")
			return

		num_keccak = int(num_keccak_str)
		if num_keccak > 255:
			print(" * Invalid TUAK configuration, number of Keccak iterations must not exceed 256!")
			print("")
			return

		print("   RES size: %s bit" % id_to_str(sysmo_isimsja5_res_sizes, res_size))
		print("   MAC-A/MAC-S size: %s bit" % id_to_str(sysmo_isimsja5_mac_sizes, mac_size))
		print("   CK/IK size: %s bit" % id_to_str(sysmo_isimsja5_ckik_sizes, ckik_size))
		print("   Keccak iterations: %d" % num_keccak)

		print(" * Programming...")
		self.__select_xsim_auth_key(isim = False, _2G = True)
		self.__program_tuak_cfg(res_size, mac_size, ckik_size, num_keccak, "2g")
		self.__select_xsim_auth_key(isim = False, _2G = False)
		self.__program_tuak_cfg(res_size, mac_size, ckik_size, num_keccak, "3g")
		if self.sim.has_isim:
			self.__select_xsim_auth_key(isim = True, _2G = False)
			self.__program_tuak_cfg(res_size, mac_size, ckik_size, num_keccak, "4g5g")

		print("")

class Sysmo_isim_sja5(Sysmo_isim_sja2):
	algorithms = sysmo_isimsja5_algorithms

	def __init__(self):
		card_detected = False

		# Try card model #1: sysmoISIM-SJA5 (9FV)
		try:
			atr = "3B 9F 96 80 1F 87 80 31 E0 73 FE 21 1B 67 4A 35 75 30 35 02 59 C4"
			print("Trying to find card with ATR: " + atr)
			Sysmo_usim.__init__(self, atr)
			card_detected = True
		except:
			print(" * Card not detected!")

		if card_detected == True:
			return

		# Try card model #2: sysmoISIM-SJA5 (SLM17)
		try:
			atr = "3B 9F 96 80 1F 87 80 31 E0 73 FE 21 1B 67 4A 35 75 30 35 02 65 F8"
			print("Trying to find card with ATR: " + atr)
			Sysmo_usim.__init__(self, atr)
			card_detected = True
		except:
			print(" * Card not detected!")

		if card_detected == True:
			return

		# Try card model #3: sysmoISIM-SJA5 (3FJ)
		try:
			atr = "3B 9F 96 80 1F 87 80 31 E0 73 FE 21 1B 67 4A 35 75 30 35 02 51 CC"
			print("Trying to find card with ATR: " + atr)
			Sysmo_usim.__init__(self, atr)
			card_detected = True
		except:
			print(" * Card not detected!")

		# Exit when we are not able to detect the card
		if card_detected != True:
			sys.exit(1)
