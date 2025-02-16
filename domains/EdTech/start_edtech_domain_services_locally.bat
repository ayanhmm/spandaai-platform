@echo off
echo Starting EdTech services...

REM Start Data Preprocessing Service
start cmd /k "cd data_preprocessing && python api.py"

REM Start Document Analysis Service
start cmd /k "cd document_analysis && python api.py"

REM Start Edu AI Agents Service
start cmd /k "cd edu_ai_agents && python api.py"

REM Start QA Generation Service
start cmd /k "cd qa_generation && python api.py"

echo All services have been started!

REM Navigate to api_gateway and start Docker Compose
cd api_gateway
docker-compose up
