from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    numero_serie = db.Column(db.String(100), unique=True, nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(255), nullable=True)

    doctor_responsable = db.Column(db.String(150), nullable=False)
    puesto_responsable = db.Column(db.String(100), nullable=False)
    area_responsable = db.Column(db.String(150), nullable=False)

    nombre_material = db.Column(db.String(150), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    ubicacion = db.Column(db.String(150), nullable=False)
    estado_prestamo = db.Column(db.String(50), nullable=False)

    pdf_especificaciones = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Material {self.nombre_material}>"