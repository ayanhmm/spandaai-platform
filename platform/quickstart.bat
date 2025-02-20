@echo off
setlocal enabledelayedexpansion


:: Save the repository's root directory.
set "ROOT_DIR=%cd%"

:: Ensure required Docker networks exist.
echo 🌐 Ensuring required Docker networks exist...
docker network inspect platform_network >nul 2>&1 || docker network create platform_network
docker network inspect app_network >nul 2>&1 || docker network create app_network

:: ====================================================================
:: 1. Process Docker Compose files in the root directory.
:: ====================================================================
echo 📂 Processing Docker Compose files in the root directory...
for %%f in (docker-compose*.yml) do (
    if exist "%%f" (
        set "file=%%~nxf"
        set "friendly_name=!file:docker-compose-=!"
        set "friendly_name=!friendly_name:.yml=!"
        :prompt1
        set /p yn=Do you want to run '!friendly_name!'? (y/n): 
        if /i "!yn!"=="y" (
            if "!friendly_name!"=="vllm" (
                set /p vllm_command=Enter command for vllm: 
                echo 🚀 Running !friendly_name! with command "!vllm_command!"...
                set "COMMAND=!vllm_command!"
                docker compose -f "%%f" up -d
            ) else (
                echo 🚀 Running !friendly_name!...
                docker compose -f "%%f" up -d
            )
        ) else if /i "!yn!"=="n" (
            echo ⏩ Skipping !friendly_name!.
        ) else (
            echo Please answer yes (y) or no (n).
            goto :prompt1
        )
    )
)

:: ====================================================================
:: 2. Process each subdirectory containing Docker Compose files.
:: ====================================================================

for /f "delims=" %%d in ('forfiles /s /m "docker-compose*.yml" /c "cmd /c echo @path" 2^>nul') do (
    set "dir_path=%%~pd"
    if "!dir_path!"=="%ROOT_DIR%\" (
        rem Skip the root directory since it was already processed.
        goto :continue
    )

    echo 📂 Entering directory: !dir_path!
    pushd "!dir_path!" >nul

    for %%f in (docker-compose*.yml) do (
        if exist "%%f" (
            set "file=%%~nxf"
            set "friendly_name=!file:docker-compose-=!"
            set "friendly_name=!friendly_name:.yml=!"
            :prompt2
            set /p yn=Do you want to run '!friendly_name!' in directory '!dir_path!'? (y/n): 
            if /i "!yn!"=="y" (
                if "!friendly_name!"=="vllm" (
                    set /p vllm_command=Enter command for vllm: 
                    echo 🚀 Running !friendly_name! in !dir_path! with command "!vllm_command!"...
                    set "COMMAND=!vllm_command!"
                    docker compose -f "%%f" up -d
                ) else (
                    echo 🚀 Running !friendly_name! in !dir_path!...
                    docker compose -f "%%f" up -d
                )
            ) else if /i "!yn!"=="n" (
                echo ⏩ Skipping !friendly_name!.
            ) else (
                echo Please answer yes (y) or no (n).
                goto :prompt2
            )
        )
    )
    popd >nul
    :continue
)

:: Give services some time to start.
echo ⏳ Waiting for services to stabilize...
timeout /t 10 >nul

echo 🎉 Deployment complete! All services are now running.
echo(
echo 📝 Access points:
echo - Grafana: http://localhost:3000 (username: admin / password: admin)
echo - Prometheus: http://localhost:9090
echo - AlertManager: http://localhost:9093
echo - Kafka: http://localhost:9092
echo - Redis: http://localhost:6379
echo - MySQL: http://localhost:3306
echo - Ollama: http://localhost:11434
echo - Verba: http://localhost:8000
