@echo off
REM start_services.bat
echo Starting EdTech Microservices...

REM Start Data Preprocessing Service
start cmd /k "cd spanda_domains\services\EdTech\microservices\data_preprocessing && python api.py"

REM Start Document Analysis Service
start cmd /k "cd spanda_domains\services\EdTech\microservices\document_analysis && python api.py"

REM Start Edu AI Agents Service
start cmd /k "cd spanda_domains\services\EdTech\microservices\edu_ai_agents && python api.py"

REM Start QA generation Service
start cmd /k "cd spanda_domains\services\EdTech\microservices\qa_generation && python api.py"

REM Start API Gateway
start cmd /k "cd spanda_domains\api_gateway && python main.py"

echo All services have been started!