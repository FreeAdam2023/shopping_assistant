import logging
import os
import uuid
from logging.handlers import RotatingFileHandler
import json


class JsonFormatter(logging.Formatter):
    def format(self, record):
        # 使用标准命令行格式
        log_format = (
            f"{self.formatTime(record, self.datefmt)} "
            f"[{record.levelname}] "
            f"{os.path.basename(record.pathname)}:{record.lineno} "
            f"{record.funcName} - "
            f"{record.getMessage()}"
        )
        return log_format


class Logger:
    def __init__(self, name, log_dir='logs', app_log_file='application.log', audit_log_file='audit.log'):
        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.app_log_path = os.path.join(log_dir, app_log_file)
        self.audit_log_path = os.path.join(log_dir, audit_log_file)

        # 初始化自定义日志
        self.app_logger = logging.getLogger(f'{name}_application')
        self.app_logger.setLevel(logging.DEBUG)
        app_log_handler = RotatingFileHandler(self.app_log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        app_log_handler.setFormatter(JsonFormatter())
        self.app_logger.addHandler(app_log_handler)

        # 添加应用日志的命令行输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        self.app_logger.addHandler(console_handler)

        # 初始化审计日志
        self.audit_logger = logging.getLogger(f'{name}_audit')
        self.audit_logger.setLevel(logging.INFO)
        audit_log_handler = RotatingFileHandler(self.audit_log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        audit_log_handler.setFormatter(JsonFormatter())
        self.audit_logger.addHandler(audit_log_handler)

        # 添加审计日志的命令行输出
        audit_console_handler = logging.StreamHandler()
        audit_console_handler.setFormatter(JsonFormatter())
        self.audit_logger.addHandler(audit_console_handler)

    def info(self, message):
        """记录应用信息日志"""
        self.app_logger.info(message, stacklevel=2)

    def error(self, message):
        """记录应用错误日志"""
        self.app_logger.error(message, stacklevel=2)

    def debug(self, message):
        """记录应用调试日志"""
        self.app_logger.debug(message, stacklevel=2)

    def audit(self, message):
        """记录审计日志"""
        self.audit_logger.info(message, stacklevel=2)

    def warning(self, message):
        """记录应用警告日志"""
        self.app_logger.warning(message, stacklevel=2)

    def critical(self, message):
        """记录应用关键日志"""
        self.app_logger.critical(message, stacklevel=2)

    def set_log_level(self, level):
        """动态设置应用日志级别"""
        self.app_logger.setLevel(level)

    def set_audit_level(self, level):
        """动态设置审计日志级别"""
        self.audit_logger.setLevel(level)


# 实例化日志类
logger = Logger(name='main.py')
#
# # 使用示例
# logger.info('Starting the Facebook crawl logs process.')
