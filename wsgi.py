from app import create_app, db
from app.models import Book, Checkout

"""
WSGI config for book_management_system project.

It exposes the WSGI callable as a module-level variable named `application`.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the environment from environment variable or default to 'development'
env = os.environ.get('FLASK_ENV', 'development')

# Create the application instance
app = create_app(env)

# For WSGI servers
application = app

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Book': Book, 'Checkout': Checkout}

if __name__ == "__main__":
    # Run the development server
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
