@echo off
REM ÉèÖÃ¿ØÖÆÌ¨±àÂëÎªÖĞÎÄGBK
chcp 936 > nul

REM ÉèÖÃÏîÄ¿¸ùÄ¿Â¼Îªµ±Ç°½Å±¾ËùÔÚÄ¿Â¼
cd /d "%~dp0"

REM ¼ì²éconda½âÊÍÆ÷ÊÇ·ñ´æÔÚ
if not exist ".\.conda\python.exe" (
    echo ´íÎó: Î´ÕÒµ½conda½âÊÍÆ÷, Çë¼ì²é.condaÄ¿Â¼ÊÇ·ñ´æÔÚ
    pause
    exit /b 1
)

REM ÉèÖÃccacheÄ¿Â¼
if not exist "ccache\" (
    echo ¾¯¸æ£ºÎ´ÕÒµ½ccacheÄ¿Â¼£¬¿ÉÄÜ»áÓ°Ïì»º´æ¹¦ÄÜ
) else (
    echo ¼ì²âµ½ccacheÄ¿Â¼£¬ÒÑÌí¼Óµ½»·¾³±äÁ¿
)
set "PATH=%CD%\ccache;%PATH%"

REM Ìí¼Ó¿ÕĞĞ·Ö¸ôÂß¼­Çø¿é
echo.

REM ¼ÇÂ¼¿ªÊ¼Ê±¼ä
set start_time=%time%

REM ÔËĞĞÖ÷³ÌĞò²¢ÏÔÊ¾Ö´ĞĞÊ±¼ä
echo ÕıÔÚÆô¶¯Ãô¸ĞÊı¾İÊ¶±ğÓë·ÖÀàÏµÍ³...
echo.
echo ÕıÔÚÔËĞĞpcapÎÄ¼ş´¦Àí³ÌĞò...
@echo off
.\.conda\python.exe -O Step_1.py
if %errorlevel% neq 0 (
    echo ¼ì²âµ½pcapÎÄ¼ş´¦Àí³ÌĞòÖ´ĞĞÊ§°Ü
    pause
    exit /b 1
)

REM ÔËĞĞÍê³ÉºóÔİÍ£
echo.

echo ÕıÔÚÔËĞĞOCRÊ¶±ğ³ÌĞò...
@echo off
.\.conda\python.exe Step_2.py
if %errorlevel% neq 0 (
    echo ¼ì²âµ½OCRÊ¶±ğ³ÌĞòÖ´ĞĞÊ§°Ü
    pause
    exit /b 1
)

REM ÔËĞĞÍê³ÉºóÔİÍ£
echo.

echo ÕıÔÚÕûºÏ½á¹û...
@echo off
.\.conda\python.exe Step_3.py
if %errorlevel% neq 0 (
    echo ¼ì²âµ½ÕûºÏ½á¹ûÖ´ĞĞÊ§°Ü
    pause
    exit /b 1
)

REM ¼ÇÂ¼½áÊøÊ±¼ä
set end_time=%time%

REM ¼ÆËã×ÜºÄÊ±
setlocal enabledelayedexpansion
REM ´¦ÀíÊ±¼ä¸ñÊ½ÖĞµÄÇ°µ¼¿Õ¸ñ£¨µ±Ğ¡Ê±Îª¸öÎ»ÊıÊ±£©
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

REM ´¦Àí¿çÌìµÄÇé¿ö£¨½áÊøÊ±¼äĞ¡ÓÚ¿ªÊ¼Ê±¼ä£©
if !total_seconds! lss 0 set /a total_seconds+=86400

REM ×ª»»Îª·Ö:Ãë¸ñÊ½
set /a minutes=total_seconds / 60
set /a seconds=total_seconds %% 60

echo.
echo Ãô¸ĞÊı¾İÊ¶±ğÓë·ÖÀàÏµÍ³ÒÑ¹Ø±Õ
echo ×ÜºÄÊ±: !minutes! ·ÖÖÓ !seconds! Ãë

@echo off
setlocal enabledelayedexpansion

REM ÑÕÉ«´úÂë
set "normal=[0m"
set "green=[92m"
set "yellow=[93m"
set "red=[91m"

REM ÇåÀíÁÙÊ±ÎÄ¼ş
echo.
echo ÕıÔÚ¼ì²éÁÙÊ±ÎÄ¼ş...
if exist "Temp" (
    REM ¼ÆËãÁÙÊ±ÎÄ¼ş×Ü´óĞ¡
    for /f "tokens=1,2 delims= " %%a in ('powershell -Command "$sum=(Get-ChildItem 'Temp' -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; if ($sum -eq $null) { $sum = 0 }; if ($sum -ge 1GB) { '{0:N2} GB' -f ($sum / 1GB) } elseif ($sum -ge 1MB) { '{0:N2} MB' -f ($sum / 1MB) } else { '{0:N2} KB' -f ($sum / 1KB) }"') do (
        set "size_val=%%a"
        set "size_unit=%%b"
    )

    echo ¼ì²âµ½ÁÙÊ±Ä¿Â¼£º%cd%\Temp
    REM Ìí¼ÓÄ¬ÈÏÖµ´¦Àí
    if not defined size_val set "size_val=0.00"
    if not defined size_unit set "size_unit=KB"
    echo %green%ÁÙÊ±ÎÄ¼ş×Ü´óĞ¡£º%normal%!size_val! !size_unit!
    set /p "del_temp=%yellow%ÊÇ·ñÉ¾³ıÁÙÊ±ÎÄ¼ş£¿(y/n) %normal%"
    if /i "!del_temp!"=="y" (
        .\.conda\python.exe -c "from utils.clean_utils import clean_temp; clean_temp()"
        echo %green%ÒÑÇåÀíÁÙÊ±ÎÄ¼ş%normal%
    ) else (
        echo %yellow%ÒÑÌø¹ıÁÙÊ±ÎÄ¼şÇåÀí%normal%
    )
) else (
    echo %red%Î´ÕÒµ½ÁÙÊ±Ä¿Â¼ Temp%normal%
)

pause