#!/bin/sh
. ./test-data

# set to 2 (default) + read back
$TOOL -a $ADMPIN -N 02
$TOOL -a $ADMPIN -n

# set to 3 + read back
$TOOL -a $ADMPIN -N 03
$TOOL -a $ADMPIN -n

# set to 2 (default) + read back
$TOOL -a $ADMPIN -N 02
$TOOL -a $ADMPIN -n

