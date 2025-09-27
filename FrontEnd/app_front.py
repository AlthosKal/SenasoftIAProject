#!/usr/bin/env python3
"""
MedicoIA - Servidor Frontend
Servidor simple para servir la aplicación HTML + TailwindCSS + HTMX
"""

import http.server
import socketserver
import socket
import os
import webbrowser
import threading
import time
import signal
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class MedicoIAHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personalizado para servir la aplicación MedicoIA"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        """Manejar requests GET"""
        if self.path == '/':
            # Servir index.html como página principal
            self.path = '/index.html'
        elif self.path == '/shutdown':
            # Manejar señal de cierre desde el navegador
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Cerrando servidor...')
            # Cerrar servidor en hilo separado para evitar bloqueos
            threading.Thread(target=self._shutdown_server).start()
            return
        
        # Agregar headers CORS para desarrollo
        super().do_GET()
    
    def do_POST(self):
        """Manejar requests POST para shutdown"""
        if self.path == '/shutdown':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Cerrando servidor...')
            threading.Thread(target=self._shutdown_server).start()
        else:
            super().do_POST()
    
    def _shutdown_server(self):
        """Cerrar el servidor con delay para permitir respuesta"""
        time.sleep(0.5)
        if hasattr(self.server, '_shutdown_requested'):
            return  # Ya se solicitó el cierre
        self.server._shutdown_requested = True
        print("\n🔗 Cierre solicitado desde navegador")
        self.server.shutdown()
    
    def end_headers(self):
        """Agregar headers CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Personalizar logging"""
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}")

def check_backend_status():
    """Verificar si el backend Flask está disponible"""
    try:
        import requests
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

def signal_handler(sig, frame, httpd=None):
    """Manejar señales del sistema para cerrar el servidor correctamente"""
    print("\n" + "=" * 50)
    print("🛑 Cerrando servidor...")
    if httpd:
        httpd.shutdown()
        httpd.server_close()
        # Asegurar liberación del puerto
        time.sleep(0.5)
    print("✅ Servidor cerrado correctamente")
    print("👋 ¡Gracias por usar MedicoIA!")
    sys.exit(0)

def main():
    """Función principal del servidor"""
    PORT = int(os.getenv('FRONTEND_PORT', '7860'))
    HOST = os.getenv('FRONTEND_HOST', '0.0.0.0')
    BACKEND_PORT = os.getenv('BACKEND_PORT', '5000')
    
    print("🏥 MedicoIA - Frontend Server")
    print("=" * 50)
    print(f"🚀 Iniciando servidor en puerto {PORT}")
    print(f"📂 Directorio: {os.path.dirname(os.path.abspath(__file__))}")
    
    
    print()
    print("🌐 URLs de acceso:")
    print(f"   Local:    http://localhost:{PORT}")
    print(f"   Red:      http://{get_local_ip()}:{PORT}")
    print()
    print("⚡ Características del frontend:")
    print("   ✓ HTML + TailwindCSS + HTMX")
    print("   ✓ Diseño médico profesional")
    print("   ✓ Responsive y optimizado")
    print("   ✓ Análisis de imágenes médicas")
    print("   ✓ Chat inteligente")
    print()
    print("🔧 Para detener: Ctrl+C o cerrar navegador")
    print("🚪 El servidor se cerrará automáticamente al cerrar la pestaña")
    print("=" * 50)
    
    try:
        # Crear servidor con reuso de puerto
        httpd = socketserver.TCPServer((HOST, PORT), MedicoIAHTTPRequestHandler)
        httpd.allow_reuse_address = True
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Configurar manejo de señales para cierre automático
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, httpd))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, httpd))
        
        # Abrir navegador en hilo separado
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print(f"✅ Servidor iniciado exitosamente")
        print(f"🌐 Accede a: http://localhost:{PORT}")
        print()
        
        # Servir indefinidamente
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None, httpd if 'httpd' in locals() else None)
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}")
        print("💡 Verifica que el puerto 7860 esté disponible")
    finally:
        if 'httpd' in locals():
            httpd.server_close()

def get_local_ip():
    """Obtener IP local para acceso desde la red"""
    import socket
    try:
        # Conectar a un servidor externo para obtener la IP local
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"

if __name__ == "__main__":
    main()