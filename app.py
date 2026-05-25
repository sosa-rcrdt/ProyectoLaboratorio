from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from datetime import datetime
from uuid import uuid4
import os

from config import Config
from models import db, Material, MaterialFoto, MaterialPDF, Factura
from functools import wraps


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


# Crear carpetas de uploads si no existen
os.makedirs(app.config["UPLOAD_FOLDER_FOTOS"], exist_ok=True)
os.makedirs(app.config["UPLOAD_FOLDER_PDFS"], exist_ok=True)
os.makedirs(app.config["UPLOAD_FOLDER_FACTURAS"], exist_ok=True)

def modo_edicion_activo():
    return session.get("modo_edicion") is True


def ruta_local_segura(ruta):
    if not ruta:
        return False

    if not ruta.startswith("/"):
        return False

    if ruta.startswith("//"):
        return False

    return True


def requiere_modo_edicion(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not modo_edicion_activo():
            session["next_modo_edicion"] = request.path
            flash("Debes autenticarte para realizar modificaciones.", "error")
            return redirect(url_for("menu"))

        return func(*args, **kwargs)

    return wrapper


@app.context_processor
def inyectar_modo_edicion():
    return {
        "modo_edicion": modo_edicion_activo()
    }


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
    return [archivo for archivo in lista_archivos if archivo and archivo.filename]


def extension_permitida(nombre_archivo, extensiones_permitidas):
    if "." not in nombre_archivo:
        return False

    extension = nombre_archivo.rsplit(".", 1)[1].lower()
    return extension in extensiones_permitidas


def validar_archivos(fotos, pdfs, fotos_actuales=0, pdfs_actuales=0):
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

def validar_pdf_factura(pdf):
    if not pdf or not pdf.filename:
        return None

    filename = secure_filename(pdf.filename)

    if not extension_permitida(filename, app.config["EXTENSIONES_PDFS"]):
        return "Solo se permiten archivos PDF."

    return None

def guardar_archivo(archivo, carpeta_config, ruta_relativa):
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


def obtener_datos_material_formulario():
    inventariado = request.form.get("inventariado", "").strip()
    no_inventario = request.form.get("no_inventario", "").strip()

    if inventariado == "No Inventariado":
        no_inventario = ""

    return {
        "nombre_material": request.form.get("nombre_material", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "marca": request.form.get("marca", "").strip(),
        "numero_serie": request.form.get("numero_serie", "").strip(),
        "no_fabricante": request.form.get("no_fabricante", "").strip(),
        "inventariado": inventariado,
        "no_inventario": no_inventario,
        "software": request.form.get("software", "").strip(),
        "doctor_responsable": request.form.get("doctor_responsable", "").strip(),
        "anio": request.form.get("anio", "").strip(),
        "ubicacion": request.form.get("ubicacion", "").strip(),
        "estado_prestamo": request.form.get("estado_prestamo", "").strip(),
    }


def validar_material(datos, estados_validos, inventariado_validos, current_year):
    if datos["inventariado"] and datos["inventariado"] not in inventariado_validos:
        return "El valor de inventariado no es válido."

    if not datos["doctor_responsable"]:
        return "Debes seleccionar un profesor responsable."

    if datos["doctor_responsable"] not in PROFESORES:
        return "El profesor seleccionado no es válido."

    if not datos["estado_prestamo"]:
        return "Debes seleccionar un estado."

    if datos["estado_prestamo"] not in estados_validos:
        return "El estado seleccionado no es válido."

    if datos["anio"]:
        if not datos["anio"].isdigit():
            return "El año debe ser un número entero."

        if int(datos["anio"]) > current_year:
            return "El año no puede ser mayor al actual."

    return None


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

def guardar_pdf_factura(pdf):
    return guardar_archivo(
        pdf,
        "UPLOAD_FOLDER_FACTURAS",
        "uploads/facturas"
    )

@app.route("/autenticarse", methods=["POST"])
def autenticarse():
    siguiente_pendiente = session.get("next_modo_edicion")
    siguiente_formulario = request.form.get("next")
    siguiente = siguiente_pendiente or siguiente_formulario or request.referrer or url_for("menu")

    if not ruta_local_segura(siguiente):
        siguiente = url_for("menu")

    password = request.form.get("password", "")

    if password == app.config["EDIT_PASSWORD"]:
        session["modo_edicion"] = True
        session.pop("next_modo_edicion", None)
        flash("Modo edición activado correctamente.", "success")
        return redirect(siguiente)

    flash("Contraseña incorrecta.", "error")

    if siguiente_pendiente:
        return redirect(url_for("menu"))

    return redirect(siguiente)


@app.route("/salir-modo-edicion")
def salir_modo_edicion():
    session.pop("modo_edicion", None)
    flash("Has salido del modo edición.", "success")
    return redirect(url_for("menu"))

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
@requiere_modo_edicion
def crear_material():
    current_year = datetime.now().year
    estados_validos = ["Disponible", "En préstamo", "Fuera de servicio", "En mantenimiento"]
    inventariado_validos = ["Inventariado", "No Inventariado"]
    error = None

    if request.method == "POST":
        datos = obtener_datos_material_formulario()

        fotos = archivos_con_nombre(request.files.getlist("fotos"))
        pdfs = archivos_con_nombre(request.files.getlist("pdfs"))

        error = validar_material(
            datos,
            estados_validos,
            inventariado_validos,
            current_year
        )

        if not error:
            error = validar_archivos(fotos, pdfs)

        if error:
            return render_template(
                "materiales/crear.html",
                error=error,
                estados_validos=estados_validos,
                inventariado_validos=inventariado_validos,
                datos=datos,
                current_year=current_year,
                profesores=PROFESORES,
                max_archivos=app.config["MAX_ARCHIVOS_POR_TIPO"]
            )

        datos_profesor = PROFESORES.get(datos["doctor_responsable"])
        puesto_responsable = datos_profesor["puesto"] if datos_profesor else ""
        area_responsable = datos_profesor["area"] if datos_profesor else ""

        nuevo_material = Material(
            numero_serie=datos["numero_serie"],
            no_fabricante=datos["no_fabricante"],
            nombre_material=datos["nombre_material"],
            marca=datos["marca"],
            anio=int(datos["anio"]) if datos["anio"] else None,
            descripcion=datos["descripcion"],
            software=datos["software"],
            inventariado=datos["inventariado"],
            no_inventario=datos["no_inventario"],
            doctor_responsable=datos["doctor_responsable"],
            puesto_responsable=puesto_responsable,
            area_responsable=area_responsable,
            ubicacion=datos["ubicacion"],
            estado_prestamo=datos["estado_prestamo"]
        )

        db.session.add(nuevo_material)
        db.session.flush()

        guardar_fotos_de_material(nuevo_material, fotos)
        guardar_pdfs_de_material(nuevo_material, pdfs)

        db.session.commit()

        flash("Material registrado correctamente.", "success")
        return redirect(url_for("listar_materiales"))

    return render_template(
        "materiales/crear.html",
        error=error,
        estados_validos=estados_validos,
        inventariado_validos=inventariado_validos,
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
            filtros = [
                Material.nombre_material.ilike(f"%{busqueda}%"),
                Material.marca.ilike(f"%{busqueda}%"),
                Material.numero_serie.ilike(f"%{busqueda}%"),
                Material.no_fabricante.ilike(f"%{busqueda}%"),
                Material.no_inventario.ilike(f"%{busqueda}%")
            ]

            if busqueda.isdigit():
                filtros.append(Material.anio == int(busqueda))

            resultados = Material.query.filter(
                filtros[0] |
                filtros[1] |
                filtros[2] |
                filtros[3] |
                filtros[4] |
                (filtros[5] if len(filtros) > 5 else False)
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

    if request.method == "POST":
        profesor_buscado = request.form.get("doctor_responsable", "").strip()

        if not profesor_buscado:
            error = "Debes seleccionar un profesor."
        elif profesor_buscado not in PROFESORES:
            error = "El profesor seleccionado no es válido."
        else:
            resultados = Material.query.filter_by(
                doctor_responsable=profesor_buscado
            ).all()

    return render_template(
        "materiales/profesor.html",
        resultados=resultados,
        profesor_buscado=profesor_buscado,
        profesores=PROFESORES,
        error=error
    )


# EDITAR MATERIAL
@app.route("/materiales/editar/<int:id>", methods=["GET", "POST"])
@requiere_modo_edicion
def editar_material(id):
    current_year = datetime.now().year
    material = Material.query.get_or_404(id)

    estados_validos = ["Disponible", "En préstamo", "Fuera de servicio", "En mantenimiento"]
    inventariado_validos = ["Inventariado", "No Inventariado"]
    error = None

    if request.method == "POST":
        datos = obtener_datos_material_formulario()

        fotos = archivos_con_nombre(request.files.getlist("fotos"))
        pdfs = archivos_con_nombre(request.files.getlist("pdfs"))

        error = validar_material(
            datos,
            estados_validos,
            inventariado_validos,
            current_year
        )

        if not error:
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
                inventariado_validos=inventariado_validos,
                datos=datos,
                current_year=current_year,
                profesores=PROFESORES,
                max_archivos=app.config["MAX_ARCHIVOS_POR_TIPO"]
            )

        datos_profesor = PROFESORES.get(datos["doctor_responsable"])
        puesto_responsable = datos_profesor["puesto"] if datos_profesor else ""
        area_responsable = datos_profesor["area"] if datos_profesor else ""

        material.numero_serie = datos["numero_serie"]
        material.no_fabricante = datos["no_fabricante"]
        material.nombre_material = datos["nombre_material"]
        material.marca = datos["marca"]
        material.anio = int(datos["anio"]) if datos["anio"] else None
        material.descripcion = datos["descripcion"]
        material.software = datos["software"]
        material.inventariado = datos["inventariado"]
        material.no_inventario = datos["no_inventario"]
        material.doctor_responsable = datos["doctor_responsable"]
        material.puesto_responsable = puesto_responsable
        material.area_responsable = area_responsable
        material.ubicacion = datos["ubicacion"]
        material.estado_prestamo = datos["estado_prestamo"]

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
        inventariado_validos=inventariado_validos,
        datos={},
        current_year=current_year,
        profesores=PROFESORES,
        max_archivos=app.config["MAX_ARCHIVOS_POR_TIPO"]
    )


# ELIMINAR UNA FOTO ESPECÍFICA
@app.route("/materiales/foto/eliminar/<int:foto_id>", methods=["POST"])
@requiere_modo_edicion
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
@requiere_modo_edicion
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
@requiere_modo_edicion
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

# PLACEHOLDERS DE FACTURAS
@app.route("/facturas")
def listar_facturas():
    flash("Sección de facturas en construcción.", "info")
    return redirect(url_for("menu"))


@app.route("/facturas/buscar", methods=["GET", "POST"])
def buscar_factura():
    flash("Búsqueda de facturas en construcción.", "info")
    return redirect(url_for("menu"))


@app.route("/facturas/profesor", methods=["GET", "POST"])
def facturas_por_profesor():
    flash("Filtro de facturas por profesor en construcción.", "info")
    return redirect(url_for("menu"))


@app.route("/facturas/crear", methods=["GET", "POST"])
@requiere_modo_edicion
def crear_factura():
    flash("Registro de facturas en construcción.", "info")
    return redirect(url_for("menu"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)