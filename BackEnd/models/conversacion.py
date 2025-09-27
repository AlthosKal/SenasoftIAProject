from senasoft import db
from datetime import datetime

class Conversacion(db.Model):
    conversacion_id = db.Column(db.Integer, primary_key=True)
    agente_id = db.Column(db.Integer)
    fecha_inicio = db.Column(db.DateTime, default=datetime.now)
    fecha_ultimo_mensaje = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    titulo = db.Column(db.String(50), nullable=False)
