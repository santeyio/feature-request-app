#!/bin/bash

cd /var/opt/feature-requests;
source bin/activate;
kill `cat tmp/gunicorn.pid`;
rm -r feature-request-app;
git clone https://github.com/santeyio/feature-request-app.git;
cd feature-request-app;
pip install -r requirements.txt;
chmod 755 /var/opt/feature-requests/feature-request-app;
find /var/opt/feature-requests/feature-request-app/static -type d -exec chmod 755 {} \;
find /var/opt/feature-requests/feature-request-app/static -type f -exec chmod 644 {} \;
../bin/gunicorn -D --bind 127.0.0.1:5000 -p ../tmp/gunicorn.pid featurerequests:app;

