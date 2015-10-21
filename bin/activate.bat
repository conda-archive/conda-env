@echo on
SETLOCAL ENABLEDELAYEDEXPANSION

SET ARGS_COUNT=0
FOR %%A in (%*) DO SET /A ARGS_COUNT+=1

IF %ARGS_COUNT% GTR 1 CALL :usage & goto END
ENDLOCAL & (
    IF %ARGS_COUNT% EQU 0 (CALL :activate_root) else (CALL :activate_path_or_name %1)
)
goto END

REM Code below are subroutines called above

:usage
    echo.
    echo ERROR: Too many arguments provided
    echo    Activate takes 0 or 1 argument (the environment to be activated, by name or by path)
    echo.
    echo    Passing no arguments activates root environment.
    goto :EOF

:activate_root
    pushd %~dp0..\
    set CONDA_NEW_PATH=%CD%
    set CONDA_NEW_NAME=^<root^>
    popd
    CALL :deactivate_active_env
    CALL :set_paths
    goto :EOF

:activate_path_or_name
    set CONDA_NEW_NAME=%1
    if "%CONDA_NEW_NAME%" == "DEACTIVATE" (call :deactivate_active_env & goto deactivated)
    REM CONDA_NEW_NAME might be a path or simply and env name here.
    REM    if EXIST effectively checks if it is a path.  If both a path in CWD AND
    REM    an environment with a similar name exist, then the path in CWD takes
    REM    preference
    if EXIST %CONDA_NEW_NAME% (CALL :activate_path) else (CALL :activate_name)
    CALL :deactivate_active_env
    CALL :set_paths
    :deactivated
    goto :EOF

:activate_path
    if exist "%CONDA_NEW_NAME%\conda-meta" (
        set CONDA_NEW_PATH=%CONDA_NEW_NAME%
        REM set the name to be shown to be the last folder in the path
        for /F %%i in ("%CONDA_NEW_PATH%") do set CONDA_NEW_NAME=%%~ni
    ) else (
        echo Error: %CONDA_NEW_NAME% is not a valid conda installation directory. & goto END
    )
    goto :EOF

: activate_name
    REM Check for CONDA_EVS_PATH environment variable
    REM It it doesn't exist, look inside the Anaconda install tree
    if NOT DEFINED CONDA_ENVS_PATH (
        pushd %~dp0..\
        set CONDA_ENVS_PATH=%CD%\envs
        popd
    )
    REM Search through paths in CONDA_ENVS_PATH
    REM First match will be the one used
    for %%F in ("%CONDA_ENVS_PATH:;=" "%") do (
        if exist "%%~F\%CONDA_NEW_NAME%\conda-meta" (
        set CONDA_NEW_PATH=%%~F\%CONDA_NEW_NAME%
        )
    )
    IF NOT DEFINED CONDA_NEW_PATH echo Error: Did not find env named %CONDA_NEW_NAME% in %CONDA_ENVS_PATH% & goto END
    goto :EOF

:set_active_path
    set CONDACTIVATE_PATH=%CONDA_ACTIVE_ENV%;%CONDA_ACTIVE_ENV%\Scripts;%CONDA_ACTIVE_ENV%\Library\bin;
    goto :EOF

:deactivate_active_env
    if NOT DEFINED CONDA_ACTIVE_ENV goto not_active
    echo Deactivating environment "%CONDA_ACTIVE_ENV%"...

    REM Run any deactivate scripts
    if not exist "%CONDA_ACTIVE_ENV%\etc\conda\deactivate.d" goto nodeactivate
        pushd "%CONDA_ACTIVE_ENV%\etc\conda\deactivate.d"
        for %%g in (*.bat) do call "%%g"
        popd
    :nodeactivate

    REM This search/replace removes the previous env from the path
    call :set_active_path
    echo %PATH%
    call set PATH=%%PATH:%CONDACTIVATE_PATH%=%%
    echo %PATH%
    set CONDA_ACTIVE_ENV=
    set CONDACTIVATE_PATH=
    set PROMPT=%CONDA_OLD_PROMPT%
    set CONDA_OLD_PROMPT=
    :not_active
    goto :EOF

:set_paths
    set CONDA_ACTIVE_ENV=%CONDA_NEW_PATH%
    echo Activating environment "%CONDA_NEW_NAME%"...
    call :set_active_path
    set PATH=%CONDACTIVATE_PATH%%PATH%
    set "PROMPT=[%CONDA_NEW_NAME%] $P$G"

    REM Run any activate scripts
    if not exist "%CONDA_ACTIVE_ENV%\etc\conda\activate.d" goto noactivate
        pushd "%CONDA_ACTIVE_ENV%\etc\conda\activate.d"
        for %%g in (*.bat) do call "%%g"
        popd
    :noactivate
    goto :EOF

:END
