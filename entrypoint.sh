#!/bin/sh
set -eu

echo "boot: env key names:"
env | awk -F= '/^[A-Za-z_][A-Za-z0-9_]*=/ { print "  " $1 }' | sort

exec python -m bot
