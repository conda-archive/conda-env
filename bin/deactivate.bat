@echo off
setlocal

if not "%1" == "--help" goto skipusage
    (
    echo Usage: deactivate
    echo.
    echo Deactivates previously activated Conda
    echo environment.
    echo.
    echo Additional arguments are ignored.
    ) 1>&2
    exit /b 1
:skipusage

SET "CONDA_EXE=%~dp0\\conda.bat"

REM Use conda itself to figure things out
:runcondasecretcommand
REM activate conda root environment
FOR /F "delims=" %%i IN ('call "%CONDA_EXE%" ..deactivate') DO set PATH=%%i

:resetprompt
set PROMPT=%CONDA_OLD_PS1%

endlocal & set PROMPT=%PROMPT%& set PATH=%PATH%& set CONDA_ACTIVE_ENV=& set CONDA_OLD_PS1=
