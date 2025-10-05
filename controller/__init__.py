"""
Controller layer for the medical chatbot application.
Contains web views with Jinja templates only.
"""

from .web_controller import web_bp

__all__ = [
    'web_bp'
]