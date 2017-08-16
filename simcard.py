#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simcard IO Class

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

from card.USIM import USIM
from card.SIM import SIM
from card.utils import *

# Files
GSM_SIM_MF = [0x3F, 0x00]
GSM_SIM_DF_TELECOM = [0x7F, 0x10]
GSM_SIM_DF_GSM = [0x7F, 0x20]
GSM_SIM_EF_ADN = [0x6f,0x3A]
GSM_SIM_EF_IMSI = [0x6F, 0x07]
GSM_SIM_EF_ICCID = [0x2F, 0xE2]
GSM_USIM_EF_DIR = [0x2F, 0x00] # See also: 3GPP TS 31.102 Table 105

# Card types
GSM_SIM = 0
GSM_USIM = 1

# CHV Types
GSM_CHV1 = 0x01
GSM_CHV2 = 0x02

# Record oriented read modes
GSM_SIM_INS_READ_RECORD_NEXT = 0x02
GSM_SIM_INS_READ_RECORD_PREV = 0x03
GSM_SIM_INS_READ_RECORD_ABS = 0x04

# Record oriented write modes
GSM_SIM_INS_UPDATE_RECORD_NEXT = 0x02
GSM_SIM_INS_UPDATE_RECORD_PREV = 0x03
GSM_SIM_INS_UPDATE_RECORD_ABS = 0x04

class Card_res_apdu():
	apdu = None
	sw = None
	swok = True

	# convert Benoit Michau style result to sysmocom style result
	def from_mich(self, mich):
		self.apdu = mich[3]
                self.sw = [ mich[2][0], mich[2][1] ]

	def __str__(self):
		dump  = "APDU:  " + hexdump(self.apdu)
		dump += "  SW:  " + hexdump(self.sw)
		return dump

# A class to abstract a simcard.
class Simcard():

	card = None

	# Constructor: Create a new simcard object
	def __init__(self, cardtype = GSM_USIM):
		if cardtype == GSM_USIM:
			self.card = USIM()
			self.usim = True
		else:
			self.card = SIM()
			self.usim = False

	# Find the right class byte, depending on the simcard type
	def __get_cla(self, usim):
		return self.card.CLA

	# Select a file
	def select(self, fid, dry = False, strict = True):
		res = Card_res_apdu()
		res.from_mich(self.card.SELECT_FILE(P2 = 0x0C, Data = fid))
		return res

	# Perform card holder verification
	def verify_chv(self, chv, chv_no, dry = False, strict = True):
		res = Card_res_apdu()
		res.from_mich(self.card.VERIFY(P2 = chv_no, Data = chv))
		return res

	# Read CHV retry counter
	def chv_retrys(self, chv_no, dry = False, strict = True):
		res = self.card.VERIFY(P2 = chv_no)
		return res[2][1] & 0x0F

	# Perform file operation (Write)
	def update_binary(self, data, offset = 0, dry = False, strict = True):
		offs_high = (offset >> 8) & 0xFF
		offs_low = offset & 0xFF
		res = Card_res_apdu()
		res.from_mich(self.card.UPDATE_BINARY(offs_high, offs_low, data))
		return res

	# Perform file operation (Read, byte oriented)
	def read_binary(self, length, offset = 0, dry = False, strict = True):
		offs_high = (offset >> 8) & 0xFF
		offs_low = offset & 0xFF
		res = Card_res_apdu()
		res.from_mich(self.card.READ_BINARY(offs_high, offs_low, length))
		return res

	# Perform file operation (Read, record oriented)
	def read_record(self, length, rec_no = 0, dry = False, strict = True):
		res = Card_res_apdu()
		res.from_mich(self.card.READ_RECORD(rec_no, GSM_SIM_INS_READ_RECORD_ABS, length))
		return res


	# Perform file operation (Read, record oriented)
	def update_record(self, data, rec_no = 0, dry = False, strict = True):
		res = Card_res_apdu()
		res.from_mich(self.card.UPDATE_RECORD(rec_no, GSM_SIM_INS_UPDATE_RECORD_ABS, data))
                return res
