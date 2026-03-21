import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename

from models import db, Material

materiales_bp = Blueprint("materiales", __name__)


def guardar_archivo(archivo, carpeta_destino):
    if archivo and archivo.filename:
        nombre_seguro = secure_filename(archivo.filename)
        nombre_base, extension = os.path.splitext(nombre_seguro)

        identificador_unico = uuid.uuid4().hex
        nuevo_nombre = f"{nombre_base}_{identificador_unico}{extension}"

        ruta_completa = os.path.join(carpeta_destino, nuevo_nombre)
        archivo.save(ruta_completa)

        return nuevo_nombre

    return None


@materiales_bp.route("/")
@materiales_bp.route("/materiales")
def listar_materiales():
    materiales = Material.query.all()
    return render_template("materiales/lista.html", materiales=materiales)


@materiales_bp.route("/crear", methods=["GET", "POST"])
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

        nombre_foto = guardar_archivo(
            archivo_foto,
            current_app.config["UPLOAD_FOLDER_FOTOS"]
        )
        nombre_pdf = guardar_archivo(
            archivo_pdf,
            current_app.config["UPLOAD_FOLDER_PDFS"]
        )

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

        return redirect(url_for("materiales.listar_materiales"))

    return render_template("materiales/crear.html")


@materiales_bp.route("/editar/<int:id>", methods=["GET", "POST"])
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
            if material.foto:
                ruta_foto_anterior = os.path.join(
                    current_app.config["UPLOAD_FOLDER_FOTOS"],
                    material.foto
                )
                if os.path.exists(ruta_foto_anterior):
                    os.remove(ruta_foto_anterior)

            nombre_foto = guardar_archivo(
                archivo_foto,
                current_app.config["UPLOAD_FOLDER_FOTOS"]
            )
            material.foto = nombre_foto

        if archivo_pdf and archivo_pdf.filename:
            if material.pdf_especificaciones:
                ruta_pdf_anterior = os.path.join(
                    current_app.config["UPLOAD_FOLDER_PDFS"],
                    material.pdf_especificaciones
                )
                if os.path.exists(ruta_pdf_anterior):
                    os.remove(ruta_pdf_anterior)

            nombre_pdf = guardar_archivo(
                archivo_pdf,
                current_app.config["UPLOAD_FOLDER_PDFS"]
            )
            material.pdf_especificaciones = nombre_pdf

        db.session.commit()
        return redirect(url_for("materiales.listar_materiales"))

    return render_template("materiales/editar.html", material=material)


@materiales_bp.route("/materiales/eliminar/<int:id>", methods=["POST"])
def eliminar_material(id):
    material = Material.query.get_or_404(id)

    if material.foto:
        ruta_foto = os.path.join(current_app.config["UPLOAD_FOLDER_FOTOS"], material.foto)
        if os.path.exists(ruta_foto):
            os.remove(ruta_foto)

    if material.pdf_especificaciones:
        ruta_pdf = os.path.join(current_app.config["UPLOAD_FOLDER_PDFS"], material.pdf_especificaciones)
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)

    db.session.delete(material)
    db.session.commit()

    return redirect(url_for("materiales.listar_materiales"))