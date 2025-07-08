@echo off
REM ���ÿ���̨����Ϊ����GBK
chcp 936 > nul

REM ������Ŀ��Ŀ¼Ϊ��ǰ�ű�����Ŀ¼
cd /d "%~dp0"

REM ���conda�������Ƿ����
if not exist ".\.conda\python.exe" (
    echo ����: δ�ҵ�conda������, ����.condaĿ¼�Ƿ����
    pause
    exit /b 1
)

REM ����ccacheĿ¼
if not exist "ccache\" (
    echo ���棺δ�ҵ�ccacheĿ¼�����ܻ�Ӱ�컺�湦��
) else (
    echo ��⵽ccacheĿ¼������ӵ���������
)
set "PATH=%CD%\ccache;%PATH%"

REM ��ӿ��зָ��߼�����
echo.

REM ��¼��ʼʱ��
set start_time=%time%

REM ������������ʾִ��ʱ��
echo ����������������ʶ�������ϵͳ...
echo.
echo ��������pcap�ļ��������...
@echo off
.\.conda\python.exe -O Step_1.py
if %errorlevel% neq 0 (
    echo ��⵽pcap�ļ��������ִ��ʧ��
    pause
    exit /b 1
)

REM ������ɺ���ͣ
echo.

echo ��������OCRʶ�����...
@echo off
.\.conda\python.exe Step_2.py
if %errorlevel% neq 0 (
    echo ��⵽OCRʶ�����ִ��ʧ��
    pause
    exit /b 1
)

REM ������ɺ���ͣ
echo.

echo �������Ͻ��...
@echo off
.\.conda\python.exe Step_3.py
if %errorlevel% neq 0 (
    echo ��⵽���Ͻ��ִ��ʧ��
    pause
    exit /b 1
)

REM ��¼����ʱ��
set end_time=%time%

REM �����ܺ�ʱ
setlocal enabledelayedexpansion
REM ����ʱ���ʽ�е�ǰ���ո񣨵�СʱΪ��λ��ʱ��
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

REM �����������������ʱ��С�ڿ�ʼʱ�䣩
if !total_seconds! lss 0 set /a total_seconds+=86400

REM ת��Ϊ��:���ʽ
set /a minutes=total_seconds / 60
set /a seconds=total_seconds %% 60

echo.
echo ��������ʶ�������ϵͳ�ѹر�
echo �ܺ�ʱ: !minutes! ���� !seconds! ��

@echo off
setlocal enabledelayedexpansion

REM ��ɫ����
set "normal=[0m"
set "green=[92m"
set "yellow=[93m"
set "red=[91m"

REM ������ʱ�ļ�
echo.
echo ���ڼ����ʱ�ļ�...
if exist "Temp" (
    REM ������ʱ�ļ��ܴ�С
    for /f "tokens=1,2 delims= " %%a in ('powershell -Command "$sum=(Get-ChildItem 'Temp' -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; if ($sum -eq $null) { $sum = 0 }; if ($sum -ge 1GB) { '{0:N2} GB' -f ($sum / 1GB) } elseif ($sum -ge 1MB) { '{0:N2} MB' -f ($sum / 1MB) } else { '{0:N2} KB' -f ($sum / 1KB) }"') do (
        set "size_val=%%a"
        set "size_unit=%%b"
    )

    echo ��⵽��ʱĿ¼��%cd%\Temp
    REM ���Ĭ��ֵ����
    if not defined size_val set "size_val=0.00"
    if not defined size_unit set "size_unit=KB"
    echo %green%��ʱ�ļ��ܴ�С��%normal%!size_val! !size_unit!
    set /p "del_temp=%yellow%�Ƿ�ɾ����ʱ�ļ���(y/n) %normal%"
    if /i "!del_temp!"=="y" (
        .\.conda\python.exe -c "from utils.clean_utils import clean_temp; clean_temp()"
        echo %green%��������ʱ�ļ�%normal%
    ) else (
        echo %yellow%��������ʱ�ļ�����%normal%
    )
) else (
    echo %red%δ�ҵ���ʱĿ¼ Temp%normal%
)

pause