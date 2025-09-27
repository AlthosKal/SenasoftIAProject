from senasoft import db
from models.mensaje import Mensaje

def get_all():
   return Mensaje.query.all()

def save(mensaje: Mensaje):
   db.session.add(mensaje)
   db.session.commit()

def delete(mensaje: Mensaje):
   db.session.delete(mensaje)
   db.session.commit()

def search_by_id(mensaje_id: int):
   return Mensaje.query.get(mensaje_id)