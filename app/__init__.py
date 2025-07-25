from flask import Flask

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # Register blueprints
    from .routes import bp
    app.register_blueprint(bp)

    return app
