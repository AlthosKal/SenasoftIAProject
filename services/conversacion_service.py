from repositories import conversacion_repository
from models.conversacion import Conversacion
from datetime import datetime

#Listar conversaciones
def get_conversaciones():
    return conversacion_repository.get_all()

#Crear conversacion
def create_conversacion(agente_id: int, fecha_inicio: datetime):
    nuevaConversacion = Conversacion(agente_id = agente_id, fecha_inicio = fecha_inicio)
    conversacion_repository.save(nuevaConversacion)
    return nuevaConversacion

#Eliminar conversacion
def delete_conversacion(conversacion_id: int):
    try:
        conversacion = conversacion_repository.search_by_id(conversacion_id)
        if conversacion != None:
            conversacion_repository.delete(conversacion)
            return "Despues le meto dtos para mejores respuestas"
        else:
            return "No se ha encontrado la conversacion a eliminar"
    except Exception as e:
        return (f"Error al eliminar la conversacion:  {e}")