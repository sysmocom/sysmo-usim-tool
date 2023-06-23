#!/bin/sh
. ./test-data

# First we select a configuration that includes TUAK
$TOOL -a $ADMPIN -T "COMP128v1:MILENAGE:TUAK"

# Program/read-back valid TUAK configuration
$TOOL -a $ADMPIN -W 32:64:128:123
$TOOL -a $ADMPIN -w

# Program/read-back a 128 bit key
$TOOL -a $ADMPIN -K a0b1c2d3e4f5061728394a5b6c7d8e9f
$TOOL -a $ADMPIN -k

# Program/read-back a 256 bit key
$TOOL -a $ADMPIN -K a0b1ca0b1c2d3e4fe8394a55061722d3b6c7d8e9f8394a5506172e9fb6c7d84f
$TOOL -a $ADMPIN -k

# Program/read-back a TOP value
$TOOL -a $ADMPIN -O e8394a55061a0b1ca3e4f722d3b6c7d8e172e9fb680b1cc7d84f9f2d394a5506
$TOOL -a $ADMPIN -o

# Program/read-back a TOPc value
$TOOL -a $ADMPIN -C 03b694a5506c7d8e172e9fb680b1cc7d61a0b1ca3e4f722d84e8394a55f9f2d3
$TOOL -a $ADMPIN -o

# restore original Ki value + read back
$TOOL -a $ADMPIN -T "COMP128v1:COMP128v1:COMP128v1"
$TOOL -a $ADMPIN -K $KI
$TOOL -a $ADMPIN -k
