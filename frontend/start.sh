#!/bin/bash

echo "🚀 Iniciando PS Model Comparator - Frontend"
echo "==========================================="

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instala Node.js 16+ primero."
    exit 1
fi

# Verificar si las dependencias están instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

echo "🔧 Configuración:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo ""
echo "⚡ Asegúrate de que el backend esté ejecutándose en el puerto 8000"
echo ""

# Iniciar servidor de desarrollo
npm run dev
