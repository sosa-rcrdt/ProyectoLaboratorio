from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    numero_serie = db.Column(db.String(100), unique=True, nullable=False)
    marca = db.Column(db.String(100), nullable=False)

    doctor_responsable = db.Column(db.String(150), nullable=False)
    puesto_responsable = db.Column(db.String(100), nullable=False)
    area_responsable = db.Column(db.String(150), nullable=False)

    nombre_material = db.Column(db.String(150), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    ubicacion = db.Column(db.String(150), nullable=False)
    estado_prestamo = db.Column(db.String(50), nullable=False)

    fotos = db.relationship(
        "MaterialFoto",
        backref="material",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    pdfs = db.relationship(
        "MaterialPDF",
        backref="material",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Material {self.nombre_material}>"


class MaterialFoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey("material.id"), nullable=False)
    archivo = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<MaterialFoto {self.archivo}>"


class MaterialPDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey("material.id"), nullable=False)
    archivo = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<MaterialPDF {self.archivo}>"
