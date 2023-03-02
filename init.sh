#!/bin/bash
set -e

# echo "Starting SSH ..."
service ssh start

echo "Starting CSAFE server2"
echo $PWD
echo $FLASK_INTENT
python3 app.py

# Start Gunicorn processes
#echo Starting Gunicorn.
#exec gunicorn csafe.wsgi:application \
#    --bind 0.0.0.0:8000 \
#    --workers 3