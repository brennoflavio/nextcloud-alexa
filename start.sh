# /bin/sh

rm -rf /srv/logs
mkdir /srv/logs/
touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
tail -n 0 -f /srv/logs/*.log &

echo Starting Gunicorn
#flask run
 exec gunicorn main:app \
     --bind 0.0.0.0:5000 \
     --chdir /usr/src/app/ \
     --workers 1 \
     --log-level=debug \
     --log-file=/srv/logs/gunicorn.log \
     --access-logfile=/srv/logs/access.log \
     --timeout 110 \
     --limit-request-line 0
