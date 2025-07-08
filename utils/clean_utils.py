import os
import shutil
#============= 系统自定义模块 =============
from utils.logger import system_logger
#=========================================

def clean_temp(temp_dir='Temp'):
    """
    安全清理临时目录
    功能：
        1. 删除Temp目录下所有内容
        2. 保留空Temp目录
        3. 记录清理日志
    参数：
        temp_dir: 要清理的目录路径(默认当前目录下的Temp)
    """
    if not os.path.exists(temp_dir):
        system_logger.warning(f"临时目录不存在: {temp_dir}")
        return

    try:
        # 遍历删除目录内容(保留顶层目录)
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # 删除文件或符号链接
                system_logger.debug(f"已删除文件: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 递归删除子目录
                system_logger.debug(f"已删除目录: {file_path}")
                
        system_logger.info(f"成功清理临时目录: {temp_dir}")
    except Exception as e:
        system_logger.error(f"清理失败: {str(e)}")
        raise RuntimeError(f"临时目录清理异常: {str(e)}") from e
