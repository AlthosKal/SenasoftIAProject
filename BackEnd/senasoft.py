from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():

    # Carga de variables definidas en archivo .env (toca crearlo)
    load_dotenv()
    app = Flask(__name__)

    #Parametros bd 
    #En la url se pone el usuario, contraseña, host y base de datos
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    #Importar-Registrar controladores
    from controllers.conversacion_controller import conversacion_bp
    from controllers.mensaje_controller import mensaje_bp
    app.register_blueprint(conversacion_bp)
    app.register_blueprint(mensaje_bp)

    with app.app_context():
        db.create_all()

    return app