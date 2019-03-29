#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo Collecting static files
python manage.py collectstatic --no-input

ls -al /static/

chmod -R 777 /static

# run gatekeeper
./keycloak-gatekeeper --config gatekeeper.conf 2>&1 | tee /tmp/gatekeeper.log &

# run uwsgi
exec uwsgi

