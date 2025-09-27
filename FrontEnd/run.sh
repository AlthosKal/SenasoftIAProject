#!/bin/bash
# Script para ejecutar MedicoIA Frontend Moderno
# HTML + TailwindCSS + HTMX

echo "🏥 MedicoIA - Frontend Moderno"
echo "HTML + TailwindCSS + HTMX"
echo "================================="

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    exit 1
fi

# Verificar que estamos en el directorio correcto
if [ ! -f "index.html" ]; then
    echo "❌ Error: No se encuentra index.html"
    echo "   Ejecuta este script desde el directorio FrontEnd"
    exit 1
fi

# Verificar que el backend Flask está corriendo
echo "🔍 Verificando backend Flask..."
if curl -s "http://localhost:5000/" > /dev/null; then
    echo "✅ Backend Flask conectado en puerto 5000"
else
    echo "⚠️  ADVERTENCIA: Backend Flask no está disponible"
    echo "   Para funcionalidad completa:"
    echo "   cd ../BackEnd && python app.py"
    echo ""
    echo "   Continuando con frontend..."
fi

# Instalar requests si no está disponible (para verificar backend)
python3 -c "import requests" 2>/dev/null || pip install --break-system-packages requests

echo ""
echo "🚀 Iniciando servidor frontend..."
echo "   URL: http://localhost:7860"
echo "   Tecnologías: HTML + TailwindCSS + HTMX"
echo ""
echo "💡 Características:"
echo "   ✓ Diseño médico profesional"
echo "   ✓ Totalmente responsivo"
echo "   ✓ Análisis de imágenes drag & drop"
echo "   ✓ Chat en tiempo real"
echo "   ✓ Animaciones fluidas"
echo "   ✓ Optimizado para rendimiento"
echo ""

# Ejecutar servidor Python
python3 app_front.py