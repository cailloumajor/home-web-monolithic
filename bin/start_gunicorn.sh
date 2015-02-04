#!/bin/sh

NAME="home_web"
SOCK_PID_DIR="/tmp/home_web"
SOCKFILE="gunicorn.sock"
PIDFILE="gunicorn.pid"
GUNICORN="/home/home_web/.virtualenvs/home_web/bin/gunicorn"

echo "Starting $NAME as $(whoami)"

# Create directory for socket and PID file
[ -d $SOCK_PID_DIR ] || mkdir -p $SOCK_PID_DIR

# Calculate number of workers
if [ -x /usr/bin/nproc ]; then
    WORKERS=$(( $(/usr/bin/nproc) * 2 + 1 ))
else
    WORKERS=3
fi

# Run Gunicorn
exec $GUNICORN \
     --name $NAME \
     --workers $WORKERS \
     --bind "unix:${SOCK_PID_DIR}/${SOCKFILE}" \
     --pid "${SOCK_PID_DIR}/${SOCKFILE}" \
     --log-file - \
     home_web.wsgi
