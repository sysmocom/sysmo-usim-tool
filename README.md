sysmo-usim-tool
===============

This repository contains a python language utility to configure the
vendor-specific parameters of sysmoUSIM-SJS1 programmable USIM cards.

For more information about the sysmoUSIM-SJS1, please see the related
[user manual](https://www.sysmocom.de/manuals/sysmousim-manual.pdf)

sysmoUSIM-SJS1
--------------

The sysmoUSIM-SJS1 is programmable and Java capable USIM card. Not all
commands are known yet and this page should grow over time. Each card is
using a separate ADM1 key and the default configuration is
hacker/developer friendly (fields being writable, reduced security for
installing applets to have more quick development cycles).

https://osmocom.org/projects/cellular-infrastructure/wiki/SysmoUSIM-SJS1

The cards are available from the [sysmocom webshop](http://shop.sysmocom.de/t/sim-card-related/sim-cards)

Dependencies
------------

- To run, http://pyscard.sourceforge.net needs to be installed;
- You may also need to install the pcscd service.

On Debian:

  apt-get install python-pyscard pcscd
  systemctl start pcscd
