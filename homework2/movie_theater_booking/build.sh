#!/usr/bin/env bash
# Render runs this on every deploy.
set -o errexit   # stop immediately if any command fails

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_demo