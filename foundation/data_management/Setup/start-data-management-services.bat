@echo off
setlocal enabledelayedexpansion

REM Spanda AI Platform - Data Management Services Startup Script
REM This script starts all data management services in the correct order

echo [*] Starting Spanda AI Platform Data Management Services...
echo ==================================================

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo Starting services in dependency order...
echo.

REM 1. Start Data Storage (Database/Storage layer first)
echo [1] Starting Data Storage...
cd /d "%SCRIPT_DIR%DataStorage"
if exist "Data-Storage.yml" (
    echo     Running: docker-compose -f Data-Storage.yml up -d
    docker-compose -f Data-Storage.yml up -d
    if %errorlevel% equ 0 (
        echo     [OK] Data Storage containers started
    ) else (
        echo     [X] Failed to start Data Storage
    )
) else (
    echo     [!] Data-Storage.yml not found, skipping...
)
echo.

REM 2. Start Data Lake (Storage layer)
echo [2] Starting Data Lake...
cd /d "%SCRIPT_DIR%DataLake"
if exist "Data-Lake.yml" (
    echo     Running: docker-compose -f Data-Lake.yml up -d
    docker-compose -f Data-Lake.yml up -d
    if %errorlevel% equ 0 (
        echo     [OK] Data Lake containers started
    ) else (
        echo     [X] Failed to start Data Lake
    )
) else (
    echo     [!] Data-Lake.yml not found, skipping...
)
echo.

REM 3. Start Data Ingestion (Input layer)
echo [3] Starting Data Ingestion...
cd /d "%SCRIPT_DIR%DataIngestion"
if exist "Data-Ingestion.yml" (
    echo     Running: docker-compose -f Data-Ingestion.yml up -d
    docker-compose -f Data-Ingestion.yml up -d
    if %errorlevel% equ 0 (
        echo     [OK] Data Ingestion containers started
    ) else (
        echo     [X] Failed to start Data Ingestion
    )
) else (
    echo     [!] Data-Ingestion.yml not found, skipping...
)
echo.

REM 4. Start Data Processing (Processing layer)
echo [4] Starting Data Processing...
cd /d "%SCRIPT_DIR%DataProcessing"
if exist "Data-Processing.yml" (
    echo     Running: docker-compose -f Data-Processing.yml up -d
    docker-compose -f Data-Processing.yml up -d
    if %errorlevel% equ 0 (
        echo     [OK] Data Processing containers started
    ) else (
        echo     [X] Failed to start Data Processing
    )
) else (
    echo     [!] Data-Processing.yml not found, skipping...
)
echo.

REM 5. Start Data Analytics (Analysis layer)
echo [5] Starting Data Analytics...
cd /d "%SCRIPT_DIR%DataAnalytics"
if exist "Data-Analytics.yml" (
    echo     Running: docker-compose -f Data-Analytics.yml up -d
    docker-compose -f Data-Analytics.yml up -d
    if %errorlevel% equ 0 (
        echo     [OK] Data Analytics containers started
    ) else (
        echo     [X] Failed to start Data Analytics
    )
) else (
    echo     [!] Data-Analytics.yml not found, skipping...
)
echo.

REM Return to original directory
cd /d "%SCRIPT_DIR%"

echo ==================================================
echo [*] All services startup completed!
echo.

REM Wait a moment for services to initialize
echo [~] Waiting 10 seconds for services to initialize...
timeout /t 10 /nobreak >nul

echo Checking service status...
echo ----------------------

echo.
echo [i] To view all running containers:
echo    docker ps
echo.
echo [i] To view service logs, use:
echo    docker-compose -f DataStorage\Data-Storage.yml logs -f
echo    docker-compose -f DataLake\Data-Lake.yml logs -f
echo    docker-compose -f DataIngestion\Data-Ingestion.yml logs -f
echo    docker-compose -f DataProcessing\Data-Processing.yml logs -f
echo    docker-compose -f DataAnalytics\Data-Analytics.yml logs -f
echo.
echo [i] To stop all services, use:
echo    docker-compose -f DataStorage\Data-Storage.yml down
echo    docker-compose -f DataLake\Data-Lake.yml down
echo    docker-compose -f DataIngestion\Data-Ingestion.yml down
echo    docker-compose -f DataProcessing\Data-Processing.yml down
echo    docker-compose -f DataAnalytics\Data-Analytics.yml down
echo.
echo [*] Spanda AI Platform - Data Management Layer startup complete!

pause