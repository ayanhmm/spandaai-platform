@echo off
echo Starting AFE Component Services...
echo ================================

echo.
echo Choose Model Inference Type:
echo 1. GPU-based inference (Recommended for better performance)
echo 2. CPU-based inference (For systems without GPU)
echo.
set /p INFERENCE_CHOICE=Enter your choice (1 or 2): 

if "%INFERENCE_CHOICE%"=="1" (
    set INFERENCE_TYPE=GPU
    set COMPOSE_FILE=docker-compose-ollama-gpu.yml
    set OLLAMA_CONTAINER=ollama-platform-gpu
    set EDTECH_COMPOSE_FILE=docker-compose-lecture-video-analysis-gpu.yml
    echo Selected: GPU-based inference
) else if "%INFERENCE_CHOICE%"=="2" (
    set INFERENCE_TYPE=CPU
    set COMPOSE_FILE=docker-compose-ollama-cpu.yml
    set OLLAMA_CONTAINER=ollama-platform-cpu
    set EDTECH_COMPOSE_FILE=docker-compose-lecture-video-analysis.yml
    echo Selected: CPU-based inference
) else (
    echo Invalid choice. Defaulting to GPU-based inference.
    set INFERENCE_TYPE=GPU
    set COMPOSE_FILE=docker-compose-ollama-gpu.yml
    set OLLAMA_CONTAINER=ollama-platform-gpu
    set EDTECH_COMPOSE_FILE=docker-compose-lecture-video-analysis-gpu.yml
)

echo.
echo Configuration Setup...
echo ----------------------
echo For the services to work properly, we need your Hugging Face token.
echo You can get one from: https://huggingface.co/settings/tokens
echo.
set /p HF_TOKEN=Enter your Hugging Face token: 

if "%HF_TOKEN%"=="" (
    echo Warning: No Hugging Face token provided. Some services may not work properly.
    echo You can add it later to the .env files manually.
    set HF_TOKEN=put-your-hf-token-here
)

echo.
pause

REM Get the current directory (should be profile-scripts)
set PROFILE_SCRIPTS_DIR=%~dp0
echo Component Scripts Directory: %PROFILE_SCRIPTS_DIR%

REM Navigate to the repository root (one level up from profile-scripts)
cd /d "%PROFILE_SCRIPTS_DIR%.."
set REPO_ROOT=%CD%
echo Repository Root: %REPO_ROOT%

echo.
echo Setting up configuration files...
echo ---------------------------------

REM Function to create .env from env.example and add HF token
call :setup_env_file "%REPO_ROOT%\foundation\data_management\Setup\DataStorage"
call :setup_env_file "%REPO_ROOT%\domains\EdTech\lecture-analysis\docker"
call :setup_env_file "%REPO_ROOT%\solutions\EdTech\multimodal_afe_frontend\docker"

echo Configuration files setup complete!

echo.
echo Creating Docker Networks...
echo ---------------------------
docker network create dev-network 2>nul || echo Network dev-network already exists or created
docker network create Spanda-Net --driver bridge 2>nul || echo Network Spanda-Net already exists or created
docker network create platform_network 2>nul || echo Network platform_network already exists or created
docker network create app_network 2>nul || echo Network app_network already exists or created
echo Docker networks created/verified successfully

echo.
echo Starting Spanda.AI Data Storage...
echo ----------------------------------
cd /d "%REPO_ROOT%\foundation\data_management\Setup\DataStorage"
docker compose -f Data-Storage.yml up -d
if %ERRORLEVEL% EQU 0 (
    echo Spanda.AI Data Storage started successfully
) else (
    echo Error starting Spanda.AI Data Storage
    pause
    exit /b 1
)

echo.
echo Starting Spanda.AI Inference Engine - on device (%INFERENCE_TYPE%)...
echo --------------------------------------------------
echo Note: Other inference options exist for production - check /foundation/inference directory
cd /d "%REPO_ROOT%\foundation\inference\cpu-optimized-gguf"
docker compose -f %COMPOSE_FILE% up -d
if %ERRORLEVEL% EQU 0 (
    echo Spanda.AI Inference Engine started successfully
    
    echo.
    echo Waiting for Ollama container to be ready...
    timeout /t 10 /nobreak
    
    echo Pulling gemma3:4b model...
    echo ---------------------------
    docker exec -it %OLLAMA_CONTAINER% ollama pull gemma3:4b
    if %ERRORLEVEL% EQU 0 (
        echo gemma3:4b model pulled successfully
    ) else (
        echo Warning: Failed to pull gemma3:4b model. You may need to pull it manually later.
        echo Command: docker exec -it %OLLAMA_CONTAINER% ollama pull gemma3:4b
    )
) else (
    echo Error starting Spanda.AI Inference Engine
    pause
    exit /b 1
)

echo.
echo Starting Spanda.AI EdTech domain - %INFERENCE_TYPE% version...
echo --------------------------------------------------
cd /d "%REPO_ROOT%\domains\EdTech\lecture-analysis\docker"
docker compose -f %EDTECH_COMPOSE_FILE% up -d
if %ERRORLEVEL% EQU 0 (
    echo Spanda.AI EdTech domain backend started successfully
) else (
    echo Error starting Spanda.AI EdTech domain backend
    pause
    exit /b 1
)

echo.
echo Starting Spanda.AI Multi-modal Lecture Content and Delivery Analysis...
echo -----------------------------------------------------------------------
cd /d "%REPO_ROOT%\solutions\EdTech\multimodal_afe_frontend\docker"
docker compose -f docker-compose-images.yml up -d
if %ERRORLEVEL% EQU 0 (
    echo Spanda.AI Multi-modal Frontend started successfully
) else (
    echo Error starting Spanda.AI Multi-modal Frontend
    pause
    exit /b 1
)

echo.
echo Waiting for services to be ready...
timeout /t 30 /nobreak
echo ========================================
echo All AFE Component Services Started Successfully!
echo ========================================
echo.
echo Services started in detached mode:
echo 1. Docker Networks Created
echo 2. Configuration files (.env) created/updated with your HF token
echo 3. Spanda.AI Data Storage
echo 4. Spanda.AI Inference Engine - on device (%INFERENCE_TYPE%)
echo    * Other inference options available in /foundation/inference
echo    * gemma3:4b model pulled and ready
echo 5. Spanda.AI EdTech domain - %INFERENCE_TYPE% version
echo 6. Spanda.AI Multi-modal Lecture Content and Delivery Analysis
echo.
echo All services are running in the background.
echo Use 'docker-compose down' in respective directories to stop services.
echo Use 'docker ps' to view running containers.
echo.
echo AFE Component Services deployment complete!
echo Go to http://localhost:3001/multimodal to try out the application! Note that wait times will be long depending on Hardware.
echo.
pause
goto :eof

REM Function to setup .env file from env.example
:setup_env_file
set TARGET_DIR=%~1
echo Setting up .env in: %TARGET_DIR%

if not exist "%TARGET_DIR%" (
    echo Warning: Directory %TARGET_DIR% does not exist. Skipping...
    goto :eof
)

cd /d "%TARGET_DIR%"

if exist "env.example" (
    if not exist ".env" (
        echo Creating .env from env.example...
        copy "env.example" ".env" >nul
        echo .env created from env.example
    ) else (
        echo .env already exists, checking for HF token...
    )
    
    REM Add or update Hugging Face token in .env
    echo. >> ".env"
    echo # External Services >> ".env"
    echo HUGGINGFACE_TOKEN=%HF_TOKEN% >> ".env"
    echo Added/Updated Hugging Face token in .env
) else (
    if not exist ".env" (
        echo No env.example found, creating basic .env with HF token...
        echo # External Services > ".env"
        echo HUGGINGFACE_TOKEN=%HF_TOKEN% >> ".env"
        echo Created basic .env with HF token
    ) else (
        echo .env exists but no env.example found, adding HF token...
        echo. >> ".env"
        echo # External Services >> ".env"
        echo HUGGINGFACE_TOKEN=%HF_TOKEN% >> ".env"
        echo Added HF token to existing .env
    )
)
goto :eof