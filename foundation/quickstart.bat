@echo off
setlocal enabledelayedexpansion

REM Save the repository's root directory
set "ROOT_DIR=%cd%"

REM Ensure required Docker networks exist
echo Ensuring required Docker networks exist...
docker network inspect platform_network >nul 2>&1 || docker network create platform_network
docker network inspect app_network      >nul 2>&1 || docker network create app_network

REM ====================================================================
REM 1. Process Docker Compose files in the root directory
REM ====================================================================
echo Processing Docker Compose files in the root directory...
for %%f in (docker-compose*.yml) do (
    set "file=%%f"
    set "friendly_name=!file:docker-compose-=!"
    set "friendly_name=!friendly_name:.yml=!"
    
    if "%%f"=="docker-compose.yml" (
        set "friendly_name=base"
    )
    
    call :ask_deployment "!friendly_name!" "%%f" ""
)

REM ====================================================================
REM 2. Process each subdirectory containing Docker Compose files
REM ====================================================================

REM Create a temporary file to store processed directories to avoid duplicates
set "processed_dirs=%TEMP%\processed_dirs_%RANDOM%.txt"
type nul > "%processed_dirs%"

REM Find all docker-compose files
echo Searching for Docker Compose files in subdirectories...
for /r . %%F in (docker-compose*.yml) do (
    set "dir_path=%%~dpF"
    set "dir_path=!dir_path:~0,-1!"
    
    REM Skip the root directory as we already processed it
    if not "!dir_path!"=="%CD%" (
        REM Check if we've already processed this directory
        findstr /i /c:"!dir_path!" "%processed_dirs%" >nul
        if errorlevel 1 (
            echo Found compose file in: !dir_path!
            echo !dir_path!>> "%processed_dirs%"
            
            echo Entering directory: !dir_path!
            pushd "!dir_path!"
            
            REM Process each Docker Compose file in this directory
            for %%G in (docker-compose*.yml) do (
                set "file=%%G"
                set "friendly_name=!file:docker-compose-=!"
                set "friendly_name=!friendly_name:.yml=!"
                
                if "%%G"=="docker-compose.yml" (
                    set "friendly_name=base"
                )
                
                call :ask_deployment "!friendly_name!" "%%G" "!dir_path!"
            )
            
            popd
        )
    )
)

REM Delete temporary file
del "%processed_dirs%" 2>nul

REM Give services some time to start
echo Waiting for services to stabilize...
timeout /t 10 /nobreak > nul

echo Deployment complete! All services are now running.
echo.
echo Access points:
echo - Grafana: http://localhost:3000 (username: admin / password: admin)
echo - Prometheus: http://localhost:9090
echo - AlertManager: http://localhost:9093
echo - Kafka: http://localhost:9092
echo - Redis: http://localhost:6379
echo - MySQL: http://localhost:3306
echo - Ollama: http://localhost:11434
echo - Verba: http://localhost:8000
echo.

goto :eof

REM ====================================================================
REM Subroutine to ask about deploying a service
REM ====================================================================
:ask_deployment
setlocal
set "friendly_name=%~1"
set "filename=%~2"
set "directory=%~3"

if "%directory%"=="" (
    set "location_info="
) else (
    set "location_info= in directory '%directory%'"
)

:prompt_deploy
set yn=
set /p yn=Do you want to run '%friendly_name%'%location_info%? (y/n): 
if /i "%yn%"=="y" (
    if "%friendly_name%"=="vllm" (
        set vllm_command=
        set /p vllm_command=Enter command for vllm: 
        echo Running %friendly_name%%location_info% with command '%vllm_command%'...
        set "COMMAND=%vllm_command%" && docker compose -f "%filename%" up -d
    ) else (
        echo Running %friendly_name%%location_info%...
        docker compose -f "%filename%" up -d
    )
) else if /i "%yn%"=="n" (
    echo Skipping %friendly_name%.
) else (
    echo Please answer yes (y^) or no (n^).
    goto :prompt_deploy
)
endlocal
goto :eof