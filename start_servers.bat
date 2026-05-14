@echo off
echo ===================================================
echo Starting Student Performance Evaluation System
echo ===================================================

echo.
echo Checking and Starting Backend Server...
cd backend
if not exist venv (
    echo Creating virtual environment for backend...
    python -m venv venv
    call .\venv\Scripts\activate.bat
    echo Installing backend dependencies...
    pip install -r requirements.txt
) else (
    call .\venv\Scripts\activate.bat
)
start "Backend Server" cmd /k "python app.py"
cd ..

echo.
echo Checking and Starting Frontend (UI) Server...
cd ui
if not exist venv (
    echo Creating virtual environment for frontend...
    python -m venv venv
    call .\venv\Scripts\activate.bat
    echo Installing frontend dependencies...
    pip install -r requirements.txt
) else (
    call .\venv\Scripts\activate.bat
)
start "Frontend Server" cmd /k "streamlit run streamlit_app.py"
cd ..

echo.
echo Setup Complete! 
echo Two terminal windows have been opened for the Background and Frontend.
echo A browser window should open automatically with the Streamlit app.
echo If it doesn't, navigate to http://localhost:8501 in your browser.
echo.
pause
