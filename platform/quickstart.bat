@echo off
setlocal enabledelayedexpansion

echo.
echo   _____                       _                  _____ 
echo  / ____|                     | |           /\   |_   _|
echo | (___  _ __   __ _ _ __   __| | __ _     /  \    | |  
echo  \___ \| '_ \ / _` | '_ \ / _` |/ _` |   / /\ \   | |  
echo  ____) | |_) | (_| | | | | (_| | (_| |_ / ____ \ _| |_ 
echo |_____/| .__/ \__,_|_| |_|\__,_|\__,_(_)_/    \_\_____|
echo        | |                                             
echo        |_|                                             
echo.

rem Prompt user to choose between CPU or GPU setup
:chooseSetup
echo Choose your setup type:
echo 1. CPU
echo 2. GPU
set /p "SETUP_TYPE=Enter the number (1 or 2): "

if "%SETUP_TYPE%" == "1" (
    set "COMPOSE_FILE=docker-compose-cpu.yml"
    echo 🔧 Selected setup: CPU
) else if "%SETUP_TYPE%" == "2" (
    set "COMPOSE_FILE=docker-compose-gpu.yml"
    echo 🔧 Selected setup: GPU
) else (
    echo ❌ Invalid input! Please choose either 1 (CPU) or 2 (GPU).
    goto chooseSetup
)

rem Store the current directory path
set "ROOT_DIR=%cd%"

rem Create platform network if it doesn't exist
echo 🌐 Creating platform network if it doesn't exist...
docker network inspect platform_network >nul 2>&1 || docker network create platform_network

rem Create app network if it doesn't exist
echo 🌐 Creating app_network if it doesn't exist...
docker network inspect app_network >nul 2>&1 || docker network create app_network

rem Start main services with Docker Compose
echo 🚀 Starting main services with Docker Compose...
docker-compose -f %COMPOSE_FILE% up -d

rem Change to the dockprom directory
if exist "observability\dockprom" (
    cd observability\dockprom
) else (
    echo ❌ Error: dockprom directory not found!
    echo Creating dockprom directory...
    mkdir observability\dockprom
    cd observability\dockprom
)

rem Start monitoring services in dockprom
echo 🚀 Starting monitoring services in dockprom...
docker-compose up -d

rem Return to root directory
cd "%ROOT_DIR%"

rem Wait for services to be healthy
echo ⏳ Waiting for services to be healthy...
timeout /t 10 >nul

rem Check service status
echo ✨ Checking service status...
echo Main services:
docker-compose ps
echo.
echo Monitoring services:
cd observability\dockprom
docker-compose ps

echo 🎉 Deployment complete! All services are now running.
echo.
echo 📝 Access points:
echo - Grafana: http://localhost:3000 (username - admin / password - admin)
echo - Prometheus: http://localhost:9090
echo - AlertManager: http://localhost:9093
echo - Kafka: http://localhost:9092
echo - Redis: http://localhost:6379
echo - MySQL: http://localhost:3306
echo - Ollama: http://localhost:11434
echo - Verba: http://localhost:8000
pause
