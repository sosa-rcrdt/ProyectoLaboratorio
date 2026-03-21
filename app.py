import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["UPLOAD_FOLDER_FOTOS"] = os.path.join("static", "uploads", "fotos")
app.config["UPLOAD_FOLDER_PDFS"] = os.path.join("static", "uploads", "pdfs")

db = SQLAlchemy(app)


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_serie = db.Column(db.String(100), unique=True, nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(255), nullable=True)
    doctor_responsable = db.Column(db.String(150), nullable=False)
    nombre_material = db.Column(db.String(150), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    ubicacion = db.Column(db.String(150), nullable=False)
    estado_prestamo = db.Column(db.String(50), nullable=False)
    pdf_especificaciones = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Material {self.nombre_material}>"


def guardar_archivo(archivo, carpeta_destino):
    if archivo and archivo.filename:
        nombre_seguro = secure_filename(archivo.filename)
        ruta_completa = os.path.join(carpeta_destino, nombre_seguro)
        archivo.save(ruta_completa)
        return nombre_seguro
    return None


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/materiales")
def listar_materiales():
    materiales = Material.query.all()
    return render_template("materiales/lista.html", materiales=materiales)


@app.route("/materiales/crear", methods=["GET", "POST"])
def crear_material():
    if request.method == "POST":
        numero_serie = request.form["numero_serie"]
        marca = request.form["marca"]
        doctor_responsable = request.form["doctor_responsable"]
        nombre_material = request.form["nombre_material"]
        anio = request.form["anio"]
        ubicacion = request.form["ubicacion"]
        estado_prestamo = request.form["estado_prestamo"]

        archivo_foto = request.files.get("foto")
        archivo_pdf = request.files.get("pdf_especificaciones")

        nombre_foto = guardar_archivo(archivo_foto, app.config["UPLOAD_FOLDER_FOTOS"])
        nombre_pdf = guardar_archivo(archivo_pdf, app.config["UPLOAD_FOLDER_PDFS"])

        nuevo_material = Material(
            numero_serie=numero_serie,
            marca=marca,
            doctor_responsable=doctor_responsable,
            nombre_material=nombre_material,
            anio=int(anio),
            ubicacion=ubicacion,
            estado_prestamo=estado_prestamo,
            foto=nombre_foto,
            pdf_especificaciones=nombre_pdf
        )

        db.session.add(nuevo_material)
        db.session.commit()

        return redirect(url_for("listar_materiales"))

    return render_template("materiales/crear.html")


@app.route("/materiales/editar/<int:id>", methods=["GET", "POST"])
def editar_material(id):
    material = Material.query.get_or_404(id)

    if request.method == "POST":
        material.numero_serie = request.form["numero_serie"]
        material.marca = request.form["marca"]
        material.doctor_responsable = request.form["doctor_responsable"]
        material.nombre_material = request.form["nombre_material"]
        material.anio = int(request.form["anio"])
        material.ubicacion = request.form["ubicacion"]
        material.estado_prestamo = request.form["estado_prestamo"]

        archivo_foto = request.files.get("foto")
        archivo_pdf = request.files.get("pdf_especificaciones")

        if archivo_foto and archivo_foto.filename:
            nombre_foto = guardar_archivo(archivo_foto, app.config["UPLOAD_FOLDER_FOTOS"])
            material.foto = nombre_foto

        if archivo_pdf and archivo_pdf.filename:
            nombre_pdf = guardar_archivo(archivo_pdf, app.config["UPLOAD_FOLDER_PDFS"])
            material.pdf_especificaciones = nombre_pdf

        db.session.commit()
        return redirect(url_for("listar_materiales"))

    return render_template("materiales/editar.html", material=material)


@app.route("/materiales/eliminar/<int:id>", methods=["POST"])
def eliminar_material(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for("listar_materiales"))


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER_FOTOS"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER_PDFS"], exist_ok=True)

    with app.app_context():
        db.create_all()

    app.run(debug=True)