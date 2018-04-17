#!/bin/bash

set -e
set -x

if [ ! -d venv ]; then
  python3 -m virtualenv --python=python3 venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

python deploy.py

mv deploy/nginx.conf /etc/nginx/sites-available/beepboop.ktensor.com
ln -s /etc/nginx/sites-available/beepboop.ktensor.com /etc/nginx/sites-enabled/beepboop.ktensor.com
nginx -t
service nginx restart

mv deploy/gunicorn.service /etc/systemd/system/gunicorn.service
mv deploy/gunicorn.socket /etc/systemd/system/gunicorn.socket
mv deploy/gunicorn.conf /etc/tmpfiles.d/gunicorn.conf

systemctl daemon-reload
systemctl enable gunicorn.socket
systemctl start gunicorn.socket
systemctl start gunicorn.service
