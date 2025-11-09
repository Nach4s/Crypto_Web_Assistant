@echo off
echo Starting Crypto Chat Assistant Frontend...
echo.

cd frontend

if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo.
echo Starting Vite dev server on http://localhost:3000
echo.
call npm run dev

pause
