import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Simple logging configuration
import logging
from controller.web_controller import web_bp


def create_app(config_name: str = 'development') -> Flask:
    """
    Application factory for creating Flask app instance.
    Implements layered architecture with proper dependency injection.
    """
    
    # Load environment variables
    load_dotenv()
    
    # Create Flask app with view templates and static files
    app = Flask(__name__, 
                template_folder='view/templates',  # Plantillas Jinja en view
                static_folder='view/static')  # Assets estáticos
    
    # Configure app
    _configure_app(app, config_name)
    
    # Configure CORS
    _configure_cors(app)
    
    # Setup simple logging
    _setup_logging(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Setup health check
    _setup_health_check(app)
    
    return app


def _configure_app(app: Flask, config_name: str):
    """Configure Flask app settings"""
    
    # Basic Flask config
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'medico-ia-secret-key-2025')
    app.config['DEBUG'] = config_name == 'development'
    app.config['TESTING'] = config_name == 'testing'
    
    # MongoDB configuration
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # LangChain and AI configuration
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_KEY')
    app.config['OLLAMA_URL'] = os.getenv('OLLAMA_URL')
    app.config['OLLAMA_MODEL'] = os.getenv('OLLAMA_MODEL')
    
    # RAG configuration
    app.config['EMBEDDING_MODEL'] = os.getenv('EMBEDDING_MODEL')
    app.config['VECTOR_SEARCH_INDEX'] = os.getenv('VECTOR_SEARCH_INDEX')
    
    # Logging configuration
    app.config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')


def _configure_cors(app: Flask):
    """Configure CORS for the application"""
    
    allowed_origins = [
        "http://localhost:7860",
        "http://127.0.0.1:7860",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173"
    ]
    
    # Add production origins from environment
    production_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
    if production_origins and production_origins[0]:
        allowed_origins.extend(production_origins)
    
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": [
                "Content-Type", 
                "Authorization", 
                "X-Requested-With",
                "Accept",
                "Origin"
            ],
            "supports_credentials": True
        }
    })


def _setup_logging(app: Flask):
    """Setup simple logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def _register_blueprints(app: Flask):
    """Register all blueprints"""
    
    # Register web views blueprint (Jinja templates only)
    app.register_blueprint(web_bp)


def _setup_health_check(app: Flask):
    """Setup basic health check endpoint"""
    
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "service": "MedicoIA Web Application",
            "timestamp": "2025-01-01T00:00:00Z"
        }