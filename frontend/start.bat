@echo off
echo 🚀 Iniciando PS Model Comparator - Frontend
echo ===========================================

REM Verificar si Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js no está instalado. Por favor instala Node.js 16+ primero.
    pause
    exit /b 1
)

REM Verificar si las dependencias están instaladas
if not exist "node_modules" (
    echo 📦 Instalando dependencias...
    npm install
)

echo 🔧 Configuración:
echo    - Frontend: http://localhost:5173
echo    - Backend API: http://localhost:8000
echo.
echo ⚡ Asegúrate de que el backend esté ejecutándose en el puerto 8000
echo.

REM Iniciar servidor de desarrollo
npm run dev
