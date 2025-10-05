from flask import Blueprint, render_template, request, redirect, url_for
from service.chat_service_impl import ChatServiceImpl

# Create Blueprint for web views
web_bp = Blueprint('web', __name__)

# Initialize service
chat_service = ChatServiceImpl()


@web_bp.route('/')
def index():
    """
    Página principal del chatbot médico usando Jinja
    Renderiza index.html con historial de conversaciones
    """
    try:
        conversations = chat_service.get_user_conversations(limit=20)
        return render_template('index.html', conversations=conversations)
    except Exception as e:
        print(f"Error loading index: {e}")
        return render_template('index.html', conversations=[])


@web_bp.route('/chat', methods=['GET', 'POST'])
def chat_page():
    """
    Página de chat interactivo
    GET: Muestra la interfaz
    POST: Procesa mensaje y devuelve respuesta
    """
    if request.method == 'POST':
        # Procesar mensaje del formulario
        message = request.form.get('message', '')
        
        if message:
            try:
                # Obtener conversation_id si existe
                conversation_id = request.form.get('conversation_id', None)
                
                # Enviar a servicio de chat
                response = chat_service.send_text_message(message, conversation_id)
                
                # Obtener conversaciones para el sidebar
                conversations = chat_service.get_user_conversations(limit=20)
                
                # Renderizar con respuesta
                return render_template('index.html', 
                                     user_message=message,
                                     bot_response=response.get('response', ''),
                                     conversation_id=response.get('conversation_id', ''),
                                     conversations=conversations)
            except Exception as e:
                conversations = chat_service.get_user_conversations(limit=20)
                return render_template('index.html',
                                     error=f"Error procesando mensaje: {str(e)}",
                                     conversations=conversations)
    
    # GET - mostrar página con conversaciones
    try:
        conversations = chat_service.get_user_conversations(limit=20)
        return render_template('index.html', conversations=conversations)
    except Exception as e:
        return render_template('index.html', conversations=[], error=str(e))


@web_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    Manejo de subida de imágenes médicas
    """
    if 'image' not in request.files:
        return redirect(url_for('web.index'))
    
    file = request.files['image']
    message = request.form.get('message', '')
    
    if file.filename == '':
        return redirect(url_for('web.index'))
    
    try:
        # Leer imagen
        image_data = file.read()
        
        # Obtener conversation_id si existe
        conversation_id = request.form.get('conversation_id', None)
        
        # Procesar con servicio
        response = chat_service.analyze_image_with_text(image_data, message, conversation_id)
        
        # Obtener conversaciones para el sidebar
        conversations = chat_service.get_user_conversations(limit=20)
        
        # Renderizar con resultado
        return render_template('index.html',
                             user_message=f"[IMAGEN] {message}",
                             bot_response=response.get('response', ''),
                             image_analysis=response.get('image_analysis', {}),
                             conversation_id=response.get('conversation_id', ''),
                             conversations=conversations)
    
    except Exception as e:
        conversations = chat_service.get_user_conversations(limit=20)
        return render_template('index.html',
                             error=f"Error procesando imagen: {str(e)}",
                             conversations=conversations)


@web_bp.route('/conversation/<conversation_id>', methods=['GET', 'POST'])
def view_conversation(conversation_id):
    """
    Ver y continuar una conversación específica
    """
    if request.method == 'POST':
        # Continuar conversación existente
        message = request.form.get('message', '')
        
        if message:
            try:
                # Enviar mensaje usando el conversation_id existente
                response = chat_service.send_text_message(message, conversation_id)
                
                # Obtener historial actualizado
                history = chat_service.get_conversation_history(conversation_id)
                conversations = chat_service.get_user_conversations(limit=20)
                
                # Renderizar con el nuevo mensaje y respuesta
                return render_template('index.html',
                                     conversation_history=history,
                                     user_message=message,
                                     bot_response=response.get('response', ''),
                                     conversation_id=conversation_id,
                                     conversations=conversations)
            except Exception as e:
                conversations = chat_service.get_user_conversations(limit=20)
                return render_template('index.html',
                                     error=f"Error continuando conversación: {str(e)}",
                                     conversation_id=conversation_id,
                                     conversations=conversations)
    
    # GET - mostrar conversación existente
    try:
        history = chat_service.get_conversation_history(conversation_id)
        conversations = chat_service.get_user_conversations(limit=20)
        
        return render_template('index.html',
                             conversation_history=history,
                             conversation_id=conversation_id,
                             conversations=conversations)
    except Exception as e:
        conversations = chat_service.get_user_conversations(limit=20)
        return render_template('index.html',
                             error=f"Error cargando conversación: {str(e)}",
                             conversations=conversations)


@web_bp.route('/history')
def user_history():
    """
    Ver historial de conversaciones
    """
    try:
        conversations = chat_service.get_user_conversations(limit=20)
        return render_template('history.html',
                             conversations=conversations)
    except Exception as e:
        return render_template('index.html',
                             error=f"Error cargando historial: {str(e)}")


@web_bp.route('/about')
def about():
    """
    Página sobre MedicoIA
    """
    return render_template('about.html')


# API Routes for backward compatibility
@web_bp.route('/api/get-history')
def get_history_api():
    """Simple API for history - redirects to conversations"""
    return '<div class="text-center"><a href="/">Ver historial completo</a></div>'


@web_bp.route('/api/conversation/<conversation_id>')
def get_conversation_api(conversation_id):
    """Simple API for conversations - redirects"""
    from flask import redirect, url_for
    return redirect(url_for('web.view_conversation', conversation_id=conversation_id))


# Filtros Jinja personalizados
@web_bp.app_template_filter('datetime_format')
def datetime_format(value, format='%Y-%m-%d %H:%M'):
    """Filtro para formatear fechas en templates"""
    if value is None:
        return ""
    return value.strftime(format)


# Context processors para variables globales en templates
@web_bp.app_context_processor
def inject_app_info():
    """Inyecta información de la app en todos los templates"""
    return {
        'app_name': 'MedicoIA',
        'app_version': '1.0.0',
        'app_description': 'Asistente Médico con IA'
    }