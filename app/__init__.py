from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from app.database.db_config import init_db
from app.errors.handlers import register_error_handlers
from app.routes.lead_routes import lead_bp
from app.routes.appointment_routes import appointment_bp
from app.routes.auth_routes import auth_bp
from app.routes.cron_job_routes import cron_job_bp

load_dotenv()

def create_app():
    app = Flask(__name__)

    CORS(
        app,
        resources={r"/*": {
            "origins": [
                "https://form.b2bflow.com.br"
            ]
        }},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )

    init_db()
    
    app.register_blueprint(lead_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cron_job_bp)

    
    register_error_handlers(app)

    return app
