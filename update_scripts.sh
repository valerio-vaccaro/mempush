#!/bin/sh

cd /opt/mempush

. ./venv/bin/activate
date > log.txt
python scripts/push_transactions.py 2>&1 >> log.txt
date >> log.txt
deactivate
