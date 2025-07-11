@echo off
REM 设置控制台编码为中文GBK
chcp 936 > nul

REM 设置项目根目录为当前脚本所在目录
cd /d "%~dp0"

REM 检查conda解释器是否存在
if not exist ".\.conda\python.exe" (
    echo 错误: 未找到conda解释器, 请检查.conda目录是否存在
    pause
    exit /b 1
)

REM 设置ccache目录
if not exist "ccache\" (
    echo 警告：未找到ccache目录，可能会影响缓存功能
) else (
    echo 检测到ccache目录，已添加到环境变量
)
set "PATH=%CD%\ccache;%PATH%"

REM 添加空行分隔逻辑区块
echo.

REM 记录开始时间
set start_time=%time%

REM 运行主程序并显示执行时间
echo 正在启动敏感数据识别与分类系统...
echo.
echo 正在运行pcap文件处理程序...
@echo off
.\.conda\python.exe -O Step_1.py
if %errorlevel% neq 0 (
    echo 检测到pcap文件处理程序执行失败
    pause
    exit /b 1
)

REM 运行完成后暂停
echo.

echo 正在运行OCR识别程序...
@echo off
.\.conda\python.exe Step_2.py
if %errorlevel% neq 0 (
    echo 检测到OCR识别程序执行失败
    pause
    exit /b 1
)

REM 运行完成后暂停
echo.

echo 正在整合结果...
@echo off
.\.conda\python.exe Step_3.py
if %errorlevel% neq 0 (
    echo 检测到整合结果执行失败
    pause
    exit /b 1
)

REM 记录结束时间
set end_time=%time%

REM 计算总耗时
setlocal enabledelayedexpansion
REM 处理时间格式中的前导空格（当小时为个位数时）
set start_hour=!start_time:~0,2!
set start_hour=!start_hour: =0!
set /a start_minute=1!start_time:~3,2! - 100
set /a start_second=1!start_time:~6,2! - 100

set end_hour=!end_time:~0,2!
set end_hour=!end_hour: =0!
set /a end_minute=1!end_time:~3,2! - 100
set /a end_second=1!end_time:~6,2! - 100

set /a start_total_seconds=start_hour*3600 + start_minute*60 + start_second
set /a end_total_seconds=end_hour*3600 + end_minute*60 + end_second
set /a total_seconds=end_total_seconds - start_total_seconds

REM 处理跨天的情况（结束时间小于开始时间）
if !total_seconds! lss 0 set /a total_seconds+=86400

REM 转换为分:秒格式
set /a minutes=total_seconds / 60
set /a seconds=total_seconds %% 60

echo.
echo 敏感数据识别与分类系统已关闭
echo 总耗时: !minutes! 分钟 !seconds! 秒

@echo off
setlocal enabledelayedexpansion

REM 颜色代码
set "normal=[0m"
set "green=[92m"
set "yellow=[93m"
set "red=[91m"

REM 清理临时文件
echo.
echo 正在检查临时文件...
if exist "Temp" (
    REM 计算临时文件总大小
    for /f "tokens=1,2 delims= " %%a in ('powershell -Command "$sum=(Get-ChildItem 'Temp' -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; if ($sum -eq $null) { $sum = 0 }; if ($sum -ge 1GB) { '{0:N2} GB' -f ($sum / 1GB) } elseif ($sum -ge 1MB) { '{0:N2} MB' -f ($sum / 1MB) } else { '{0:N2} KB' -f ($sum / 1KB) }"') do (
        set "size_val=%%a"
        set "size_unit=%%b"
    )

    echo 检测到临时目录：%cd%\Temp
    REM 添加默认值处理
    if not defined size_val set "size_val=0.00"
    if not defined size_unit set "size_unit=KB"
    echo %green%临时文件总大小：%normal%!size_val! !size_unit!
    set /p "del_temp=%yellow%是否删除临时文件？(y/n) %normal%"
    if /i "!del_temp!"=="y" (
        .\.conda\python.exe -c "from utils.clean_utils import clean_temp; clean_temp()"
        echo %green%已清理临时文件%normal%
    ) else (
        echo %yellow%已跳过临时文件清理%normal%
    )
) else (
    echo %red%未找到临时目录 Temp%normal%
)

pause