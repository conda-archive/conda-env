@echo off
setlocal

set CONDA_NEW_ENV=%~1

if "%2" == "" goto skiptoomanyargs
    (echo Error: did not expect more than one argument.) 1>&2
    exit /b 1
:skiptoomanyargs

if not "%1" == "" goto skipmissingarg
    :: Set env to root if no arg provided
    set CONDA_NEW_ENV=root
:skipmissingarg

REM Use conda itself to figure things out

SET "CONDA_EXE=%~dp0\\conda.exe"

REM TODO: will this work if Conda root env is not on PATH?

REM Run secret conda ..checkenv command
call "%CONDA_EXE%" ..checkenv %CONDA_NEW_ENV%
REM EQU 0 means 0 or above on Windows ;(
if %ERRORLEVEL% GTR 0 (
    exit /b 1
)

REM Deactivate a previous activation if it is live
FOR /F "delims=" %%i IN ('"%CONDA_EXE%" ..deactivate') DO set PATH=%%i
if %ERRORLEVEL% GTR 0 (
exit /b 1
)
REM Activate the new environment
FOR /F "delims=" %%i IN ('"%CONDA_EXE%" ..activate %CONDA_NEW_ENV%') DO set PATH=%%i
if %ERRORLEVEL% GTR 0 (
exit /b 1
)
for /F %%C IN ('"%CONDA_EXE%" ..changeps1') DO set CHANGEPS1=%%C
if "%CHANGEPS1%" == "1" set PROMPT=[%CONDA_NEW_ENV%] $P$G
if %ERRORLEVEL% GTR 0 (
exit /b 1
)
endlocal & set PROMPT=%PROMPT%& set PATH=%PATH%& set CONDA_ACTIVE_ENV=%CONDA_NEW_ENV%
