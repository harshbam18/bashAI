@echo off
echo === Pulling LLaMA 2 model with Ollama ===
ollama pull llama2

if %errorlevel% neq 0 (
    echo Failed to pull llama2 model. Make sure Ollama is installed and running.
    pause
    exit /b %errorlevel%
)

echo === Installing Python dependencies ===
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install Python requirements. Check for errors above.
    pause
    exit /b %errorlevel%
)

echo === Setup complete ===
pause
