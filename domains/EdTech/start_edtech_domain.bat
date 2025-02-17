@echo off
set /p mode="Do you want to run the services using Docker or locally? (Enter 'docker' or 'local'): "

if /i "%mode%"=="docker" (
    echo Starting EdTech services with Docker...
    
    REM Run first docker-compose in the background
    start cmd /k "docker compose up -d"

    echo All services have been started in the background!
    
    REM Start API Gateway in foreground
    cd api_gateway
    docker compose up
    exit /b
)

if /i "%mode%"=="local" (
    echo Starting EdTech services locally...
    
    REM Start services in separate terminals
    start cmd /k "cd data_preprocessing && python api.py"
    start cmd /k "cd document_analysis && python api.py"
    start cmd /k "cd edu_ai_agents && python api.py"
    start cmd /k "cd qa_generation && python api.py"
    start cmd /k "cd face_analysis && python api.py"

    echo All services have been started!
    
    REM Start API Gateway in foreground
    cd api_gateway
    docker compose up
    exit /b
)

echo Invalid option. Please enter 'docker' or 'local'.
exit /b 1
