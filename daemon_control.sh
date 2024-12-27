#!/bin/bash
# 守护进程控制脚本

# 定义守护进程 Python 脚本的路径
DAEMON_PATH="./src/daemon_process.py"
# 定义守护进程的名称
DAEMON_NAME="DaemonProcess"
# 定义日志文件的路径
LOG_FILE="./logs/$DAEMON_NAME.log"
# 定义守护进程的 PID 文件路径，用于存储进程号
PID_FILE="./run/$DAEMON_NAME.pid"

# 启动守护进程的函数
start() {
    echo "Starting $DAEMON_NAME..."
    # 使用 nohup 命令在后台运行 Python 脚本，并将输出重定向到日志文件
    nohup python3 $DAEMON_PATH > $LOG_FILE 2>&1 &
    # 将守护进程的 PID 写入文件
    echo $! > $PID_FILE
    echo "$DAEMON_NAME started."
}

# 停止守护进程的函数
stop() {
    if [ -f $PID_FILE ]; then
        # 如果 PID 文件存在，读取 PID
        PID=$(cat $PID_FILE)
        echo "Stopping $DAEMON_NAME..."
        # 使用 kill 命令停止进程
        kill $PID
        echo "$DAEMON_NAME stopped."
        # 删除 PID 文件
        rm $PID_FILE
    else
        echo "$DAEMON_NAME is not running."
    fi
}

# 检查守护进程状态的函数
status() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        # 检查进程是否在运行
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

# 根据输入参数选择执行哪个函数
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
        # 重启守护进程
        stop
        start
        ;;
    *)
        # 如果参数不符合预期，显示用法
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
esac
