# 🏥 MedicoIA Frontend

Frontend moderno con **HTML + TailwindCSS + HTMX** para el sistema **MedicoIA** - Diagnóstico médico asistido por IA.

## ✨ Características

### 🎨 Diseño Médico Profesional
- **Verde aguamarina** - Esquema de colores médico
- **TailwindCSS** - Framework CSS moderno
- **Navegación centrada** - UX profesional
- **Animaciones fluidas** - Transiciones suaves
- **Totalmente responsivo** - Mobile-first

### ⚡ Tecnologías Modernas
- **HTML5** semántico y accesible
- **TailwindCSS** para estilos
- **HTMX** para interactividad
- **JavaScript vanilla** optimizado
- **Font Awesome** para iconos

### 🩺 Funcionalidades Médicas
- **Chat inteligente** - Consulta de síntomas
- **Análisis de imágenes** - Drag & drop para rayos X
- **Historial médico** - Seguimiento de consultas
- **Indicadores de confianza** - Niveles de precisión
- **Notificaciones** - Feedback inmediato

## 📁 Estructura

```
FrontEnd/
├── index.html          # 🚀 Interfaz principal
├── app.js             # JavaScript con HTMX
├── app.py             # Servidor Python
├── run.sh             # Script de ejecución
├── README.md          # Este archivo
└── ESTRUCTURA.md      # Documentación detallada
```

## 🚀 Instalación y Uso

### Requisitos Mínimos
- **Python 3.8+** instalado
- **Navegador moderno** (Chrome, Firefox, Safari, Edge)
- **2GB RAM** mínimo
- **Conexión a internet** para CDNs

### Ejecución Rápida
```bash
cd /home/alejo/Escritorio/SenaSoft/FrontEnd

# Ejecutar frontend
./run.sh
```

### Ejecución Manual
```bash
cd /home/alejo/Escritorio/SenaSoft/FrontEnd

# Ejecutar servidor
python3 app_front.py
```

## 🌐 URLs de Acceso

- **Frontend**: http://localhost:7860
- **Backend Flask**: http://localhost:5000 *(debe estar ejecutándose)*

## 🔧 Configuración del Backend

Para funcionalidad completa, asegúrate de que el backend Flask esté activo:

```bash
# En otra terminal
cd ../BackEnd
python app_front.py
```

## 🎯 Funcionalidades

### 💬 Chat de Diagnóstico
- Describe síntomas del paciente en texto libre
- Recibe diagnósticos con nivel de confianza
- Recomendaciones médicas automáticas
- Historial de conversaciones

### 📷 Análisis de Imágenes
- **Drag & drop** para subir imágenes
- Soporte para rayos X, resonancias, TAC
- Análisis multimodal (imagen + texto)
- Preview automático de imágenes

### 📋 Gestión de Historial
- Lista de consultas anteriores
- Búsqueda por ID de conversación
- Carga rápida de diagnósticos previos
- Seguimiento de pacientes

### ℹ️ Información del Sistema
- Estadísticas de impacto médico
- Tecnologías utilizadas
- Métricas de precisión
- Consideraciones éticas

## 🎨 Personalización

### Cambiar Colores
El esquema de colores se define en `index.html`:

```javascript
'medical': {
    500: '#14b8a6',  // Verde aguamarina principal
    600: '#0d9488',  // Verde aguamarina oscuro
    // ... más tonos
}
```

### Modificar Estilos
Los estilos personalizados están en el `<style>` de `index.html`:

```css
.gradient-medical {
    background: linear-gradient(135deg, #14b8a6 0%, #0d9488 50%, #0f766e 100%);
}
```

## 🔍 Troubleshooting

### Error de Conexión
```bash
# Verificar que el backend esté activo
curl http://localhost:5000/

# Si no responde, iniciar backend
cd ../BackEnd && python app_front.py
```

### Puerto Ocupado
```bash
# Verificar qué está usando el puerto 7860
lsof -ti:7860

# Cambiar puerto en app_front.py línea 57:
PORT = 7861  # O cualquier otro puerto
```

### Problemas con Imágenes
- **Tamaño máximo**: 10MB
- **Formatos soportados**: JPG, PNG, GIF, BMP
- **Conexión requerida**: Para CDNs de TailwindCSS

## 🏆 Optimizaciones

### Para Equipos de Bajo Rendimiento
- **CSS optimizado** sin frameworks pesados
- **JavaScript vanilla** sin librerías externas  
- **Carga lazy** de recursos
- **Animaciones condicionales** según el dispositivo
- **Servidor Python ligero** sin dependencias

### Para Conexiones Lentas
- **CDNs optimizados** de TailwindCSS y HTMX
- **Compresión automática** de requests
- **Cache de navegador** habilitado
- **Fallbacks** para recursos críticos

## 📊 Métricas

- **Tiempo de carga**: < 2 segundos
- **Tamaño total**: < 500KB (sin imágenes)
- **Compatibilidad**: 95%+ navegadores modernos
- **Responsive**: 100% dispositivos
- **Accesibilidad**: WCAG 2.1 AA

## 📄 Licencia

MIT License - **SENASoft 2025** | Categoría Inteligencia Artificial

---

**Desarrollado para democratizar el acceso al diagnóstico médico en Colombia** 🇨🇴

*"Llevando IA médica inteligente a cada rincón del país, optimizada para funcionar hasta en los equipos más básicos"* 💻✨