sysmo-usim-tool
===============

This repository contains a python language utility to configure the
vendor-specific parameters of sysmocom programmable SIM/USIM/ISIM cards.

For more information about the SIM cards, please see the related
[user manual](https://www.sysmocom.de/manuals/sysmousim-manual.pdf)

sysmoISIM-SJA2
--------------

The sysmoISIM-SJA2 is programmable and Java capable USIM, ISIM and HPSIM card.
Each card is using a separate ADM1 key and the default configuration is
hacker/developer friendly (fields being writable, reduced security for
installing applets to have more quick development cycles).

https://osmocom.org/projects/cellular-infrastructure/wiki/SysmoISIM-SJA2

The cards are available from the [sysmocom webshop](http://shop.sysmocom.de/products/sysmoISIM-SJA2)


sysmoUSIM-SJS1
--------------

The sysmoUSIM-SJS1 is programmable and Java capable USIM card.
Each card is using a separate ADM1 key and the default configuration is
hacker/developer friendly (fields being writable, reduced security for
installing applets to have more quick development cycles).

https://osmocom.org/projects/cellular-infrastructure/wiki/SysmoUSIM-SJS1

Dependencies
------------

- To run, http://pyscard.sourceforge.net needs to be installed;
- You may also need to install the pcscd service.

On Debian:

  apt-get install python-pyscard pcscd
  systemctl start pcscd
