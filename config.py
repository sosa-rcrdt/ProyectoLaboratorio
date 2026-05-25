import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "clave_secreta_laboratorio"

    # Contraseña para activar el modo edición
    EDIT_PASSWORD = "hola"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER_FOTOS = os.path.join(BASE_DIR, "static", "uploads", "fotos")
    UPLOAD_FOLDER_PDFS = os.path.join(BASE_DIR, "static", "uploads", "pdfs")

    MAX_ARCHIVOS_POR_TIPO = 5

    EXTENSIONES_FOTOS = {"png", "jpg", "jpeg", "gif", "webp"}
    EXTENSIONES_PDFS = {"pdf"}