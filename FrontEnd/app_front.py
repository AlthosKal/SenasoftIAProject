#!/usr/bin/env python3
"""
MedicoIA - Servidor Frontend
Servidor Flask para servir la aplicación HTML + TailwindCSS + HTMX sin JavaScript
"""

from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import os
import webbrowser
import threading
import time
import signal
import sys
import requests
from datetime import datetime
import base64
import json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear instancia de Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'medicoIA-secret-key-2025')

# Configuración
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Verificar si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página principal"""
    return render_template_string(open('index.html', 'r', encoding='utf-8').read())

@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    """Cerrar servidor"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return 'Not running with the Werkzeug Server'
    func()
    return 'Servidor cerrado'

@app.route('/api/chat', methods=['POST'])
def send_message():
    """Enviar mensaje al backend y recibir respuesta"""
    try:
        message = request.form.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Enviar al backend
        backend_response = requests.post(
            f'{BACKEND_URL}/chat',
            json={'message': message},
            timeout=30
        )
        
        if backend_response.status_code == 200:
            result = backend_response.json()
            # Guardar conversación en sesión
            if 'conversation_id' not in session:
                session['conversation_id'] = result.get('conversation_id')
            
            # Agregar mensaje a historial de sesión
            if 'chat_history' not in session:
                session['chat_history'] = []
            
            session['chat_history'].append({
                'user_message': message,
                'assistant_response': result.get('diagnosis', result.get('response', '')),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'confidence': result.get('confidence'),
                'recommendations': result.get('recommendations', [])
            })
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Error del backend'}), 500
            
    except requests.exceptions.RequestException:
        return jsonify({'error': 'No se puede conectar con el backend'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """Analizar imagen médica"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No se encontró archivo de imagen'}), 400
        
        file = request.files['image']
        message = request.form.get('message', 'Analizar imagen médica')
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Enviar al backend
            with open(filepath, 'rb') as f:
                files = {'image': f}
                data = {'message': message}
                backend_response = requests.post(
                    f'{BACKEND_URL}/analyze-image',
                    files=files,
                    data=data,
                    timeout=60
                )
            
            # Limpiar archivo temporal
            os.remove(filepath)
            
            if backend_response.status_code == 200:
                result = backend_response.json()
                
                # Guardar en historial
                if 'chat_history' not in session:
                    session['chat_history'] = []
                
                session['chat_history'].append({
                    'user_message': f'🖼️ **Imagen médica enviada**\n**Descripción:** {message}',
                    'assistant_response': result.get('diagnosis', result.get('response', '')),
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'confidence': result.get('confidence'),
                    'recommendations': result.get('recommendations', []),
                    'is_image_analysis': True
                })
                
                return jsonify(result)
            else:
                return jsonify({'error': 'Error al analizar imagen en backend'}), 500
        else:
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    """Limpiar historial del chat"""
    session.pop('chat_history', None)
    session.pop('conversation_id', None)
    return jsonify({'status': 'success', 'message': 'Chat limpiado'})

@app.route('/api/get-history')
def get_history():
    """Obtener historial de conversaciones"""
    try:
        # Intentar obtener historial del backend
        backend_response = requests.get(f'{BACKEND_URL}/history', timeout=10)
        if backend_response.status_code == 200:
            return jsonify(backend_response.json())
        else:
            return jsonify({'conversations': []})
    except:
        return jsonify({'conversations': []})

@app.route('/api/chat-history')
def get_chat_history():
    """Obtener historial de la sesión actual"""
    return jsonify({
        'history': session.get('chat_history', []),
        'conversation_id': session.get('conversation_id')
    })

@app.route('/components/chat-messages')
def chat_messages_component():
    """Componente de mensajes del chat"""
    history = session.get('chat_history', [])
    
    if not history:
        return '''
        <div class="flex items-start space-x-3 animate-fade-in">
            <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-medical-500 rounded-full flex items-center justify-center text-white">
                    <i class="fas fa-robot"></i>
                </div>
            </div>
            <div class="message-bubble bg-white rounded-2xl rounded-tl-sm p-4 shadow-md border border-gray-200">
                <div class="text-sm text-gray-900">
                    <div class="font-medium text-medical-600 mb-2">¡Hola! Soy tu asistente médico inteligente</div>
                    <p>Puedes:</p>
                    <ul class="list-disc list-inside mt-2 space-y-1 text-gray-700">
                        <li><strong>Describir síntomas</strong> del paciente en texto libre</li>
                        <li><strong>Subir imágenes médicas</strong> (rayos X, resonancias, etc.)</li>
                        <li><strong>Consultar el historial</strong> de diagnósticos anteriores</li>
                    </ul>
                    <div class="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <p class="text-xs text-yellow-800">
                            <i class="fas fa-exclamation-triangle mr-1"></i>
                            <strong>Importante:</strong> Este es un sistema de asistencia que debe ser validado por un profesional médico.
                        </p>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    messages_html = ""
    for msg in history:
        is_image = msg.get('is_image_analysis', False)
        confidence = msg.get('confidence')
        recommendations = msg.get('recommendations', [])
        
        # Mensaje del usuario
        messages_html += f'''
        <div class="flex justify-end space-x-3 animate-slide-up">
            <div class="message-bubble bg-medical-500 text-white rounded-2xl rounded-br-sm p-4 shadow-md max-w-xl">
                <div class="text-sm">
                    <div class="message-content whitespace-pre-wrap">{msg['user_message']}</div>
                </div>
                <div class="text-xs text-blue-100 mt-2">{msg['timestamp']}</div>
            </div>
            <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white">
                <i class="fas fa-user-md"></i>
            </div>
        </div>
        '''
        
        # Generar HTML de confianza
        confidence_html = ""
        if confidence:
            confidence_pct = round(confidence * 100)
            confidence_color = 'success' if confidence_pct >= 80 else 'warning' if confidence_pct >= 60 else 'danger'
            confidence_icon = 'check-circle' if confidence_pct >= 80 else 'exclamation-triangle' if confidence_pct >= 60 else 'times-circle'
            
            confidence_html = f'''
            <div class="mt-3 p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">Nivel de Confianza</span>
                    <div class="flex items-center">
                        <i class="fas fa-{confidence_icon} text-{confidence_color}-500 mr-1"></i>
                        <span class="text-sm font-bold text-{confidence_color}-600">{confidence_pct}%</span>
                    </div>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill bg-{confidence_color}-500" style="width: {confidence_pct}%"></div>
                </div>
            </div>
            '''
        
        # Generar HTML de recomendaciones
        recommendations_html = ""
        if recommendations:
            rec_items = ''.join([f'<li class="text-sm text-blue-800">• {rec}</li>' for rec in recommendations])
            recommendations_html = f'''
            <div class="mt-3 p-3 bg-blue-50 rounded-lg">
                <h4 class="text-sm font-medium text-blue-900 mb-2">
                    <i class="fas fa-pills mr-2"></i>Recomendaciones:
                </h4>
                <ul class="space-y-1">{rec_items}</ul>
            </div>
            '''
        
        # Mensaje del asistente
        analysis_icon = '<i class="fas fa-microscope text-medical-500 mr-2"></i>' if is_image else ''
        
        messages_html += f'''
        <div class="flex justify-start space-x-3 animate-slide-up">
            <div class="w-10 h-10 bg-medical-500 rounded-full flex items-center justify-center text-white">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-bubble bg-white rounded-2xl rounded-bl-sm p-4 shadow-md border border-gray-200 max-w-xl">
                <div class="text-sm">
                    <div class="font-medium text-medical-600 mb-1">{analysis_icon}Asistente Médico</div>
                    <div class="message-content whitespace-pre-wrap">{msg['assistant_response']}</div>
                    {confidence_html}
                    {recommendations_html}
                    <div class="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <p class="text-xs text-yellow-800">
                            <i class="fas fa-exclamation-triangle mr-1"></i>
                            <strong>Importante:</strong> Este diagnóstico debe ser validado por un profesional médico.
                        </p>
                    </div>
                </div>
                <div class="text-xs text-gray-500 mt-2">{msg['timestamp']}</div>
            </div>
        </div>
        '''
    
    return messages_html

@app.route('/components/notification')
def show_notification():
    """Mostrar notificación temporal"""
    message = request.args.get('message', '')
    type_notif = request.args.get('type', 'info')
    
    icons = {
        'success': 'check-circle',
        'error': 'times-circle', 
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    }
    
    colors = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning', 
        'info': 'medical'
    }
    
    return f'''
    <div id="notification" 
         class="fixed top-4 right-4 z-50 bg-white border-l-4 border-{colors[type_notif]}-500 rounded-lg shadow-lg p-4 max-w-sm animate-slide-up"
         hx-trigger="load delay:5s"
         hx-delete="/components/notification"
         hx-target="#notification"
         hx-swap="outerHTML">
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <i class="fas fa-{icons[type_notif]} text-{colors[type_notif]}-500"></i>
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">{message}</p>
            </div>
            <div class="ml-auto pl-3">
                <button hx-delete="/components/notification" 
                        hx-target="#notification" 
                        hx-swap="outerHTML"
                        class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    </div>
    '''

@app.route('/components/notification', methods=['DELETE'])
def hide_notification():
    """Ocultar notificación"""
    return ""

def check_backend_status():
    """Verificar si el backend Flask está disponible"""
    try:
        backend_url = os.getenv('BACKEND_URL', 'http://localhost:5000')
        timeout = int(os.getenv('REQUEST_TIMEOUT', '5'))
        response = requests.get(f'{backend_url}/', timeout=timeout)
        return response.status_code == 200
    except:
        return False

def open_browser():
    """Abrir navegador después de un breve delay"""
    if os.getenv('AUTO_OPEN_BROWSER', 'true').lower() == 'true':
        time.sleep(1.5)
        port = os.getenv('FRONTEND_PORT', '7860')
        webbrowser.open(f'http://localhost:{port}')

def get_local_ip():
    """Obtener IP local para acceso desde la red"""
    try:
        # Conectar a un servidor externo para obtener la IP local
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"

def main():
    """Función principal del servidor Flask"""
    PORT = int(os.getenv('FRONTEND_PORT', '7860'))
    HOST = os.getenv('FRONTEND_HOST', '0.0.0.0')
    
    print("🏥 MedicoIA - Frontend Server (Flask)")
    print("=" * 50)
    print(f"🚀 Iniciando servidor Flask en puerto {PORT}")
    print(f"📂 Directorio: {os.path.dirname(os.path.abspath(__file__))}")
    print()
    print("🌐 URLs de acceso:")
    print(f"   Local:    http://localhost:{PORT}")
    print(f"   Red:      http://{get_local_ip()}:{PORT}")
    print()
    print("⚡ Características del frontend:")
    print("   ✓ Flask + HTML + TailwindCSS + HTMX")
    print("   ✓ Sin dependencias de JavaScript")
    print("   ✓ Diseño médico profesional")
    print("   ✓ Responsive y optimizado")
    print("   ✓ Análisis de imágenes médicas")
    print("   ✓ Chat inteligente")
    print()
    print("🔧 Para detener: Ctrl+C")
    print("=" * 50)
    
    # Abrir navegador en hilo separado
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        app.run(host=HOST, port=PORT, debug=False)
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}")
        print("💡 Verifica que el puerto 7860 esté disponible")

if __name__ == "__main__":
    main()