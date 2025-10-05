import os
from flask import Blueprint, render_template, request, redirect, url_for
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from service.chat_service_impl import ChatServiceImpl
from service.rag_service_impl import RAGServiceImpl

# Create Blueprint for web views
web_bp = Blueprint('web', __name__)

# Initialize services with error handling
def get_chat_service():
    """Get chat service instance, initializing if needed"""
    if not hasattr(get_chat_service, 'instance'):
        try:
            get_chat_service.instance = ChatServiceImpl()
        except Exception as e:
            print(f"Error initializing chat service: {e}")
            get_chat_service.instance = None
    return get_chat_service.instance

def get_rag_service():
    """Get RAG service instance, initializing if needed"""
    if not hasattr(get_rag_service, 'instance'):
        try:
            get_rag_service.instance = RAGServiceImpl()
        except Exception as e:
            print(f"Error initializing RAG service: {e}")
            get_rag_service.instance = None
    return get_rag_service.instance


@web_bp.route('/')
def index():
    """
    Página principal del chatbot médico usando Jinja
    Renderiza index.html con historial de conversaciones
    """
    try:
        chat_service = get_chat_service()
        if chat_service:
            conversations = chat_service.get_user_conversations(limit=20)
        else:
            conversations = []
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
                chat_service = get_chat_service()
                if not chat_service:
                    raise Exception("Chat service not available")
                
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
                chat_service = get_chat_service()
                if not chat_service:
                    raise Exception("Chat service not available")
                
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
                chat_service = get_chat_service()
                conversations = chat_service.get_user_conversations(limit=20) if chat_service else []
                return render_template('index.html',
                                     error=f"Error continuando conversación: {str(e)}",
                                     conversation_id=conversation_id,
                                     conversations=conversations)
    
    # GET - mostrar conversación existente
    try:
        chat_service = get_chat_service()
        if not chat_service:
            return render_template('index.html',
                                 error="Chat service not available",
                                 conversations=[])
        
        history = chat_service.get_conversation_history(conversation_id)
        conversations = chat_service.get_user_conversations(limit=20)
        
        return render_template('index.html',
                             conversation_history=history,
                             conversation_id=conversation_id,
                             conversations=conversations)
    except Exception as e:
        chat_service = get_chat_service()
        conversations = chat_service.get_user_conversations(limit=20) if chat_service else []
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


@web_bp.route('/documents', methods=['GET', 'POST'])
def documents():
    """
    Gestión de documentos para el sistema RAG
    """
    if request.method == 'POST':
        try:
            # Get uploaded files
            uploaded_files = request.files.getlist('documents')
            
            rag_service = get_rag_service()
            if not rag_service:
                return render_template('documents.html',
                                     error="RAG service not available",
                                     documents=[])
            
            if not uploaded_files or all(f.filename == '' for f in uploaded_files):
                return render_template('documents.html',
                                     error="No se seleccionaron archivos",
                                     documents=rag_service.get_all_documents())
            
            # Get form data
            document_type = request.form.get('document_type', 'other')
            specialty = request.form.get('specialty', 'general')
            description = request.form.get('description', '')
            
            # Process documents
            result = rag_service.process_documents(
                uploaded_files, document_type, specialty, description
            )
            
            if result['errors']:
                error_msg = f"Errores procesando documentos: {'; '.join([e.get('error', str(e)) for e in result['errors']])}"
                return render_template('documents.html',
                                     error=error_msg,
                                     documents=rag_service.get_all_documents())
            
            success_msg = f"Se procesaron {len(result['processed_documents'])} documentos correctamente. Total de fragmentos: {result['total_fragments']}"
            return render_template('documents.html',
                                 success_message=success_msg,
                                 documents=rag_service.get_all_documents())
            
        except Exception as e:
            return render_template('documents.html',
                                 error=f"Error procesando documentos: {str(e)}",
                                 documents=rag_service.get_all_documents())
    
    # GET - mostrar página de documentos
    try:
        rag_service = get_rag_service()
        if rag_service:
            documents = rag_service.get_all_documents()
        else:
            documents = []
        return render_template('documents.html', documents=documents)
    except Exception as e:
        return render_template('documents.html',
                             error=f"Error cargando documentos: {str(e)}",
                             documents=[])


@web_bp.route('/documents/delete/<document_id>', methods=['POST'])
def delete_document(document_id):
    """
    Eliminar un documento del sistema RAG
    """
    try:
        rag_service = get_rag_service()
        if not rag_service:
            return render_template('documents.html',
                                 error="RAG service not available",
                                 documents=[])
        
        success = rag_service.delete_document(document_id)
        if success:
            return redirect(url_for('web.documents'))
        else:
            return render_template('documents.html',
                                 error="Error eliminando documento",
                                 documents=rag_service.get_all_documents())
    except Exception as e:
        rag_service = get_rag_service()
        documents = rag_service.get_all_documents() if rag_service else []
        return render_template('documents.html',
                             error=f"Error eliminando documento: {str(e)}",
                             documents=documents)


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