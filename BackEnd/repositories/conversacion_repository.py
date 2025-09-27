from models.conversacion import Conversacion
from senasoft import db

#Metodos del repositorio

#Obtener todas las conversaciones
def get_all():
    return Conversacion.query.all()

#Guardar conversación
def save(conversacion: Conversacion):
    db.session.add(conversacion)
    db.session.commit()

#Eliminar conversación
def delete(conversacion: Conversacion):
    db.session.delete(conversacion)
    db.session.commit()

#Buscar por id (Devuelve la conversacion o none)
def search_by_id(conversacion_id: int):
    return Conversacion.query.get(conversacion_id)