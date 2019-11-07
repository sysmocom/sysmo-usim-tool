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
from utils import *

# Files
GSM_SIM_MF = [0x3F, 0x00]
GSM_SIM_DF_TELECOM = [0x7F, 0x10]
GSM_SIM_DF_GSM = [0x7F, 0x20]
GSM_SIM_EF_ADN = [0x6f,0x3A]
GSM_SIM_EF_IMSI = [0x6F, 0x07]
GSM_SIM_EF_AD = [0x6f, 0xAD]
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

	# convert Benoit Michau style result to sysmocom style result
	def from_mich(self, mich):
		self.apdu = mich[3]
                self.sw = [ mich[2][0], mich[2][1] ]

	def __str__(self):
		dump = ""
		if len(self.apdu) > 0:
			dump = "APDU: " + hexdump(self.apdu)
		else:
			dump = "APDU: (no data)"
		dump += ", SW: " + hexdump(self.sw)
		return dump

# A class to abstract a simcard.
class Simcard():

	card = None
	filelen = 0 #length of the currently selected file

	# Constructor: Create a new simcard object
	def __init__(self, cardtype = GSM_USIM, atr = None):
		if cardtype == GSM_USIM:
			self.card = USIM(atr)
			self.usim = True
		else:
			self.card = SIM(atr)
			self.usim = False

	# Find the right class byte, depending on the simcard type
	def __get_cla(self, usim):
		return self.card.CLA

	# Get file size from FCP
	def __get_len_from_tlv(self, fcp):
		# Note: This has been taken from http://git.osmocom.org/pysim/tree/pySim/commands.py,
		# but pySim uses ascii-hex strings for its internal data representation. We use
		# regular lists with integers, so we must convert to an ascii-hex string first:
		fcp =  ''.join('{:02x}'.format(x) for x in fcp)

		# see also: ETSI TS 102 221, chapter 11.1.1.3.1 Response for MF,
		# DF or ADF
		from pytlv.TLV import TLV
		tlvparser = TLV(['82', '83', '84', 'a5', '8a', '8b', '8c', '80', 'ab', 'c6', '81', '88'])

		# pytlv is case sensitive!
		fcp = fcp.lower()

		if fcp[0:2] != '62':
			raise ValueError('Tag of the FCP template does not match, expected 62 but got %s'%fcp[0:2])

		# Unfortunately the spec is not very clear if the FCP length is
		# coded as one or two byte vale, so we have to try it out by
		# checking if the length of the remaining TLV string matches
		# what we get in the length field.
		# See also ETSI TS 102 221, chapter 11.1.1.3.0 Base coding.
		exp_tlv_len = int(fcp[2:4], 16)
		if len(fcp[4:])/2 == exp_tlv_len:
			skip = 4
		else:
			exp_tlv_len = int(fcp[2:6], 16)
			if len(fcp[4:])/2 == exp_tlv_len:
				skip = 6

		# Skip FCP tag and length
		tlv = fcp[skip:]
		tlv_parsed = tlvparser.parse(tlv)

		if '80' in tlv_parsed:
			return int(tlv_parsed['80'], 16)
		else:
			return 0

	# Get the file length from a response (select)
	def __len(self, res, p2):
		if p2 == 0x04:
			return self.__get_len_from_tlv(res)
		else:
			return int(res[-1][4:8], 16)

	# Select a file and retrieve its length
	def select(self, fid):
		self.filelen = 0
		p2 = 0x04
		res = Card_res_apdu()
		res.from_mich(self.card.SELECT_FILE(P2 = p2, Data = fid))

		# Stop here, on failure
		if res.sw[0] != 0x61:
			return res

		res.from_mich(self.card.GET_RESPONSE(res.sw[1]))
		self.filelen = self.__len(res.apdu, p2)
		return res

	# Perform card holder verification
	def verify_chv(self, chv, chv_no):
		res = Card_res_apdu()
		res.from_mich(self.card.VERIFY(P2 = chv_no, Data = chv))
		return res

	# Read CHV retry counter
	def chv_retrys(self, chv_no):
		res = self.card.VERIFY(P2 = chv_no)
		return res[2][1] & 0x0F

	# Perform file operation (Write)
	def update_binary(self, data, offset = 0):
		offs_high = (offset >> 8) & 0xFF
		offs_low = offset & 0xFF
		res = Card_res_apdu()
		res.from_mich(self.card.UPDATE_BINARY(offs_high, offs_low, data))
		return res

	# Perform file operation (Read, byte oriented)
	def read_binary(self, length, offset = 0):
		offs_high = (offset >> 8) & 0xFF
		offs_low = offset & 0xFF
		res = Card_res_apdu()
		res.from_mich(self.card.READ_BINARY(offs_high, offs_low, length))
		return res

	# Perform file operation (Read, record oriented)
	def read_record(self, length, rec_no = 0):
		res = Card_res_apdu()
		res.from_mich(self.card.READ_RECORD(rec_no, GSM_SIM_INS_READ_RECORD_ABS, length))
		return res


	# Perform file operation (Read, record oriented)
	def update_record(self, data, rec_no = 0):
		res = Card_res_apdu()
		res.from_mich(self.card.UPDATE_RECORD(rec_no, GSM_SIM_INS_UPDATE_RECORD_ABS, data))
                return res
