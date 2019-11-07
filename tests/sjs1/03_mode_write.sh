#!/bin/sh
. ./test-data

$TOOL -a $ADMPIN -c
$TOOL -a $ADMPIN -m
$TOOL -a $ADMPIN -u
$TOOL -a $ADMPIN -m
