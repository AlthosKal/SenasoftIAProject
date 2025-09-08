from flask import Blueprint, jsonify, request
from services import conversacion_service
from datetime import datetime

mensaje_bp = Blueprint("mensaje", __name__)

"En un mismo endpoint podemos tener diferentes metodos"
@mensaje_bp.route("/", methods=['GET', 'POST'])
def chat():
    return "<h1>nada de momento</h1>"

@mensaje_bp.route("/analyze-image", methods=['POST'])
def analyze_image():
    return "<h1>nada de momento</h1>"