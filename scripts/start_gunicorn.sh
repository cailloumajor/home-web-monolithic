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
    THREADS=$(( $(/usr/bin/nproc) * 2 + 1 ))
else
    THREADS=3
fi

# Run Gunicorn
exec $GUNICORN \
     --name $NAME \
     --threads $THREADS \
     --bind "unix:${SOCK_PID_DIR}/${SOCKFILE}" \
     --pid "${SOCK_PID_DIR}/${PIDFILE}" \
     --log-file - \
     home_web.wsgi
