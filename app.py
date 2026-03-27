from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta_laboratorio"

basedir = os.path.abspath(os.path.dirname(__file__))

FOTOS_FOLDER = os.path.join(basedir, 'static', 'uploads', 'fotos')
PDFS_FOLDER = os.path.join(basedir, 'static', 'uploads', 'pdfs')
app.config['FOTOS_FOLDER'] = FOTOS_FOLDER
app.config['PDFS_FOLDER'] = PDFS_FOLDER
os.makedirs(FOTOS_FOLDER, exist_ok=True)
os.makedirs(PDFS_FOLDER, exist_ok=True)

def eliminar_archivo_local(ruta_relativa):
    if not ruta_relativa:
        return
    if not str(ruta_relativa).startswith('http'):
        path_absoluta = os.path.join(basedir, 'static', ruta_relativa)
        if os.path.exists(path_absoluta):
            try:
                os.remove(path_absoluta)
            except Exception as e:
                print(f"Error al eliminar {path_absoluta}: {e}")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
        numero_serie = request.form["numero_serie"].strip()
        marca = request.form["marca"].strip()
        doctor_responsable = request.form["doctor_responsable"].strip()
        nombre_material = request.form["nombre_material"].strip()
        anio = request.form["anio"].strip()
        ubicacion = request.form["ubicacion"].strip()
        estado_prestamo = request.form["estado_prestamo"].strip()

        # Handle Files
        foto_file = request.files.get("foto")
        pdf_file = request.files.get("pdf_especificaciones")
        foto_path = None
        pdf_path = None

        if foto_file and foto_file.filename:
            filename = secure_filename(foto_file.filename)
            foto_file.save(os.path.join(app.config['FOTOS_FOLDER'], filename))
            foto_path = f"uploads/fotos/{filename}"

        if pdf_file and pdf_file.filename:
            filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(app.config['PDFS_FOLDER'], filename))
            pdf_path = f"uploads/pdfs/{filename}"

        if not numero_serie or not marca or not doctor_responsable or not nombre_material or not anio or not ubicacion or not estado_prestamo:
            error = "Todos los campos obligatorios deben estar llenos."
        elif not anio.isdigit():
            error = "El año debe ser un número entero."
        elif int(anio) > datetime.now().year:
            error = "El año no puede ser mayor al actual."
        elif estado_prestamo not in estados_validos:
            error = "El estado seleccionado no es válido."
        elif Material.query.filter_by(numero_serie=numero_serie).first():
            error = "Ya existe un material con ese número de serie."
        else:
            nuevo_material = Material(
                numero_serie=numero_serie,
                marca=marca,
                foto=foto_path,
                doctor_responsable=doctor_responsable,
                nombre_material=nombre_material,
                anio=int(anio),
                ubicacion=ubicacion,
                estado_prestamo=estado_prestamo,
                pdf_especificaciones=pdf_path
            )

            db.session.add(nuevo_material)
            db.session.commit()
            flash("Material registrado correctamente.", "success")
            return redirect(url_for("listar_materiales"))

        return render_template(
            "materiales/crear.html",
            error=error,
            estados_validos=estados_validos,
            datos=request.form,
            current_year=current_year
            
        )

    return render_template(
        "materiales/crear.html",
        error=error,
        estados_validos=estados_validos,
        datos={},
        current_year=datetime.now().year
    )

# BUSCAR MATERIAL
@app.route("/materiales/buscar", methods=["GET", "POST"])
def buscar_material():
    resultados = []
    busqueda = ""
    error = None

    if request.method == "POST":
        busqueda = request.form["busqueda"].strip()

        if not busqueda:
            error = "Debes escribir algo para buscar"
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
        profesor_buscado = request.form["doctor_responsable"].strip()

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

#EDITAR MATERIAL
@app.route("/materiales/editar/<int:id>", methods=["GET", "POST"])
def editar_material(id):
    current_year = datetime.now().year
    material = Material.query.get_or_404(id)

    estados_validos = ["Disponible", "En préstamo", "Fuera de servicio", "En mantenimiento"]
    error = None

    if request.method == "POST":
        numero_serie = request.form["numero_serie"].strip()
        marca = request.form["marca"].strip()
        doctor_responsable = request.form["doctor_responsable"].strip()
        nombre_material = request.form["nombre_material"].strip()
        anio = request.form["anio"].strip()
        ubicacion = request.form["ubicacion"].strip()
        estado_prestamo = request.form["estado_prestamo"].strip()

        foto_file = request.files.get("foto")
        pdf_file = request.files.get("pdf_especificaciones")

        if not numero_serie or not marca or not doctor_responsable or not nombre_material or not anio or not ubicacion or not estado_prestamo:
            error = "Todos los campos obligatorios deben estar llenos."
        elif not anio.isdigit():
            error = "El año debe ser un número entero."
        elif int(anio) > datetime.now().year:
            error = "El año no puede ser mayor al actual."
        elif estado_prestamo not in estados_validos:
            error = "El estado seleccionado no es válido."
        else:
            material_con_mismo_numero = Material.query.filter_by(numero_serie=numero_serie).first()

            if material_con_mismo_numero and material_con_mismo_numero.id != material.id:
                error = "Ya existe otro material con ese número de serie."
            else:
                material.numero_serie = numero_serie
                material.marca = marca
                material.doctor_responsable = doctor_responsable
                material.nombre_material = nombre_material
                material.anio = int(anio)
                material.ubicacion = ubicacion
                material.estado_prestamo = estado_prestamo

                if foto_file and foto_file.filename:
                    eliminar_archivo_local(material.foto)
                    filename = secure_filename(foto_file.filename)
                    foto_file.save(os.path.join(app.config['FOTOS_FOLDER'], filename))
                    material.foto = f"uploads/fotos/{filename}"

                if pdf_file and pdf_file.filename:
                    eliminar_archivo_local(material.pdf_especificaciones)
                    filename = secure_filename(pdf_file.filename)
                    pdf_file.save(os.path.join(app.config['PDFS_FOLDER'], filename))
                    material.pdf_especificaciones = f"uploads/pdfs/{filename}"

                db.session.commit()
                flash("Material actualizado correctamente.", "success")
                return redirect(url_for("listar_materiales"))

        return render_template(
            "materiales/editar.html",
            material=material,
            error=error,
            estados_validos=estados_validos,
            datos=request.form,
            current_year = datetime.now().year
        )

    return render_template(
        "materiales/editar.html",
        material=material,
        error=error,
        estados_validos=estados_validos,
        datos={},
        current_year=datetime.now().year
    )

@app.route("/materiales/eliminar/<int:id>", methods=["POST"])
def eliminar_material(id):
        material = Material.query.get_or_404(id)
        eliminar_archivo_local(material.foto)
        eliminar_archivo_local(material.pdf_especificaciones)
        db.session.delete(material)
        db.session.commit()
        flash("Material eliminado correctamente.", "success")
        return redirect(url_for("listar_materiales"))

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)