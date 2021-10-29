#!/usr/bin/env python3
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

from card import *
from simcard import *
from utils import *
import sys

# CHV Types
SYSMO_USIM_ADM1 = 0x0A

class Sysmo_usim:

	sim = None

	def __init__(self, atr):
		print("Initializing smartcard terminal...")
		self.sim = Simcard(GSM_USIM, toBytes(atr))
		self.sim.card.SELECT_ADF_USIM()
		print(" * Detected Card IMSI:  %s" % self.sim.card.get_imsi())
		if self.sim.has_isim:
			print("   ISIM Application installed")
		if self.sim.has_usim:
			print("   USIM Application installed")
		print("")

	def _warn_failed_auth(self, attempts = 3, keytype = "ADM1"):
		print("   ===  Authentication problem! The Card will permanently   ===")
		print("   === lock down after %d failed attemts! Double check %s! ===" % (attempts, keytype))
		print("")

	def _warn_remaining_auth(self, attempts = 3, keytype = "ADM1"):
		print(" * Error: Only two authentication attempts remaining, we don't")
		print("          want to risk another failed authentication attempt!")
		print("          (double check ADM1 and use option -f to override)")
		print("")


	# Initalize card (select master file)
	def _init(self):
		print(" * Initalizing...")
		self.sim.select(GSM_SIM_MF)


	# Read files sensitively
	def _read_binary(self, length, offset=0):
		res = self.sim.read_binary(length, offset)
		if len(res.apdu) != length:
			print("   Error: could not read file (sw=%02x%02x) -- abort!\n" % (res.sw[0], res.sw[1]))
			exit(1)
		return res


	# Authenticate as administrator
	def admin_auth(self, adm1, force = False):
		print("Authenticating...")
		rc = True
		rem_attemts = self.sim.chv_retrys(SYSMO_USIM_ADM1)

		print(" * Remaining attempts: " + str(rem_attemts))

		# Stop if a decreased ADM1 retry counter is detected
		if(rem_attemts < 3) and force == False:
			self._warn_remaining_auth()
			self._warn_failed_auth()
			return False

		if(len(adm1) != 8):
			print(" * Error: Short ADM1, a valid ADM1 is 8 digits long!")
			print("")
			self._warn_failed_auth()
			return False

		# Try to authenticate
		try:
			print(" * Authenticating...")
			res = self.sim.verify_chv(adm1, SYSMO_USIM_ADM1)
			if res.sw != [0x90, 0x00]:
				raise
			print(" * Authentication successful")
		except:
			print(" * Error: Authentication failed!")
			rc = False

		# Read back and display remaining attemts
		rem_attemts = self.sim.chv_retrys(SYSMO_USIM_ADM1)
		print(" * Remaining attempts: " + str(rem_attemts))
		print("")

		if rc == False:
			self._warn_failed_auth()
		return rc


	# Show current ICCID value
	def show_iccid(self):
		print("Reading ICCID value...")
		self._init()
		print(" * Reading...")
		print(" * Card ICCID: %s" % self.sim.card.get_ICCID())
		print("")


	# Program new ICCID value
	# Note: Since the ICCID is a stanard file writing to it works the same
	# way for all card models. However, the ICCID may be linked to the
	# license management of the card O/S, so changing it might cause
	# problems for some cards models. (USE WITH CAUTION!)
	def write_iccid(self, iccid):
		print("Writing ICCID value...")
		self._init()

		print(" * New ICCID setting:")
		print("   ICCID: " + hexdump(iccid))

		self.sim.select(GSM_SIM_EF_ICCID)

		print(" * Programming...")
		self.sim.update_binary(swap_nibbles(iccid))
		print("")


	# Program new IMSI value
	def write_imsi(self, imsi):
		print("Writing IMSI value...")
		self._init()

		print(" * New ISMI setting:")
		print("   IMSI: " + hexdump(imsi))

		self.sim.select(GSM_SIM_DF_GSM)
		self.sim.select(GSM_SIM_EF_IMSI)

		imsi = [len(imsi)] + swap_nibbles(imsi)

		print(" * Programming...")
		self.sim.update_binary(imsi)
		print("")


	# Show current mnc length value
	def show_mnclen(self):
		print("Reading MNCLEN value...")
		self._init()

		print(" * Reading...")
		self.sim.select(GSM_SIM_DF_GSM)
		self.sim.select(GSM_SIM_EF_AD)
		res = self.sim.read_binary(4)

		print(" * Current MNCLEN setting:")
		print("   MNCLEN: " + "0x%02x" % res.apdu[3])
		print("")


	# Program new mnc length value
	def write_mnclen(self, mnclen):
		print("Writing MNCLEN value...")
		self._init()

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


	# Show installed applications (AIDs)
	def show_aid(self):
		print("Reading application directory...");
		self._init()
		self.sim.card.get_AID()
		AID = self.sim.card.AID
		for a in AID:
			if a[0:7] == [0xA0, 0x00, 0x00, 0x00, 0x87, 0x10, 0x02]:
				appstr = "USIM"
			elif a[0:7] == [0xA0, 0x00, 0x00, 0x00, 0x87, 0x10, 0x04]:
				appstr = "ISIM"
			else:
				appstr = "(unknown)"
			print("   AID: " + hexdump(a[0:5]) + " " +  hexdump(a[5:7]) + " " +  hexdump(a[7:]) + " ==> " + appstr)
		print("")
