#!/bin/bash

set -e

rshell -p /dev/ttyUSB0 rsync -m ./src/ /pyboard/
