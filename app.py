from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from uuid import uuid4
import os

from config import Config
from models import db, Material, MaterialFoto, MaterialPDF


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


# Crear carpetas de uploads si no existen
os.makedirs(app.config["UPLOAD_FOLDER_FOTOS"], exist_ok=True)
os.makedirs(app.config["UPLOAD_FOLDER_PDFS"], exist_ok=True)


PROFESORES = {
    "Dr. Castillo Mixcoatl Juan": {
        "puesto": "Profesor Investigador",
        "area": "Optoelectrónica y fotónica"
    },
    "Dr. Muñoz Aguirre Severino": {
        "puesto": "Profesor Investigador",
        "area": "Optoelectrónica y fotónica"
    },
    "Dra. Beltrán Pérez Georgina": {
        "puesto": "Profesora Investigadora",
        "area": "Optoelectrónica y fotónica"
    },
    "Mtro. Pinto Rafael María Inés Teresa": {
        "puesto": "Técnica Académica",
        "area": "Optoelectrónica y fotónica"
    }
}


def archivos_con_nombre(lista_archivos):
    """
    Filtra los archivos realmente seleccionados por el usuario.
    Cuando no se selecciona nada, Flask puede recibir un objeto vacío.
    """
    return [archivo for archivo in lista_archivos if archivo and archivo.filename]


def extension_permitida(nombre_archivo, extensiones_permitidas):
    if "." not in nombre_archivo:
        return False

    extension = nombre_archivo.rsplit(".", 1)[1].lower()
    return extension in extensiones_permitidas


def validar_archivos(fotos, pdfs, fotos_actuales=0, pdfs_actuales=0):
    """
    Valida cantidad máxima y extensión de archivos.
    El límite aplica por material:
    - máximo 5 fotos
    - máximo 5 PDFs
    """
    max_archivos = app.config["MAX_ARCHIVOS_POR_TIPO"]

    if fotos_actuales + len(fotos) > max_archivos:
        return f"Cada material puede tener máximo {max_archivos} fotos."

    if pdfs_actuales + len(pdfs) > max_archivos:
        return f"Cada material puede tener máximo {max_archivos} PDFs."

    for foto in fotos:
        filename = secure_filename(foto.filename)
        if not extension_permitida(filename, app.config["EXTENSIONES_FOTOS"]):
            return "Solo se permiten imágenes con extensión: png, jpg, jpeg, gif o webp."

    for pdf in pdfs:
        filename = secure_filename(pdf.filename)
        if not extension_permitida(filename, app.config["EXTENSIONES_PDFS"]):
            return "Solo se permiten archivos PDF."

    return None


def guardar_archivo(archivo, carpeta_config, ruta_relativa):
    """
    Guarda un archivo con nombre único y regresa la ruta relativa
    que se almacenará en la base de datos.

    Ejemplos de retorno:
    uploads/fotos/9f2a1c_material.png
    uploads/pdfs/7b3d8e_manual.pdf
    """
    if not archivo or not archivo.filename:
        return None

    filename_original = secure_filename(archivo.filename)

    if not filename_original:
        return None

    nombre_unico = f"{uuid4().hex}_{filename_original}"

    ruta_absoluta = os.path.join(app.config[carpeta_config], nombre_unico)
    archivo.save(ruta_absoluta)

    return f"{ruta_relativa}/{nombre_unico}"


def eliminar_archivo_local(ruta_relativa):
    if not ruta_relativa:
        return

    if str(ruta_relativa).startswith("http"):
        return

    path_absoluta = os.path.join(app.static_folder, ruta_relativa)

    if os.path.exists(path_absoluta):
        try:
            os.remove(path_absoluta)
        except Exception as e:
            print(f"Error al eliminar {path_absoluta}: {e}")


def guardar_fotos_de_material(material, fotos):
    for foto in fotos:
        ruta_foto = guardar_archivo(
            foto,
            "UPLOAD_FOLDER_FOTOS",
            "uploads/fotos"
        )

        if ruta_foto:
            material_foto = MaterialFoto(
                material_id=material.id,
                archivo=ruta_foto
            )
            db.session.add(material_foto)


def guardar_pdfs_de_material(material, pdfs):
    for pdf in pdfs:
        ruta_pdf = guardar_archivo(
            pdf,
            "UPLOAD_FOLDER_PDFS",
            "uploads/pdfs"
        )

        if ruta_pdf:
            material_pdf = MaterialPDF(
                material_id=material.id,
                archivo=ruta_pdf
            )
            db.session.add(material_pdf)


# MENÚ PRINCIPAL
@app.route("/")
def menu():
    return render_template("menu.html")


# LISTAR TODOS LOS MATERIALES
@app.route("/materiales")
def listar_materiales():
    materiales = Material.query.all()
    total_materiales = Material.query.count()

    return render_template(
        "materiales/lista.html",
        materiales=materiales,
        total_materiales=total_materiales
    )


# CREAR MATERIAL
@app.route("/materiales/crear", methods=["GET", "POST"])
def crear_material():
    current_year = datetime.now().year
    estados_validos = ["Disponible", "En préstamo", "Fuera de servicio", "En mantenimiento"]
    error = None

    if request.method == "POST":
        numero_serie = request.form.get("numero_serie", "").strip()
        marca = request.form.get("marca", "").strip()
        doctor_responsable = request.form.get("doctor_responsable", "").strip()

        datos_profesor = PROFESORES.get(doctor_responsable)
        puesto_responsable = datos_profesor["puesto"] if datos_profesor else ""
        area_responsable = datos_profesor["area"] if datos_profesor else ""

        nombre_material = request.form.get("nombre_material", "").strip()
        anio = request.form.get("anio", "").strip()
        ubicacion = request.form.get("ubicacion", "").strip()
        estado_prestamo = request.form.get("estado_prestamo", "").strip()

        fotos = archivos_con_nombre(request.files.getlist("fotos"))
        pdfs = archivos_con_nombre(request.files.getlist("pdfs"))

        # Primero validar todo el formulario
        if not numero_serie or not marca or not doctor_responsable or not nombre_material or not anio or not ubicacion or not estado_prestamo:
            error = "Todos los campos obligatorios deben estar llenos."
        elif not anio.isdigit():
            error = "El año debe ser un número entero."
        elif int(anio) > current_year:
            error = "El año no puede ser mayor al actual."
        elif estado_prestamo not in estados_validos:
            error = "El estado seleccionado no es válido."
        elif Material.query.filter_by(numero_serie=numero_serie).first():
            error = "Ya existe un material con ese número de serie."
        else:
            error = validar_archivos(fotos, pdfs)

        if error:
            return render_template(
                "materiales/crear.html",
                error=error,
                estados_validos=estados_validos,
                datos=request.form,
                current_year=current_year,
                profesores=PROFESORES,
                max_archivos=app.config["MAX_ARCHIVOS_POR_TIPO"]
            )

        # Si todo es válido, primero se guarda el material
        nuevo_material = Material(
            numero_serie=numero_serie,
            marca=marca,
            doctor_responsable=doctor_responsable,
            puesto_responsable=puesto_responsable,
            area_responsable=area_responsable,
            nombre_material=nombre_material,
            anio=int(anio),
            ubicacion=ubicacion,
            estado_prestamo=estado_prestamo
        )

        db.session.add(nuevo_material)
        db.session.flush()

        # Después se guardan los archivos asociados al material
        guardar_fotos_de_material(nuevo_material, fotos)
        guardar_pdfs_de_material(nuevo_material, pdfs)

        db.session.commit()

        flash("Material registrado correctamente.", "success")
        return redirect(url_for("listar_materiales"))

    return render_template(
        "materiales/crear.html",
        error=error,
        estados_validos=estados_validos,
        datos={},
        current_year=current_year,
        profesores=PROFESORES,
        max_archivos=app.config["MAX_ARCHIVOS_POR_TIPO"]
    )


# BUSCAR MATERIAL
@app.route("/materiales/buscar", methods=["GET", "POST"])
def buscar_material():
    resultados = []
    busqueda = ""
    error = None

    if request.method == "POST":
        busqueda = request.form.get("busqueda", "").strip()

        if not busqueda:
            error = "Debes escribir algo para buscar."
        else:
            resultados = Material.query.filter(
                (Material.numero_serie.ilike(f"%{busqueda}%")) |
                (Material.nombre_material.ilike(f"%{busqueda}%"))
            ).all()

    return render_template(
        "materiales/buscar.html",
        resultados=resultados,
        busqueda=busqueda,
        error=error
    )


# VER MATERIALES POR PROFESOR
@app.route("/materiales/profesor", methods=["GET", "POST"])
def materiales_por_profesor():
    resultados = []
    profesor_buscado = ""
    error = None

    profesores = db.session.query(Material.doctor_responsable).distinct().all()
    profesores = [p[0] for p in profesores if p[0]]

    if request.method == "POST":
        profesor_buscado = request.form.get("doctor_responsable", "").strip()

        if not profesor_buscado:
            error = "Debes seleccionar o escribir un profesor."
        else:
            resultados = Material.query.filter(
                Material.doctor_responsable.ilike(f"%{profesor_buscado}%")
            ).all()

    return render_template(
        "materiales/profesor.html",
        resultados=resultados,
        profesor_buscado=profesor_buscado,
        profesores=profesores,
        error=error
    )


# EDITAR MATERIAL
@app.route("/materiales/editar/<int:id>", methods=["GET", "POST"])
def editar_material(id):
    current_year = datetime.now().year
    material = Material.query.get_or_404(id)

    estados_validos = ["Disponible", "En préstamo", "Fuera de servicio", "En mantenimiento"]
    error = None

    if request.method == "POST":
        numero_serie = request.form.get("numero_serie", "").strip()
        marca = request.form.get("marca", "").strip()
        doctor_responsable = request.form.get("doctor_responsable", "").strip()

        datos_profesor = PROFESORES.get(doctor_responsable)
        puesto_responsable = datos_profesor["puesto"] if datos_profesor else ""
        area_responsable = datos_profesor["area"] if datos_profesor else ""

        nombre_material = request.form.get("nombre_material", "").strip()
        anio = request.form.get("anio", "").strip()
        ubicacion = request.form.get("ubicacion", "").strip()
        estado_prestamo = request.form.get("estado_prestamo", "").strip()

        fotos = archivos_con_nombre(request.files.getlist("fotos"))
        pdfs = archivos_con_nombre(request.files.getlist("pdfs"))

        # Primero validar todo el formulario
        if not numero_serie or not marca or not doctor_responsable or not nombre_material or not anio or not ubicacion or not estado_prestamo:
            error = "Todos los campos obligatorios deben estar llenos."
        elif not anio.isdigit():
            error = "El año debe ser un número entero."
        elif int(anio) > current_year:
            error = "El año no puede ser mayor al actual."
        elif estado_prestamo not in estados_validos:
            error = "El estado seleccionado no es válido."
        else:
            material_con_mismo_numero = Material.query.filter_by(numero_serie=numero_serie).first()

            if material_con_mismo_numero and material_con_mismo_numero.id != material.id:
                error = "Ya existe otro material con ese número de serie."
            else:
                error = validar_archivos(
                    fotos,
                    pdfs,
                    fotos_actuales=len(material.fotos),
                    pdfs_actuales=len(material.pdfs)
                )

        if error:
            return render_template(
                "materiales/editar.html",
                material=material,
                error=error,
                estados_validos=estados_validos,
                datos=request.form,
                current_year=current_year,
                profesores=PROFESORES,
                max_archivos=app.config["MAX_ARCHIVOS_POR_TIPO"]
            )

        # Primero actualizar datos normales
        material.numero_serie = numero_serie
        material.marca = marca
        material.doctor_responsable = doctor_responsable
        material.puesto_responsable = puesto_responsable
        material.area_responsable = area_responsable
        material.nombre_material = nombre_material
        material.anio = int(anio)
        material.ubicacion = ubicacion
        material.estado_prestamo = estado_prestamo

        # Después agregar nuevos archivos, sin borrar los anteriores
        guardar_fotos_de_material(material, fotos)
        guardar_pdfs_de_material(material, pdfs)

        db.session.commit()

        flash("Material actualizado correctamente.", "success")
        return redirect(url_for("listar_materiales"))

    return render_template(
        "materiales/editar.html",
        material=material,
        error=error,
        estados_validos=estados_validos,
        datos={},
        current_year=current_year,
        profesores=PROFESORES,
        max_archivos=app.config["MAX_ARCHIVOS_POR_TIPO"]
    )


# ELIMINAR UNA FOTO ESPECÍFICA
@app.route("/materiales/foto/eliminar/<int:foto_id>", methods=["POST"])
def eliminar_foto_material(foto_id):
    foto = MaterialFoto.query.get_or_404(foto_id)
    material_id = foto.material_id

    eliminar_archivo_local(foto.archivo)

    db.session.delete(foto)
    db.session.commit()

    flash("Foto eliminada correctamente.", "success")
    return redirect(url_for("editar_material", id=material_id))


# ELIMINAR UN PDF ESPECÍFICO
@app.route("/materiales/pdf/eliminar/<int:pdf_id>", methods=["POST"])
def eliminar_pdf_material(pdf_id):
    pdf = MaterialPDF.query.get_or_404(pdf_id)
    material_id = pdf.material_id

    eliminar_archivo_local(pdf.archivo)

    db.session.delete(pdf)
    db.session.commit()

    flash("PDF eliminado correctamente.", "success")
    return redirect(url_for("editar_material", id=material_id))


# ELIMINAR MATERIAL COMPLETO
@app.route("/materiales/eliminar/<int:id>", methods=["POST"])
def eliminar_material(id):
    material = Material.query.get_or_404(id)

    for foto in material.fotos:
        eliminar_archivo_local(foto.archivo)

    for pdf in material.pdfs:
        eliminar_archivo_local(pdf.archivo)

    db.session.delete(material)
    db.session.commit()

    flash("Material eliminado correctamente.", "success")
    return redirect(url_for("listar_materiales"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
