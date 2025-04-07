#!/bin/sh

cd /opt/mempush

. ./venv/bin/activate
flask db migrate
flask run -h localhost -p 3000
deactivate
