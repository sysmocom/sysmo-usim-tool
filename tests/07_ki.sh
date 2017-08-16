#!/bin/sh
. ./test-data

# set to arbitrary value + read back
$TOOL -a $ADMPIN -K a0b1c2d3e4f5061728394a5b6c7d8e9f
$TOOL -a $ADMPIN -k

# set to original value + read back
$TOOL -a $ADMPIN -K $KI
$TOOL -a $ADMPIN -k

