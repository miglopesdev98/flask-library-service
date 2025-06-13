from flask import Blueprint

# Create the blueprint
bp = Blueprint('library', __name__)

# Import routes after creating blueprint to avoid circular imports
from . import routes

# This makes the blueprint available when importing from app.library
__all__ = ['bp']
