from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
from uuid import uuid4
import os
import json
import zipfile
import shutil
import tempfile
import sqlite3

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, legal, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

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

PRESUPUESTOS_FACTURA = [
    "Secihti",
    "POA",
    "Fondo Fijo",
    "VIEP",
    "PROME",
    "PFCE-PIFI"
]

MESES_FACTURA = [
    {"valor": "1", "nombre": "Enero"},
    {"valor": "2", "nombre": "Febrero"},
    {"valor": "3", "nombre": "Marzo"},
    {"valor": "4", "nombre": "Abril"},
    {"valor": "5", "nombre": "Mayo"},
    {"valor": "6", "nombre": "Junio"},
    {"valor": "7", "nombre": "Julio"},
    {"valor": "8", "nombre": "Agosto"},
    {"valor": "9", "nombre": "Septiembre"},
    {"valor": "10", "nombre": "Octubre"},
    {"valor": "11", "nombre": "Noviembre"},
    {"valor": "12", "nombre": "Diciembre"},
]


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

        anio = int(datos["anio"])

        if anio < 1990:
            return "El año no puede ser menor a 1990."

        if anio > current_year:
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

def texto_pdf(valor):
    if valor is None:
        return "-"

    valor = str(valor).strip()

    if not valor:
        return "-"

    return valor


def parrafo_pdf(valor, estilo):
    return Paragraph(escape(texto_pdf(valor)), estilo)


def agregar_pie_pagina_pdf(canvas, doc):
    canvas.saveState()

    if getattr(doc, "titulo_pdf", None):
        canvas.setTitle(doc.titulo_pdf)

    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#64748B"))

    canvas.drawString(
        0.35 * inch,
        0.22 * inch,
        "Sistema de Gestion de Laboratorio"
    )

    canvas.drawRightString(
        landscape(legal)[0] - 0.35 * inch,
        0.22 * inch,
        f"Pagina {doc.page}"
    )

    canvas.restoreState()


def construir_pdf_inventario_docente(profesor, materiales):
    buffer = BytesIO()

    titulo_pdf = f"Inventario de Docente - {profesor}"

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(legal),
        rightMargin=0.35 * inch,
        leftMargin=0.35 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.45 * inch
    )

    doc.titulo_pdf = titulo_pdf

    estilos = getSampleStyleSheet()
    ancho_total = doc.width

    titulo_style = ParagraphStyle(
        "TituloInventario",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=22,
        alignment=1,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=2
    )

    subtitulo_style = ParagraphStyle(
        "SubtituloInventario",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        alignment=1,
        textColor=colors.HexColor("#475569"),
        spaceAfter=16
    )

    info_style = ParagraphStyle(
        "InfoInventario",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11.2,
        textColor=colors.HexColor("#0F172A")
    )

    encabezado_style = ParagraphStyle(
        "EncabezadoTablaInventario",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=9.2,
        alignment=1,
        textColor=colors.white
    )

    celda_style = ParagraphStyle(
        "CeldaTablaInventario",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=9.3,
        textColor=colors.HexColor("#0F172A")
    )

    celda_centro_style = ParagraphStyle(
        "CeldaCentroTablaInventario",
        parent=celda_style,
        alignment=1
    )

    elementos = []

    datos_profesor = PROFESORES.get(profesor, {})
    fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")

    elementos.append(Paragraph("Laboratiorio de Electrónica y Optoelectrónica", titulo_style))
    elementos.append(Paragraph("Reporte general de materiales asignados", subtitulo_style))

    info_data = [
        [
            Paragraph(f"<b>Profesor:</b> {escape(texto_pdf(profesor))}", info_style),
            Paragraph(f"<b>Puesto:</b> {escape(texto_pdf(datos_profesor.get('puesto')))}", info_style),
            Paragraph(f"<b>Area:</b> {escape(texto_pdf(datos_profesor.get('area')))}", info_style),
        ],
        [
            Paragraph(f"<b>Fecha de generacion:</b> {escape(fecha_generacion)}", info_style),
            Paragraph(f"<b>Total de materiales:</b> {escape(str(len(materiales)))}", info_style),
            Paragraph("<b>Tipo de reporte:</b> Inventario por docente", info_style),
        ],
    ]

    info_table = Table(
        info_data,
        colWidths=[
            ancho_total / 3,
            ancho_total / 3,
            ancho_total / 3
        ]
    )

    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    elementos.append(info_table)
    elementos.append(Spacer(1, 16))

    encabezados = [
        "Material",
        "Descripcion",
        "Marca",
        "No. Serie",
        "No. Fabricante",
        "Inventariado",
        "No. Inventario",
        "Fecha",
        "Ubicacion",
        "Estado"
    ]

    tabla_datos = [
        [Paragraph(escape(encabezado), encabezado_style) for encabezado in encabezados]
    ]

    for material in materiales:
        tabla_datos.append([
            parrafo_pdf(material.nombre_material or "Sin nombre", celda_style),
            parrafo_pdf(material.descripcion, celda_style),
            parrafo_pdf(material.marca, celda_style),
            parrafo_pdf(material.numero_serie, celda_style),
            parrafo_pdf(material.no_fabricante, celda_style),
            parrafo_pdf(material.inventariado, celda_centro_style),
            parrafo_pdf(material.no_inventario, celda_style),
            parrafo_pdf(material.anio, celda_centro_style),
            parrafo_pdf(material.ubicacion, celda_style),
            parrafo_pdf(material.estado_prestamo, celda_centro_style),
        ])

    tabla = Table(
        tabla_datos,
        repeatRows=1,
        colWidths=[
            1.40 * inch,  # Material
            3.05 * inch,  # Descripcion
            1.15 * inch,  # Marca
            1.20 * inch,  # No. Serie
            1.30 * inch,  # No. Fabricante
            1.15 * inch,  # Inventariado
            1.25 * inch,  # No. Inventario
            0.80 * inch,  # Fecha
            1.20 * inch,  # Ubicacion
            0.80 * inch,  # Estado
        ]
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A237E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, 0), 0.45, colors.HexColor("#0F172A")),
    ]))

    elementos.append(tabla)

    doc.build(
        elementos,
        onFirstPage=agregar_pie_pagina_pdf,
        onLaterPages=agregar_pie_pagina_pdf
    )

    buffer.seek(0)

    return buffer


def obtener_datos_factura_formulario():
    return {
        "doctor_responsable": request.form.get("doctor_responsable", "").strip(),
        "presupuesto": request.form.get("presupuesto", "").strip(),
        "fecha_factura": request.form.get("fecha_factura", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
    }


def convertir_fecha_factura(fecha_texto):
    if not fecha_texto:
        return None

    try:
        return datetime.strptime(fecha_texto, "%Y-%m-%d").date()
    except ValueError:
        return None

def obtener_anios_facturas():
    fechas = db.session.query(Factura.fecha_factura).filter(
        Factura.fecha_factura.isnot(None)
    ).all()

    return sorted(
        {fecha.year for (fecha,) in fechas if fecha},
        reverse=True
    )


def obtener_nombre_mes_factura(valor_mes):
    valor_mes = str(valor_mes)

    for mes in MESES_FACTURA:
        if mes["valor"] == valor_mes:
            return mes["nombre"]

    return ""


def obtener_rango_fecha_factura(anio, mes=None):
    anio = int(anio)

    if mes:
        mes = int(mes)

        fecha_inicio = datetime(anio, mes, 1).date()

        if mes == 12:
            fecha_fin = datetime(anio + 1, 1, 1).date()
        else:
            fecha_fin = datetime(anio, mes + 1, 1).date()

        return fecha_inicio, fecha_fin

    fecha_inicio = datetime(anio, 1, 1).date()
    fecha_fin = datetime(anio + 1, 1, 1).date()

    return fecha_inicio, fecha_fin


def validar_busqueda_factura(presupuesto, anio, mes):
    if not presupuesto and not anio and not mes:
        return "Selecciona al menos un criterio de búsqueda."

    if presupuesto and presupuesto not in PRESUPUESTOS_FACTURA:
        return "El presupuesto seleccionado no es válido."

    if mes and not anio:
        return "Para filtrar por mes, primero debes seleccionar un año."

    if anio:
        if not anio.isdigit():
            return "El año seleccionado no es válido."

        anio_numero = int(anio)
        anio_actual = datetime.now().year

        if anio_numero < 1900 or anio_numero > anio_actual:
            return "El año seleccionado no es válido."

    if mes:
        if not mes.isdigit():
            return "El mes seleccionado no es válido."

        mes_numero = int(mes)

        if mes_numero < 1 or mes_numero > 12:
            return "El mes seleccionado no es válido."

    return None


def construir_resumen_busqueda_factura(presupuesto, anio, mes):
    criterios = []

    if presupuesto:
        criterios.append(f"Presupuesto: {presupuesto}")

    if anio:
        criterios.append(f"Año: {anio}")

    if mes:
        nombre_mes = obtener_nombre_mes_factura(mes)

        if nombre_mes:
            criterios.append(f"Mes: {nombre_mes}")

    return " · ".join(criterios)


def validar_pdf_factura(pdf, obligatorio=False):
    if obligatorio and (not pdf or not pdf.filename):
        return "Debes subir el PDF de la factura."

    if not pdf or not pdf.filename:
        return None

    filename = secure_filename(pdf.filename)

    if not extension_permitida(filename, app.config["EXTENSIONES_PDFS"]):
        return "Solo se permiten archivos PDF."

    return None


def validar_factura(datos, presupuestos_validos, pdf=None, pdf_obligatorio=False):
    if not datos["doctor_responsable"]:
        return "Debes seleccionar un profesor responsable."

    if datos["doctor_responsable"] not in PROFESORES:
        return "El profesor seleccionado no es válido."

    if not datos["presupuesto"]:
        return "Debes seleccionar de qué presupuesto sale la factura."

    if datos["presupuesto"] not in presupuestos_validos:
        return "El presupuesto seleccionado no es válido."

    if datos["fecha_factura"]:
        fecha_val = convertir_fecha_factura(datos["fecha_factura"])
        if not fecha_val:
            return "La fecha de la factura no es válida."
        if fecha_val > datetime.now().date():
            return "La fecha de la factura no puede ser posterior al día de hoy."

    error_pdf = validar_pdf_factura(pdf, obligatorio=pdf_obligatorio)
    if error_pdf:
        return error_pdf

    return None


def guardar_pdf_factura(pdf):
    return guardar_archivo(
        pdf,
        "UPLOAD_FOLDER_FACTURAS",
        "uploads/facturas"
    )

# ==========================
# RESPALDOS DEL SISTEMA
# ==========================

def generar_nombre_respaldo():
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"backup_laboratorio_{fecha}.zip"


def obtener_ruta_database():
    return os.path.join(app.root_path, "database.db")


def normalizar_ruta_zip(ruta):
    return ruta.replace(os.sep, "/")


def agregar_archivo_a_zip(zip_file, ruta_absoluta, ruta_en_zip):
    if not os.path.isfile(ruta_absoluta):
        return False

    zip_file.write(
        ruta_absoluta,
        normalizar_ruta_zip(ruta_en_zip)
    )

    return True


def agregar_carpeta_a_zip(zip_file, carpeta_absoluta, carpeta_en_zip):
    carpeta_en_zip = normalizar_ruta_zip(carpeta_en_zip).strip("/") + "/"
    total_archivos = 0

    zip_file.writestr(carpeta_en_zip, "")

    if not os.path.isdir(carpeta_absoluta):
        return total_archivos

    for raiz, _, archivos in os.walk(carpeta_absoluta):
        ruta_relativa_carpeta = os.path.relpath(raiz, carpeta_absoluta)

        if ruta_relativa_carpeta != ".":
            ruta_carpeta_zip = normalizar_ruta_zip(
                os.path.join(carpeta_en_zip, ruta_relativa_carpeta)
            ).strip("/") + "/"

            zip_file.writestr(ruta_carpeta_zip, "")

        for archivo in archivos:
            ruta_absoluta_archivo = os.path.join(raiz, archivo)
            ruta_relativa_archivo = os.path.relpath(
                ruta_absoluta_archivo,
                carpeta_absoluta
            )

            ruta_archivo_zip = normalizar_ruta_zip(
                os.path.join(carpeta_en_zip, ruta_relativa_archivo)
            )

            zip_file.write(ruta_absoluta_archivo, ruta_archivo_zip)
            total_archivos += 1

    return total_archivos


def generar_metadata_respaldo(nombre_respaldo, conteos, archivos_incluidos):
    return {
        "tipo": "backup_laboratorio",
        "version_formato": 1,
        "nombre_archivo": nombre_respaldo,
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "incluye": [
            "database.db",
            "uploads/fotos",
            "uploads/pdfs",
            "uploads/facturas"
        ],
        "conteos": conteos,
        "archivos_incluidos": archivos_incluidos
    }


def construir_zip_respaldo(nombre_respaldo):
    ruta_db = obtener_ruta_database()

    if not os.path.isfile(ruta_db):
        raise FileNotFoundError("No se encontró database.db.")

    conteos = {
        "materiales": Material.query.count(),
        "facturas": Factura.query.count()
    }

    # Cerramos la sesión antes de leer/copiar la base SQLite.
    db.session.remove()

    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        archivo_db_incluido = agregar_archivo_a_zip(
            zip_file,
            ruta_db,
            "database.db"
        )

        if not archivo_db_incluido:
            raise FileNotFoundError("No se pudo agregar database.db al respaldo.")

        zip_file.writestr("uploads/", "")

        archivos_fotos = agregar_carpeta_a_zip(
            zip_file,
            app.config["UPLOAD_FOLDER_FOTOS"],
            "uploads/fotos"
        )

        archivos_pdfs = agregar_carpeta_a_zip(
            zip_file,
            app.config["UPLOAD_FOLDER_PDFS"],
            "uploads/pdfs"
        )

        archivos_facturas = agregar_carpeta_a_zip(
            zip_file,
            app.config["UPLOAD_FOLDER_FACTURAS"],
            "uploads/facturas"
        )

        archivos_incluidos = {
            "fotos": archivos_fotos,
            "pdfs_materiales": archivos_pdfs,
            "pdfs_facturas": archivos_facturas
        }

        metadata = generar_metadata_respaldo(
            nombre_respaldo,
            conteos,
            archivos_incluidos
        )

        zip_file.writestr(
            "metadata.json",
            json.dumps(metadata, ensure_ascii=False, indent=2)
        )

    buffer.seek(0)

    return buffer

def obtener_ruta_uploads():
    return os.path.join(app.static_folder, "uploads")


def obtener_ruta_backups_automaticos():
    ruta = os.path.join(app.root_path, "backups")
    os.makedirs(ruta, exist_ok=True)
    return ruta


def asegurar_carpetas_uploads():
    os.makedirs(app.config["UPLOAD_FOLDER_FOTOS"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER_PDFS"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER_FACTURAS"], exist_ok=True)


def generar_nombre_respaldo_automatico():
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"autobackup_antes_importar_{fecha}.zip"


def limpiar_respaldos_automaticos(limite=10):
    ruta_backups = obtener_ruta_backups_automaticos()

    respaldos = []

    for nombre in os.listdir(ruta_backups):
        if nombre.startswith("autobackup_antes_importar_") and nombre.endswith(".zip"):
            ruta = os.path.join(ruta_backups, nombre)

            if os.path.isfile(ruta):
                respaldos.append((ruta, os.path.getmtime(ruta)))

    respaldos.sort(key=lambda item: item[1], reverse=True)

    for ruta, _ in respaldos[limite:]:
        try:
            os.remove(ruta)
        except OSError as error:
            print(f"No se pudo eliminar respaldo automático antiguo {ruta}: {error}")


def crear_respaldo_automatico_pre_importacion():
    ruta_backups = obtener_ruta_backups_automaticos()
    nombre_respaldo = generar_nombre_respaldo_automatico()
    ruta_respaldo = os.path.join(ruta_backups, nombre_respaldo)

    zip_buffer = construir_zip_respaldo(nombre_respaldo)

    with open(ruta_respaldo, "wb") as archivo:
        archivo.write(zip_buffer.getvalue())

    limpiar_respaldos_automaticos(limite=10)

    return ruta_respaldo


def nombre_zip_seguro(nombre):
    nombre_normalizado = nombre.replace("\\", "/")

    if not nombre_normalizado:
        return False

    if nombre_normalizado.startswith("/"):
        return False

    if nombre_normalizado.startswith("../"):
        return False

    partes = nombre_normalizado.split("/")

    if ".." in partes:
        return False

    if partes[0].endswith(":"):
        return False

    return True


def validar_estructura_zip_respaldo(ruta_zip):
    if not zipfile.is_zipfile(ruta_zip):
        return "El archivo seleccionado no es un ZIP válido."

    try:
        with zipfile.ZipFile(ruta_zip, "r") as zip_file:
            archivo_danado = zip_file.testzip()

            if archivo_danado:
                return f"El respaldo contiene un archivo dañado: {archivo_danado}"

            nombres = zip_file.namelist()

            for nombre in nombres:
                if not nombre_zip_seguro(nombre):
                    return "El ZIP contiene rutas no seguras y no puede importarse."

            nombres_normalizados = {nombre.replace("\\", "/") for nombre in nombres}

            if "database.db" not in nombres_normalizados:
                return "El respaldo no contiene database.db."

            tiene_uploads = any(
                nombre == "uploads/" or nombre.startswith("uploads/")
                for nombre in nombres_normalizados
            )

            if not tiene_uploads:
                return "El respaldo no contiene la carpeta uploads."

    except zipfile.BadZipFile:
        return "El archivo seleccionado no es un ZIP válido."

    return None


def validar_database_importada(ruta_db):
    if not os.path.isfile(ruta_db):
        return "No se encontró database.db dentro del respaldo."

    try:
        conexion = sqlite3.connect(ruta_db)
        cursor = conexion.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = {fila[0] for fila in cursor.fetchall()}

        conexion.close()
    except sqlite3.Error:
        return "database.db no es una base SQLite válida."

    tablas_requeridas = {
        "material",
        "material_foto",
        "material_pdf",
        "factura"
    }

    faltantes = tablas_requeridas - tablas

    if faltantes:
        faltantes_texto = ", ".join(sorted(faltantes))
        return f"La base de datos del respaldo no tiene las tablas requeridas: {faltantes_texto}."

    return None


def extraer_zip_respaldo(ruta_zip, carpeta_destino):
    with zipfile.ZipFile(ruta_zip, "r") as zip_file:
        zip_file.extractall(carpeta_destino)


def restaurar_respaldo_extraido(carpeta_extraida):
    ruta_db_nueva = os.path.join(carpeta_extraida, "database.db")
    ruta_uploads_nueva = os.path.join(carpeta_extraida, "uploads")

    ruta_db_actual = obtener_ruta_database()
    ruta_uploads_actual = obtener_ruta_uploads()

    db.session.remove()
    db.engine.dispose()

    if os.path.exists(ruta_db_actual):
        os.remove(ruta_db_actual)

    shutil.copy2(ruta_db_nueva, ruta_db_actual)

    if os.path.isdir(ruta_uploads_actual):
        shutil.rmtree(ruta_uploads_actual)

    if os.path.isdir(ruta_uploads_nueva):
        shutil.copytree(ruta_uploads_nueva, ruta_uploads_actual)
    else:
        os.makedirs(ruta_uploads_actual, exist_ok=True)

    asegurar_carpetas_uploads()

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
    page = request.args.get('page', 1, type=int)
    paginacion = Material.query.paginate(page=page, per_page=15, error_out=False)
    materiales = paginacion.items
    total_materiales = paginacion.total

    return render_template(
        "materiales/lista.html",
        materiales=materiales,
        total_materiales=total_materiales,
        paginacion=paginacion
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
    paginacion = None

    if request.method == "POST" or (request.method == "GET" and request.args.get("busqueda")):
        busqueda = (request.form.get("busqueda") or request.args.get("busqueda", "")).strip()

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

            query = Material.query.filter(
                filtros[0] |
                filtros[1] |
                filtros[2] |
                filtros[3] |
                filtros[4] |
                (filtros[5] if len(filtros) > 5 else False)
            )

            page = request.args.get('page', 1, type=int)
            paginacion = query.paginate(page=page, per_page=15, error_out=False)
            resultados = paginacion.items

    return render_template(
        "materiales/buscar.html",
        resultados=resultados,
        busqueda=busqueda,
        error=error,
        paginacion=paginacion
    )


# VER MATERIALES POR PROFESOR
@app.route("/materiales/profesor", methods=["GET", "POST"])
def materiales_por_profesor():
    resultados = []
    profesor_buscado = ""
    error = None
    paginacion = None

    if request.method == "POST" or (request.method == "GET" and request.args.get("doctor_responsable")):
        profesor_buscado = (request.form.get("doctor_responsable") or request.args.get("doctor_responsable", "")).strip()

        if not profesor_buscado:
            error = "Debes seleccionar un profesor."
        elif profesor_buscado not in PROFESORES:
            error = "El profesor seleccionado no es válido."
        else:
            query = Material.query.filter_by(
                doctor_responsable=profesor_buscado
            )
            page = request.args.get('page', 1, type=int)
            paginacion = query.paginate(page=page, per_page=15, error_out=False)
            resultados = paginacion.items

    return render_template(
        "materiales/profesor.html",
        resultados=resultados,
        profesor_buscado=profesor_buscado,
        profesores=PROFESORES,
        error=error,
        paginacion=paginacion
    )


# IMPRIMIR INVENTARIO DE DOCENTE EN PDF
@app.route("/materiales/profesor/pdf")
def imprimir_inventario_docente():
    profesor = request.args.get("doctor_responsable", "").strip()

    if not profesor:
        flash("Debes seleccionar un profesor para generar el inventario.", "error")
        return redirect(url_for("materiales_por_profesor"))

    if profesor not in PROFESORES:
        flash("El profesor seleccionado no es válido.", "error")
        return redirect(url_for("materiales_por_profesor"))

    materiales = Material.query.filter_by(
        doctor_responsable=profesor
    ).order_by(Material.nombre_material.asc()).all()

    if not materiales:
        flash("No hay materiales para generar el inventario de este docente.", "error")
        return redirect(url_for("materiales_por_profesor"))

    pdf_buffer = construir_pdf_inventario_docente(profesor, materiales)

    nombre_archivo = secure_filename(f"inventario_{profesor}.pdf")

    if not nombre_archivo:
        nombre_archivo = "inventario_docente.pdf"

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=nombre_archivo
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

# LISTAR FACTURAS
@app.route("/facturas")
def listar_facturas():
    page = request.args.get('page', 1, type=int)
    paginacion = Factura.query.order_by(Factura.id.desc()).paginate(page=page, per_page=15, error_out=False)
    facturas = paginacion.items
    total_facturas = paginacion.total

    return render_template(
        "facturas/lista.html",
        facturas=facturas,
        total_facturas=total_facturas,
        paginacion=paginacion
    )


# CREAR FACTURA
@app.route("/facturas/crear", methods=["GET", "POST"])
@requiere_modo_edicion
def crear_factura():
    error = None
    datos = {}

    if request.method == "POST":
        datos = obtener_datos_factura_formulario()
        pdf = request.files.get("archivo_pdf")

        error = validar_factura(
            datos,
            PRESUPUESTOS_FACTURA,
            pdf=pdf,
            pdf_obligatorio=True
        )

        if error:
            return render_template(
                "facturas/crear.html",
                error=error,
                datos=datos,
                profesores=PROFESORES,
                presupuestos=PRESUPUESTOS_FACTURA
            )

        datos_profesor = PROFESORES.get(datos["doctor_responsable"])
        puesto_responsable = datos_profesor["puesto"] if datos_profesor else ""
        area_responsable = datos_profesor["area"] if datos_profesor else ""

        ruta_pdf = guardar_pdf_factura(pdf)

        nueva_factura = Factura(
            doctor_responsable=datos["doctor_responsable"],
            puesto_responsable=puesto_responsable,
            area_responsable=area_responsable,
            presupuesto=datos["presupuesto"],
            fecha_factura=convertir_fecha_factura(datos["fecha_factura"]),
            descripcion=datos["descripcion"],
            archivo_pdf=ruta_pdf
        )

        db.session.add(nueva_factura)
        db.session.commit()

        flash("Factura registrada correctamente.", "success")
        return redirect(url_for("listar_facturas"))

    return render_template(
        "facturas/crear.html",
        error=error,
        datos=datos,
        profesores=PROFESORES,
        presupuestos=PRESUPUESTOS_FACTURA
    )


# BUSCAR FACTURA
@app.route("/facturas/buscar", methods=["GET", "POST"])
def buscar_factura():
    resultados = []
    error = None
    paginacion = None

    presupuesto_buscado = (
        request.form.get("presupuesto")
        or request.args.get("presupuesto", "")
    ).strip()

    anio_buscado = (
        request.form.get("anio_factura")
        or request.args.get("anio_factura", "")
    ).strip()

    mes_buscado = (
        request.form.get("mes_factura")
        or request.args.get("mes_factura", "")
    ).strip()

    busqueda_realizada = bool(
        presupuesto_buscado or anio_buscado or mes_buscado
    )

    if request.method == "POST" or busqueda_realizada:
        error = validar_busqueda_factura(
            presupuesto_buscado,
            anio_buscado,
            mes_buscado
        )

        if not error:
            query = Factura.query

            if presupuesto_buscado:
                query = query.filter(Factura.presupuesto == presupuesto_buscado)

            if anio_buscado:
                fecha_inicio, fecha_fin = obtener_rango_fecha_factura(
                    anio_buscado,
                    mes_buscado if mes_buscado else None
                )

                query = query.filter(
                    Factura.fecha_factura >= fecha_inicio,
                    Factura.fecha_factura < fecha_fin
                )

            query = query.order_by(Factura.id.desc())

            page = request.args.get("page", 1, type=int)

            if request.method == "POST":
                page = 1

            paginacion = query.paginate(
                page=page,
                per_page=10,
                error_out=False
            )

            resultados = paginacion.items

    anios_factura = obtener_anios_facturas()

    if anio_buscado and anio_buscado.isdigit():
        anio_numero = int(anio_buscado)

        if anio_numero not in anios_factura:
            anios_factura.append(anio_numero)
            anios_factura = sorted(anios_factura, reverse=True)

    resumen_busqueda = construir_resumen_busqueda_factura(
        presupuesto_buscado,
        anio_buscado,
        mes_buscado
    )

    return render_template(
        "facturas/buscar.html",
        resultados=resultados,
        error=error,
        paginacion=paginacion,
        presupuestos=PRESUPUESTOS_FACTURA,
        meses_factura=MESES_FACTURA,
        anios_factura=anios_factura,
        presupuesto_buscado=presupuesto_buscado,
        anio_buscado=anio_buscado,
        mes_buscado=mes_buscado,
        resumen_busqueda=resumen_busqueda,
        busqueda_realizada=busqueda_realizada
    )

# VER FACTURAS POR PROFESOR
@app.route("/facturas/profesor", methods=["GET", "POST"])
def facturas_por_profesor():
    resultados = []
    profesor_buscado = ""
    error = None
    paginacion = None

    if request.method == "POST" or (request.method == "GET" and request.args.get("doctor_responsable")):
        profesor_buscado = (request.form.get("doctor_responsable") or request.args.get("doctor_responsable", "")).strip()

        if not profesor_buscado:
            error = "Debes seleccionar un profesor."
        elif profesor_buscado not in PROFESORES:
            error = "El profesor seleccionado no es válido."
        else:
            query = Factura.query.filter_by(
                doctor_responsable=profesor_buscado
            ).order_by(Factura.id.desc())

            page = request.args.get('page', 1, type=int)
            paginacion = query.paginate(page=page, per_page=15, error_out=False)
            resultados = paginacion.items

    return render_template(
        "facturas/profesor.html",
        resultados=resultados,
        profesor_buscado=profesor_buscado,
        profesores=PROFESORES,
        error=error,
        paginacion=paginacion
    )


# EDITAR FACTURA
@app.route("/facturas/editar/<int:id>", methods=["GET", "POST"])
@requiere_modo_edicion
def editar_factura(id):
    factura = Factura.query.get_or_404(id)
    error = None
    datos = {}

    if request.method == "POST":
        datos = obtener_datos_factura_formulario()
        pdf = request.files.get("archivo_pdf")

        error = validar_factura(
            datos,
            PRESUPUESTOS_FACTURA,
            pdf=pdf,
            pdf_obligatorio=False
        )

        if error:
            return render_template(
                "facturas/editar.html",
                factura=factura,
                error=error,
                datos=datos,
                profesores=PROFESORES,
                presupuestos=PRESUPUESTOS_FACTURA
            )

        datos_profesor = PROFESORES.get(datos["doctor_responsable"])
        puesto_responsable = datos_profesor["puesto"] if datos_profesor else ""
        area_responsable = datos_profesor["area"] if datos_profesor else ""

        factura.doctor_responsable = datos["doctor_responsable"]
        factura.puesto_responsable = puesto_responsable
        factura.area_responsable = area_responsable
        factura.presupuesto = datos["presupuesto"]
        factura.fecha_factura = convertir_fecha_factura(datos["fecha_factura"])
        factura.descripcion = datos["descripcion"]

        if pdf and pdf.filename:
            ruta_pdf_anterior = factura.archivo_pdf
            ruta_pdf_nueva = guardar_pdf_factura(pdf)

            if ruta_pdf_nueva:
                factura.archivo_pdf = ruta_pdf_nueva
                eliminar_archivo_local(ruta_pdf_anterior)

        db.session.commit()

        flash("Factura actualizada correctamente.", "success")
        return redirect(url_for("listar_facturas"))

    return render_template(
        "facturas/editar.html",
        factura=factura,
        error=error,
        datos=datos,
        profesores=PROFESORES,
        presupuestos=PRESUPUESTOS_FACTURA
    )


# ELIMINAR PDF DE FACTURA
@app.route("/facturas/pdf/eliminar/<int:id>", methods=["POST"])
@requiere_modo_edicion
def eliminar_pdf_factura(id):
    factura = Factura.query.get_or_404(id)

    if factura.archivo_pdf:
        eliminar_archivo_local(factura.archivo_pdf)
        factura.archivo_pdf = None
        db.session.commit()
        flash("PDF de factura eliminado correctamente.", "success")
    else:
        flash("La factura no tiene PDF registrado.", "error")

    return redirect(url_for("editar_factura", id=factura.id))


# ELIMINAR FACTURA
@app.route("/facturas/eliminar/<int:id>", methods=["POST"])
@requiere_modo_edicion
def eliminar_factura(id):
    factura = Factura.query.get_or_404(id)

    if factura.archivo_pdf:
        eliminar_archivo_local(factura.archivo_pdf)

    db.session.delete(factura)
    db.session.commit()

    flash("Factura eliminada correctamente.", "success")
    return redirect(url_for("listar_facturas"))


# PLACEHOLDERS DE RESPALDOS
@app.route("/respaldos/exportar")
@requiere_modo_edicion
def exportar_respaldo():
    nombre_respaldo = generar_nombre_respaldo()

    try:
        zip_buffer = construir_zip_respaldo(nombre_respaldo)
    except Exception as error:
        print(f"Error al generar respaldo: {error}")
        flash("No se pudo generar el respaldo del sistema.", "error")
        return redirect(url_for("menu"))

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=nombre_respaldo
    )


@app.route("/respaldos/importar", methods=["GET", "POST"])
@requiere_modo_edicion
def importar_respaldo():
    if request.method == "GET":
        return render_template("respaldos/importar.html")

    archivo = request.files.get("archivo_respaldo")
    confirmacion = request.form.get("confirmar_importacion")

    if confirmacion != "si":
        flash("Debes confirmar que entiendes que se reemplazará la información actual.", "error")
        return redirect(url_for("importar_respaldo"))

    if not archivo or not archivo.filename:
        flash("Debes seleccionar un archivo de respaldo ZIP.", "error")
        return redirect(url_for("importar_respaldo"))

    filename = secure_filename(archivo.filename)

    if not filename.lower().endswith(".zip"):
        flash("El archivo de respaldo debe tener extensión .zip.", "error")
        return redirect(url_for("importar_respaldo"))

    with tempfile.TemporaryDirectory() as carpeta_temporal:
        ruta_zip = os.path.join(carpeta_temporal, filename)
        carpeta_extraida = os.path.join(carpeta_temporal, "respaldo_extraido")

        archivo.save(ruta_zip)

        error_zip = validar_estructura_zip_respaldo(ruta_zip)

        if error_zip:
            flash(error_zip, "error")
            return redirect(url_for("importar_respaldo"))

        os.makedirs(carpeta_extraida, exist_ok=True)
        extraer_zip_respaldo(ruta_zip, carpeta_extraida)

        ruta_db_importada = os.path.join(carpeta_extraida, "database.db")
        error_db = validar_database_importada(ruta_db_importada)

        if error_db:
            flash(error_db, "error")
            return redirect(url_for("importar_respaldo"))

        try:
            ruta_autobackup = crear_respaldo_automatico_pre_importacion()
            restaurar_respaldo_extraido(carpeta_extraida)
        except Exception as error:
            print(f"Error al importar respaldo: {error}")
            flash("Ocurrió un error al importar el respaldo. No se pudo completar la restauración.", "error")
            return redirect(url_for("importar_respaldo"))

    flash("Respaldo importado correctamente. Se generó una copia automática del estado anterior.", "success")
    return redirect(url_for("menu"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=False)