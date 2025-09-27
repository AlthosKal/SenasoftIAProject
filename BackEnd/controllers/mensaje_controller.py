from flask import Blueprint, jsonify, request
from services import conversacion_service, mensaje_service
from datetime import datetime
import uuid
import os

mensaje_bp = Blueprint("mensaje", __name__)

@mensaje_bp.route("/", methods=['GET'])
def status():
    """Endpoint de estado del sistema"""
    return jsonify({
        "status": "active",
        "message": "MedicoIA Backend is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@mensaje_bp.route("/chat", methods=['POST'])
def chat():
    """Endpoint para chat de diagnóstico médico"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Mensaje requerido",
                "status": "error"
            }), 400
        
        message = data['message'].strip()
        
        if not message:
            return jsonify({
                "error": "El mensaje no puede estar vacío",
                "status": "error"
            }), 400
        
        return jsonify({
            "error": "Backend no implementado completamente - Se requiere integración con modelo de IA",
            "status": "error"
        }), 501
        
    except Exception as e:
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}",
            "status": "error"
        }), 500

@mensaje_bp.route("/analyze-image", methods=['POST'])
def analyze_image():
    """Endpoint para análisis de imágenes médicas"""
    try:
        if 'image' not in request.files:
            return jsonify({
                "error": "No se encontró archivo de imagen",
                "status": "error"
            }), 400
        
        file = request.files['image']
        message = request.form.get('message', 'Análisis de imagen médica')
        
        if file.filename == '':
            return jsonify({
                "error": "No se seleccionó archivo",
                "status": "error"
            }), 400
        
        # Validar tipo de archivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({
                "error": "Tipo de archivo no permitido. Use: PNG, JPG, JPEG, GIF, BMP",
                "status": "error"
            }), 400
        
        return jsonify({
            "error": "Backend no implementado completamente - Se requiere integración con modelo de análisis de imágenes médicas",
            "status": "error"
        }), 501
        
    except Exception as e:
        return jsonify({
            "error": f"Error al procesar imagen: {str(e)}",
            "status": "error"
        }), 500


@mensaje_bp.route("/conversation/<conversation_id>", methods=['GET'])
def get_conversation(conversation_id):
    """Obtener historial de una conversación específica"""
    return jsonify({
        "error": "Backend no implementado completamente",
        "status": "error"
    }), 501

@mensaje_bp.route("/conversation", methods=['POST'])
def get_conversations():
    """Obtener historial de conversaciones"""
    return jsonify({
        "error": "Backend no implementado completamente", 
        "status": "error"
    }), 501

@mensaje_bp.route("/conversation/delete/<conversation_id>", methods=['DELETE'])
def delete_conversation(conversation_id):
    """Eliminar una conversación"""
    return jsonify({
        "error": "Backend no implementado completamente",
        "status": "error"
    }), 501