import os
from flask import Flask

from config import Config
from models import db
from routes import materiales_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(materiales_bp)

    os.makedirs(app.config["UPLOAD_FOLDER_FOTOS"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER_PDFS"], exist_ok=True)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)