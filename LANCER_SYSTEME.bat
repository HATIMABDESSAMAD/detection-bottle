@echo off
title Lancement du Systeme RecyBot
echo.
echo  =============================================
echo   LANCEMENT DU SYSTEME RECYBOT
echo  =============================================
echo.

:: === 1. BACKEND NODE.JS ===
echo [1/2] Demarrage du Backend (port 5000)...
start "RecyBot - Backend" cmd /k "cd /d ""%~dp0bottle-buddy-bot\bottle-buddy-bot\backend"" && node server.js"

timeout /t 2 /nobreak >nul

:: === 2. FRONTEND VITE ===
echo [2/2] Demarrage du Frontend (port 8080)...
start "RecyBot - Frontend" cmd /k "cd /d ""%~dp0bottle-buddy-bot\bottle-buddy-bot"" && npm run dev"

echo.
echo  =============================================
echo   Tous les composants sont lances !
echo   Frontend : http://localhost:8080
echo   Backend  : http://localhost:5000
echo  =============================================
echo.
echo  Fermez cette fenetre quand vous voulez.
pause
