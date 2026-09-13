#!/bin/sh
set -eu

echo "boot: scanning env for TOKEN/BOT keys..."
env | awk -F= 'toupper($1) ~ /(TOKEN|BOT)/ { print "  key=" $1 " len=" length($2) }' || true

exec python -m bot
