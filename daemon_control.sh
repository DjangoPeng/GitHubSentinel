#!/bin/bash
# Control script for a Python daemon

DAEMON_PATH="./src/daemon_process.py"
DAEMON_NAME="DaemonProcess"
LOG_FILE="./logs/$DAEMON_NAME.log"
PID_FILE="./run/$DAEMON_NAME.pid"

start() {
    echo "Starting $DAEMON_NAME..."
    nohup python3 $DAEMON_PATH > $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    echo "$DAEMON_NAME started."
}

stop() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        echo "Stopping $DAEMON_NAME..."
        kill $PID
        echo "$DAEMON_NAME stopped."
        rm $PID_FILE
    else
        echo "$DAEMON_NAME is not running."
    fi
}

status() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null
        then
           echo "$DAEMON_NAME is running."
        else
           echo "$DAEMON_NAME is not running."
        fi
    else
        echo "$DAEMON_NAME is not running."
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
esac
