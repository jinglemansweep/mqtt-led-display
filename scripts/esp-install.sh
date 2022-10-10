#!/bin/bash

set -e

declare -r port="${1:-/dev/ttyUSB0}"

rshell -p ${port} rsync -m ./src/ /pyboard/
rshell -p ${port} repl
