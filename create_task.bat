@echo off
echo ==============================================
echo      股票分析每日定时任务创建脚本
echo ==============================================
echo.

set "SCRIPT_PATH=%~dp0daily_analyze_stock.py"
set "PYTHON_PATH=C:\Python311\python.exe"  REM 请修改为你的Python路径
set "TASK_NAME=每日股票分析"

echo 脚本路径: %SCRIPT_PATH%
echo Python路径: %PYTHON_PATH%
echo 任务名称: %TASK_NAME%
echo.

REM 创建任务计划
schtasks /create /tn "%TASK_NAME%" ^
    /tr "%PYTHON_PATH% \"%SCRIPT_PATH%\"" ^
    /sc daily ^
    /st 09:00 ^
    /sd %date:~0,4%-%date:~5,2%-%date:~8,2% ^
    /ru SYSTEM ^
    /f

if %errorlevel% equ 0 (
    echo.
    echo ✅ 任务创建成功！
    echo 📅 任务将在每天 09:00 自动执行
    echo 📁 报告将保存在 reports/ 目录下
    echo.
    echo 如需修改执行时间，请运行:
    echo   schtasks /change /tn "%TASK_NAME%" /st 新时间
    echo.
    echo 如需删除任务，请运行:
    echo   schtasks /delete /tn "%TASK_NAME%" /f
) else (
    echo ❌ 任务创建失败，请检查路径是否正确
    pause
)

echo.
echo ==============================================
pause