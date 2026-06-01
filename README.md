# Laboratiorio de Electrónica y Optoelectrónica

Aplicación web local desarrollada con Flask para administrar materiales de laboratorio, facturas, archivos PDF, fotografías y respaldos completos del sistema.

El sistema está diseñado para funcionar de forma local en una computadora, sin depender de internet, servidores externos ni cuentas de usuario. La información se guarda en una base de datos SQLite (`database.db`) y los archivos cargados se almacenan dentro de `static/uploads/`.

---

## 1. Funcionalidades principales

El sistema permite:

- Consultar materiales de laboratorio.
- Buscar materiales.
- Filtrar materiales por profesor.
- Registrar, editar y eliminar materiales.
- Subir varias fotos por material.
- Subir varios PDFs por material.
- Ver fotos y PDFs desde la aplicación.
- Eliminar fotos o PDFs individuales.
- Registrar, editar, buscar y eliminar facturas.
- Subir un PDF por factura.
- Filtrar facturas por profesor.
- Generar PDF de inventario por docente.
- Exportar respaldo completo del sistema.
- Importar respaldo completo del sistema.
- Trabajar en modo consulta o modo edición.

---

## 2. Cómo está guardada la información

La información del sistema se guarda en dos lugares:

```text
projecto/
├── database.db
└── static/
    └── uploads/
        ├── fotos/
        ├── pdfs/
        └── facturas/
```

### `database.db`

Contiene los registros del sistema:

- Materiales.
- Fotos asociadas a materiales.
- PDFs asociados a materiales.
- Facturas.

### `static/uploads/`

Contiene los archivos físicos cargados por el usuario:

- `static/uploads/fotos/`: fotografías de materiales.
- `static/uploads/pdfs/`: PDFs de materiales.
- `static/uploads/facturas/`: PDFs de facturas.

**Importante:** no basta con copiar solo `database.db`. Para mover el sistema completo a otra computadora se debe usar la función **Exportar respaldo** desde la aplicación.

---

## 3. Requisitos mínimos

### Sistema operativo recomendado

- Windows 10 o Windows 11.

También puede ejecutarse en macOS o Linux, pero las instrucciones principales de este README están pensadas para Windows.

### Software necesario

- Python 3.10 o 3.11.
- pip.
- Navegador web moderno: Chrome, Edge, Firefox o similar.
- Espacio libre en disco para fotos, PDFs, facturas y respaldos.

### Versión recomendada de Python

Se recomienda usar:

```text
Python 3.10.x o Python 3.11.x
```

Si la computadora tiene Python 3.12 o 3.13 y ocurre algún error instalando dependencias, se recomienda instalar Python 3.11 y crear el entorno virtual con esa versión.

---

## 4. Verificar si Python y pip están instalados

Abra **Símbolo del sistema** o **PowerShell** y ejecute:

```bat
python --version
pip --version
```

Si esos comandos no funcionan, pruebe:

```bat
py --version
py -m pip --version
```

### Caso A: la computadora ya tiene Python y pip correctos

Si ve algo parecido a esto:

```text
Python 3.10.x
```

o:

```text
Python 3.11.x
```

puede continuar con la instalación del proyecto.

### Caso B: la computadora no tiene Python

Si aparece un mensaje como:

```text
'python' no se reconoce como un comando interno o externo
```

o:

```text
Python was not found
```

instale Python antes de continuar.

Pasos recomendados en Windows:

1. Descargar Python desde el sitio oficial de Python.
2. Instalar Python 3.11.
3. Durante la instalación, activar la casilla:

```text
Add python.exe to PATH
```

4. Finalizar la instalación.
5. Cerrar y volver a abrir la terminal.
6. Verificar:

```bat
python --version
pip --version
```

Si `python` no funciona pero `py` sí funciona, use los comandos con `py` indicados más adelante.

### Caso C: la computadora tiene Python, pero está desactualizado

Si aparece algo como:

```text
Python 3.8.x
Python 3.9.x
```

o una versión anterior, instale Python 3.10 o 3.11.

Después de instalarlo, verifique si está disponible:

```bat
py -0
```

Si aparece Python 3.11 en la lista, puede crear el entorno virtual con:

```bat
py -3.11 -m venv venv
```

### Caso D: Python existe, pero pip no funciona

Pruebe:

```bat
python -m pip --version
```

Si no funciona, ejecute:

```bat
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel
```

Si usa `py`, ejecute:

```bat
py -m ensurepip --upgrade
py -m pip install --upgrade pip setuptools wheel
```

---

## 5. Instalación del sistema

### 5.1. Abrir la carpeta del proyecto

Coloque la carpeta del proyecto en una ubicación sencilla, por ejemplo:

```text
C:\Laboratorio\sistema_laboratorio
```

Abra una terminal dentro de esa carpeta.

En Windows puede hacerlo así:

1. Abrir la carpeta del proyecto.
2. Dar clic en la barra de dirección del Explorador de archivos.
3. Escribir `cmd`.
4. Presionar Enter.

También puede abrir PowerShell y moverse manualmente:

```bat
cd C:\Laboratorio\sistema_laboratorio
```

Si la ruta tiene espacios, use comillas:

```bat
cd "C:\Users\Usuario\Documents\Sistema Laboratorio"
```

---

## 6. Instalación rápida manual

Desde la carpeta raíz del proyecto, ejecute:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python app.py
```

Luego abra en el navegador:

```text
http://127.0.0.1:5000
```

---

## 7. Instalación usando `py` en Windows

Si `python` no funciona pero `py` sí funciona, use:

```bat
py -m venv venv
venv\Scripts\activate
py -m pip install --upgrade pip setuptools wheel
py -m pip install -r requirements.txt
py app.py
```

Si necesita forzar Python 3.11:

```bat
py -3.11 -m venv venv
venv\Scripts\activate
py -3.11 -m pip install --upgrade pip setuptools wheel
py -3.11 -m pip install -r requirements.txt
py -3.11 app.py
```

---

## 8. Instalación en macOS o Linux

Desde la carpeta raíz del proyecto:

```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
python3 app.py
```

Luego abra:

```text
http://127.0.0.1:5000
```

---

## 9. Si se incluye script de instalación

Si la carpeta del proyecto incluye un script como:

```text
instalar.bat
```

puede ejecutarse dando doble clic o desde terminal:

```bat
instalar.bat
```

Ese script debería encargarse de:

- Verificar Python.
- Crear el entorno virtual `venv`.
- Actualizar pip.
- Instalar dependencias desde `requirements.txt`.

Si el script falla, use la instalación manual de este README.

---

## 10. Si se incluye script de inicio

Si la carpeta del proyecto incluye un script como:

```text
iniciar.bat
```

puede ejecutarse dando doble clic o desde terminal:

```bat
iniciar.bat
```

Ese script debería encargarse de:

- Activar el entorno virtual.
- Ejecutar `python app.py`.
- Dejar el servidor local funcionando.

Después abra:

```text
http://127.0.0.1:5000
```

---

## 11. Ejecución diaria después de instalar

Una vez instalado, no es necesario repetir `pip install` cada vez.

Para abrir el sistema en días posteriores:

```bat
venv\Scripts\activate
python app.py
```

Luego abra el navegador en:

```text
http://127.0.0.1:5000
```

Para cerrar el sistema, vuelva a la terminal donde se está ejecutando Flask y presione:

```text
Ctrl + C
```

---

## 12. Modo consulta y modo edición

El sistema tiene dos modos:

### Modo consulta

Permite:

- Ver materiales.
- Buscar materiales.
- Filtrar por profesor.
- Ver fotos y PDFs.
- Ver facturas.
- Buscar facturas.
- Filtrar facturas por profesor.

No permite:

- Crear.
- Editar.
- Eliminar.
- Importar o exportar respaldos.

### Modo edición

Permite:

- Crear materiales.
- Editar materiales.
- Eliminar materiales.
- Eliminar fotos y PDFs individuales.
- Crear facturas.
- Editar facturas.
- Eliminar facturas.
- Exportar respaldos.
- Importar respaldos.

Para activar modo edición:

1. Dar clic en **Autenticarse**.
2. Escribir la contraseña configurada en `config.py`.
3. Confirmar.

La contraseña está en:

```text
config.py
```

en la variable:

```python
EDIT_PASSWORD
```

---

## 13. Respaldos del sistema

El sistema incluye un módulo de respaldos.

### Exportar respaldo

Genera un archivo `.zip` con:

```text
database.db
metadata.json
uploads/
├── fotos/
├── pdfs/
└── facturas/
```

Este respaldo puede guardarse donde el usuario quiera: USB, escritorio, Descargas, Drive, etc.

### Importar respaldo

Permite seleccionar un archivo `.zip` generado por el sistema y restaurarlo.

**Advertencia importante:** al importar un respaldo se reemplaza la información actual del sistema.

Antes de importar, el sistema genera automáticamente un respaldo interno del estado actual. Para evitar acumulación innecesaria, conserva solo los respaldos automáticos más recientes.

### Regla práctica para cambiar de computadora

Antes de salir de una computadora:

```text
Exportar respaldo
```

Al llegar a otra computadora:

```text
Importar respaldo
```

Así se mantiene la información completa, incluyendo base de datos, fotos y PDFs.

---

## 14. Archivos y carpetas que no deben borrarse

No borre manualmente:

```text
database.db
static/uploads/
backups/
```

### `database.db`

Contiene los registros.

### `static/uploads/`

Contiene las fotos y PDFs.

### `backups/`

Contiene respaldos automáticos generados antes de importar.

Si necesita mover la información, use la función **Exportar respaldo** desde el sistema.

---

## 15. Estructura general del proyecto

```text
proyecto/
├── app.py
├── models.py
├── config.py
├── database.db
├── requirements.txt
├── README.md
├── backups/
├── static/
│   ├── css/
│   │   ├── styles.css
│   │   └── dibujolab.png
│   ├── js/
│   │   ├── main.js
│   │   ├── materiales.js
│   │   └── facturas.js
│   └── uploads/
│       ├── fotos/
│       ├── pdfs/
│       └── facturas/
└── templates/
    ├── base.html
    ├── menu.html
    ├── materiales/
    ├── facturas/
    └── respaldos/
```

---

## 16. Dependencias principales

El proyecto usa principalmente:

- Flask.
- Flask-SQLAlchemy.
- SQLite.
- Jinja2.
- ReportLab.
- Werkzeug.

Las dependencias se instalan desde:

```text
requirements.txt
```

Comando de instalación:

```bat
python -m pip install -r requirements.txt
```

---

## 17. Problemas frecuentes y soluciones

### 17.1. `python` no se reconoce

Use:

```bat
py --version
```

Si `py` tampoco funciona, instale Python 3.10 o 3.11 y active la opción **Add Python to PATH** durante la instalación.

---

### 17.2. `pip` no se reconoce

Use:

```bat
python -m pip --version
```

Si no funciona:

```bat
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel
```

---

### 17.3. PowerShell no permite activar el entorno virtual

Si al ejecutar:

```bat
venv\Scripts\activate
```

aparece un error de permisos, puede usar Símbolo del sistema (`cmd`) en lugar de PowerShell, o ejecutar en PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Después cierre y vuelva a abrir PowerShell.

---

### 17.4. Error al instalar dependencias

Primero actualice pip:

```bat
python -m pip install --upgrade pip setuptools wheel
```

Luego intente de nuevo:

```bat
python -m pip install -r requirements.txt
```

Si el error está relacionado con la versión de Python, instale Python 3.11 y cree nuevamente el entorno virtual.

---

### 17.5. Error extraño al leer `requirements.txt`

Si pip muestra errores raros de codificación, caracteres nulos o mensajes similares a `UnicodeDecodeError`, es posible que `requirements.txt` esté guardado con una codificación incorrecta.

Solución recomendada:

1. Abrir `requirements.txt` en un editor como Visual Studio Code.
2. Guardarlo con codificación **UTF-8**.
3. Reintentar:

```bat
python -m pip install -r requirements.txt
```

---

### 17.6. La página no abre en el navegador

Verifique que la terminal muestre algo similar a:

```text
Running on http://127.0.0.1:5000
```

Luego abra:

```text
http://127.0.0.1:5000
```

Si no aparece ese mensaje, el servidor no está ejecutándose.

---

### 17.7. El puerto 5000 está ocupado

Si aparece un error indicando que el puerto está ocupado:

1. Cierre otras terminales donde se esté ejecutando el sistema.
2. Presione `Ctrl + C` en procesos anteriores.
3. Vuelva a ejecutar:

```bat
python app.py
```

Si el problema continúa, se puede cambiar el puerto al final de `app.py`, por ejemplo:

```python
app.run(debug=False, port=5001)
```

Luego abrir:

```text
http://127.0.0.1:5001
```

---

### 17.8. No aparecen fotos o PDFs

Revise que exista la carpeta:

```text
static/uploads/
```

con estas subcarpetas:

```text
fotos/
pdfs/
facturas/
```

Si movió el sistema a otra computadora, no copie solo `database.db`. Use **Exportar respaldo** e **Importar respaldo**.

---

### 17.9. Se perdió información después de importar

Importar un respaldo reemplaza la información actual.

Antes de importar, el sistema genera un respaldo automático interno en:

```text
backups/
```

Si necesita recuperar el estado anterior, localice el respaldo automático más reciente y vuelva a importarlo.

---

### 17.10. No puedo entrar al modo edición

Revise la contraseña configurada en:

```text
config.py
```

Variable:

```python
EDIT_PASSWORD
```

Si se modifica la contraseña, reinicie el servidor para asegurar que el cambio se aplique.

---

## 18. Recomendaciones de mantenimiento

- Hacer respaldos frecuentes.
- Exportar respaldo antes de mover el sistema a otra computadora.
- Importar únicamente respaldos generados por este sistema.
- No editar `database.db` manualmente.
- No mover ni renombrar manualmente archivos dentro de `static/uploads/`.
- No ejecutar varias instancias del sistema sobre la misma base de datos.
- Cerrar el sistema con `Ctrl + C` cuando termine de usarse.
- Guardar copias externas de los respaldos importantes.

---

## 19. Uso prolongado del sistema

Este sistema está preparado para uso local prolongado bajo estas condiciones:

- Uso en una computadora local.
- Uno o pocos usuarios, preferentemente uno escribiendo a la vez.
- Respaldo frecuente de la información.
- Archivos almacenados localmente.

El sistema no está diseñado para:

- Publicarse directamente en internet.
- Soportar muchos usuarios editando al mismo tiempo.
- Sincronizar automáticamente varias computadoras.
- Resolver conflictos entre versiones distintas de la base de datos.

Para trabajo entre varias computadoras, use siempre:

```text
Exportar respaldo → mover ZIP → Importar respaldo
```

---

## 20. Modo desarrollo y modo entrega

Durante desarrollo es común ejecutar Flask con:

```python
app.run(debug=True)
```

Para una entrega local más estable, se recomienda usar:

```python
app.run(debug=False)
```

Esto evita que el usuario final vea mensajes técnicos detallados en caso de error.

---

## 21. Comandos rápidos

### Crear entorno virtual

```bat
python -m venv venv
```

### Activar entorno virtual en Windows

```bat
venv\Scripts\activate
```

### Instalar dependencias

```bat
python -m pip install -r requirements.txt
```

### Ejecutar sistema

```bat
python app.py
```

### Abrir en navegador

```text
http://127.0.0.1:5000
```

### Cerrar sistema

```text
Ctrl + C
```

---

## 22. Nota final

Este sistema funciona como una aplicación local. La base de datos y los archivos viven en la computadora donde se ejecuta. Para conservar la información y moverla correctamente, use siempre el módulo de respaldos integrado.
