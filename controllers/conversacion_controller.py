from flask import Blueprint, jsonify, request
from services import conversacion_service
from datetime import datetime

conversacion_bp = Blueprint("conversacion", __name__)

#Obtener conversaciones
@conversacion_bp.route("/conversacion", methods=['GET'])
def get_conversaciones():
    conversaciones = conversacion_service.get_conversaciones()
    #Tambien puedo devolver la lista de objetos y ya
    return jsonify([{"Id conversacion": c.conversacion_id, "Id modelo": c.agente_id, "Titulo:": c.titulo} for c in conversaciones])


#Eliminar conversacion
@conversacion_bp.route("/conversacion/<conversacion_id>", methods=['DELETE'])
def delete_conversacion(conversacion_id: int):
    return conversacion_service.delete_conversacion(conversacion_id)

