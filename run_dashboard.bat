@echo off
echo ========================================
echo   Colombia Economic Insights Dashboard
echo ========================================
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo Entorno virtual no encontrado. Creando uno nuevo...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Instalando dependencias...
    pip install -r requirements.txt
)

echo.
echo Iniciando Streamlit dashboard...
echo Accede a: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

streamlit run app.py

pause