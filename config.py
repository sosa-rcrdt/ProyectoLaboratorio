import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER_FOTOS = os.path.join(BASE_DIR, "static", "uploads", "fotos")
    UPLOAD_FOLDER_PDFS = os.path.join(BASE_DIR, "static", "uploads", "pdfs")