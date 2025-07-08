from config.PATH import BASE_DIR  # 新增导入根目录路径
import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    # 日志目录路径（根目录下的Logs）
    log_dir = os.path.join(BASE_DIR, 'Logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - [%(process)d] - %(message)s'
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    # 创建每天轮转的日志处理器
    log_file = os.path.join(log_dir, 'system.log')
    handler = TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8'
    )
    handler.setFormatter(formatter)
    
    # 获取根日志器并配置
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

# 在模块最后添加全局日志器实例
system_logger = setup_logger()
