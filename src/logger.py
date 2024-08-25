# src/logger.py

from loguru import logger
import sys

# 定义统一的日志格式字符串
log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}"

# 配置 Loguru，移除默认的日志配置
logger.remove()

# 使用统一的日志格式配置标准输出和标准错误输出，支持彩色显示
logger.add(sys.stdout, level="DEBUG", format=log_format, colorize=True)
logger.add(sys.stderr, level="ERROR", format=log_format, colorize=True)

# 同样使用统一的格式配置日志文件输出，设置文件大小为1MB自动轮换
logger.add("logs/app.log", rotation="1 MB", level="DEBUG", format=log_format)

# 为logger设置别名，方便在其他模块中导入和使用
LOG = logger

# 将LOG变量公开，允许其他模块通过from logger import LOG来使用它
__all__ = ["LOG"]
