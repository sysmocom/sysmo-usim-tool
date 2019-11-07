#!/bin/sh
. ./test-data

# we can only read them for now, which will of course change once we perform auth against it
$TOOL -a $ADMPIN -s

# test if resetting SQN parameters works
$TOOL -a $ADMPIN -S
