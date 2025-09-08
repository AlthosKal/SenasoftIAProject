from repositories import mensaje_repository
from models.mensaje import Mensaje

def get_mensajes():
    return mensaje_repository.get_all()

def create_mensaje():
    nuevoMensaje = Mensaje()
    mensaje_repository.save(nuevoMensaje)
    return nuevoMensaje

