from senasoft import db
from datetime import datetime

class Mensaje(db.Model):
    mensaje_id = db.Column(db.Integer, primary_key=True)
    conversacion_id = db.Column(db.Integer, db.ForeignKey("conversacion.conversacion_id"), nullable=False)
    contenido = db.Column(db.Text, nullable=False)

    fecha_envio = db.Column(db.DateTime, default=datetime.now)