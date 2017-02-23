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

from card import *

# This is an abstraction which offers a set of tools to handle the most basic
# operations that can be performed on a sim card. The implementation is not
# simcard model specific

# Classes
GSM_SIM_CLA = 0xA0
GSM_USIM_CLA = 0x00

# Instructions, see also GSM 11.11, Table 9 Coding of the commands
GSM_SIM_INS_SELECT = 0xA4
GSM_SIM_INS_STATUS = 0xF2
GSM_SIM_INS_READ_BINARY = 0xB0
GSM_SIM_INS_UPDATE_BINARY = 0xD6
GSM_SIM_INS_READ_RECORD = 0xB2
GSM_SIM_INS_UPDATE_RECORD = 0xDC
GSM_SIM_INS_SEEK = 0xA2
GSM_SIM_INS_INCREASE = 0x32
GSM_SIM_INS_VERIFY_CHV = 0x20
GSM_SIM_INS_CHANGE_CHV = 0x24
GSM_SIM_INS_DISABLE_CHV = 0x26
GSM_SIM_INS_ENABLE_CHV = 0x28
GSM_SIM_INS_UNBLOCK_CHV = 0x2C
GSM_SIM_INS_INVALIDATE = 0x04
GSM_SIM_INS_REHABILITATE = 0x44
GSM_SIM_INS_RUN_GSM_ALGORITHM = 0x88
GSM_SIM_INS_SLEEP = 0xFA
GSM_SIM_INS_GET_RESPONSE = 0xC0
GSM_SIM_INS_TERMINAL_PROFILE = 0x10
GSM_SIM_INS_ENVELOPE = 0xC2
GSM_SIM_INS_FETCH = 0x12
GSM_SIM_INS_TERMINAL_RESPONSE = 0x14

# Partial File tree:
# The following tree is incomplete, it just contains the files we have been
# interested in so far. A full SIM card file tree can be found in:
# GSM TS 11.11, Figure 8: "File identifiers and directory structures of GSM"
# 3GPP TS 31.102, cap. 4.7: "Files of USIM"
#
# [MF 0x3F00]
#  |
#  +--[EF_DIR 0x2F00]
#  |
#  +--[EF_ICCID 0x2FE2]
#  |
#  +--[DF_TELECOM 0x7F10]
#  |   |
#  |   +-[EF_ADN 0x7F20]
#  |
#  +--[DF_GSM 0x7F20]
#      |
#      +-[EF_IMSI 0x6F07]

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

# A class to abstract a simcard.
class Simcard():

	card = None
	usim = None

	# Constructor: Create a new simcard object
	def __init__(self, terminal, cardtype = GSM_USIM):

		self.card = terminal
		if cardtype == GSM_USIM:
			self.usim = True
		else:
			self.usim = True


	# Find the right class byte, depending on the simcard type
	def __get_cla(self, usim):

		if (usim):
			return GSM_USIM_CLA
		else:
			return GSM_SIM_CLA


	# Select a file
	def select(self, fid, dry = False, strict = True):

		cla = self.__get_cla(self.usim)
		ins = GSM_SIM_INS_SELECT
		length = 0x02
	
		apdu = self.card.apdu(cla, ins, p2 = 0x0C,
			p3 = length, data = fid)
		return self.card.transact(apdu, dry, strict)


	# Perform card holder verification
	def verify_chv(self, chv, chv_no, dry = False, strict = True):

		cla = self.__get_cla(self.usim)
		ins = GSM_SIM_INS_VERIFY_CHV
		length = 0x08

		apdu = self.card.apdu(cla, ins, p2 = chv_no,
			p3 = length, data = chv)
		return self.card.transact(apdu, dry, strict)


	# Perform file operation (Write)
	def update_binary(self, data, offset = 0, dry = False, strict = True):

		cla = self.__get_cla(self.usim)
		ins = GSM_SIM_INS_UPDATE_BINARY
		length = len(data)
		offs_high = (offset >> 8) & 0xFF
		offs_low = offset & 0xFF

		apdu = self.card.apdu(cla, ins, p1 = offs_high, p2 = offs_low,
			p3 = length, data = data)
		return self.card.transact(apdu, dry, strict)


	# Perform file operation (Read, byte oriented)
	def read_binary(self, length, offset = 0, dry = False, strict = True):

		cla = self.__get_cla(self.usim)
		ins = GSM_SIM_INS_READ_BINARY
		offs_high = (offset >> 8) & 0xFF
		offs_low = offset & 0xFF

		apdu = self.card.apdu(cla, ins, p1 = offs_high,
			p2 = offs_low, p3 = length)
		return self.card.transact(apdu, dry, strict)


	# Perform file operation (Read, record oriented)
	def read_record(self, length, rec_no = 0, dry = False, strict = True):

		cla = self.__get_cla(self.usim)
		ins = GSM_SIM_INS_READ_RECORD

		apdu = self.card.apdu(cla, ins, p1 = rec_no,
			p2 = GSM_SIM_INS_READ_RECORD_ABS, p3 = length)
		return self.card.transact(apdu, dry, strict)


	# Perform file operation (Read, record oriented)
	def update_record(self, data, rec_no = 0, dry = False, strict = True):

		cla = self.__get_cla(self.usim)
		ins = GSM_SIM_INS_UPDATE_RECORD
		length = len(data)

		apdu = self.card.apdu(cla, ins, p1 = rec_no,
			p2 = GSM_SIM_INS_UPDATE_RECORD_ABS,
			p3 = length, data = data)
		return self.card.transact(apdu, dry, strict)












