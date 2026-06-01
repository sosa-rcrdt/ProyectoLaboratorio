# Laboratorio de Electrónica y Optoelectrónica

Aplicación web local desarrollada con Flask para administrar materiales de laboratorio, facturas, archivos PDF, fotografías y respaldos completos del sistema.

El sistema está diseñado para funcionar en una computadora local, sin depender de internet, servidores externos ni cuentas de usuario. La información se guarda en una base de datos SQLite (`database.db`) y los archivos cargados se almacenan dentro de `static/uploads/`.

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
proyecto/
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

- Python 3.12.x recomendado.
- pip.
- Navegador web moderno: Chrome, Edge, Firefox o similar.
- Espacio libre en disco para fotos, PDFs, facturas y respaldos.

### Versión recomendada de Python

La versión probada y recomendada para este proyecto es:

```text
Python 3.12.x
```

El proyecto ya fue probado correctamente con Python 3.12. También debería funcionar con Python 3.13.x si las dependencias se instalan correctamente desde `requirements.txt`.

Para una instalación nueva en una computadora que no tenga Python, se recomienda instalar **Python 3.12.x** desde el sitio oficial y activar la opción **Add python.exe to PATH** durante la instalación.

### Versiones no recomendadas

No se recomienda usar:

```text
Python 3.10 o menor
```

El sistema podría funcionar en algunas versiones anteriores, pero para evitar problemas de compatibilidad se recomienda usar Python 3.12.x.

---

## 4. Dependencias del proyecto

El archivo `requirements.txt` debe contener las dependencias principales del sistema.

Contenido recomendado:

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.36
greenlet==3.1.1
reportlab==4.2.5
pillow==11.0.0
```

No es necesario listar manualmente dependencias internas como `Jinja2`, `Werkzeug`, `click`, `MarkupSafe`, `itsdangerous` o `blinker`, porque Flask las instala automáticamente en versiones compatibles.

---

## 5. Verificar si Python y pip están instalados

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

### Caso A: la computadora ya tiene Python compatible

Si aparece algo como:

```text
Python 3.12.x
```

puede continuar con la instalación del proyecto.

Si aparece:

```text
Python 3.13.x
```

también puede intentar continuar. Si ocurre algún problema al instalar dependencias, instale Python 3.12.x y repita la instalación.

### Caso B: la computadora no tiene Python

Si aparece un mensaje como:

```text
'python' no se reconoce como un comando interno o externo
```

or:

```text
Python was not found
```

instale Python antes de continuar.

Pasos recomendados en Windows:

1. Descargar Python 3.12.x desde el sitio oficial de Python.
2. Ejecutar el instalador.
3. Activar la casilla:

```text
Add python.exe to PATH
```

4. Continuar con la instalación.
5. Cerrar y volver a abrir la terminal.
6. Verificar:

```bat
python --version
pip --version
```

Si `python` no funciona pero `py` sí funciona, use los comandos con `py`.

### Caso C: la computadora tiene Python, pero está desactualizado

Si aparece algo como:

```text
Python 3.8.x
Python 3.9.x
Python 3.10.x
```

instale Python 3.12.x.

Después de instalarlo, verifique las versiones disponibles con:

```bat
py -0
```

Si aparece Python 3.12 en la lista, puede crear el entorno virtual con:

```bat
py -3.12 -m venv venv
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

## 6. Instalación inicial del sistema

La instalación inicial debe realizarla una persona encargada del equipo o del mantenimiento del proyecto. Esta instalación solo se realiza una vez por computadora.

El usuario final no necesita repetir estos pasos diariamente. Después de la instalación, bastará con ejecutar `iniciar.bat`.

### 6.1. Abrir la carpeta del proyecto

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

### 6.2. Crear entorno virtual

Con `python`:

```bat
python -m venv venv
```

Con `py` y Python 3.12:

```bat
py -3.12 -m venv venv
```

Si solo tiene una versión compatible de Python instalada, también puede usar:

```bat
py -3 -m venv venv
```

### 6.3. Activar entorno virtual

```bat
venv\Scripts\activate
```

### 6.4. Actualizar pip

```bat
python -m pip install --upgrade pip setuptools wheel
```

### 6.5. Instalar dependencias

```bat
python -m pip install -r requirements.txt
```

### 6.6. Verificar instalación

Ejecute:

```bat
python app.py
```

Cuando aparezca algo similar a:

```text
Running on http://127.0.0.1:5000
```

abra el navegador en:

```text
http://127.0.0.1:5000
```

Para detener esta prueba, cierre primero la pestaña del navegador y después cierre la ventana de la terminal, o use `Ctrl + C`.

---

## 7. Ejecución diaria con `iniciar.bat`

Después de que el sistema ya fue instalado en la computadora, el uso diario se realiza con:

```text
iniciar.bat
```

El archivo `iniciar.bat` sirve únicamente para iniciar el sistema. No instala dependencias ni crea el entorno virtual.

Este archivo se encarga de:

- Verificar que exista `app.py`.
- Verificar que exista el entorno virtual `venv`.
- Iniciar el servidor local.
- Abrir automáticamente el navegador en:

```text
http://127.0.0.1:5000
```

Mientras se use el sistema, la ventana negra de `iniciar.bat` debe permanecer abierta.

Si el navegador no se abre automáticamente, copie manualmente esta dirección en Chrome, Edge, Firefox o el navegador de su preferencia:

```text
http://127.0.0.1:5000
```

---

## 8. Cómo cerrar el sistema

La forma recomendada para usuarios finales es:

1. Cerrar la pestaña del navegador.
2. Cerrar la ventana negra de `iniciar.bat` con la **X**.

Si ya terminó de usar el sistema y no hay operaciones en curso, esto no debería afectar la base de datos ni los archivos guardados.

No cierre la ventana mientras el sistema esté:

- Guardando un material.
- Editando una factura.
- Eliminando información.
- Subiendo fotos o PDFs.
- Importando un respaldo.
- Exportando un respaldo.

### Cierre técnico alternativo

También puede cerrarse desde la ventana negra con:

```text
Ctrl + C
```

Si Windows pregunta:

```text
¿Desea terminar el trabajo por lotes (S/N)?
```

escriba:

```text
S
```

y presione Enter.

---

## 9. Instalación en macOS o Linux

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

El archivo `iniciar.bat` está pensado para Windows. En macOS o Linux se debe iniciar el sistema desde terminal con `python3 app.py`.

---

## 10. Modo consulta y modo edición

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

## 11. Respaldos del sistema

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

## 12. Archivos y carpetas que no deben borrarse

No borre manualmente:

```text
database.db
static/uploads/
backups/
venv/
```

### `database.db`

Contiene los registros.

### `static/uploads/`

Contiene las fotos y PDFs.

### `backups/`

Contiene respaldos automáticos generados antes de importar.

### `venv/`

Contiene el entorno virtual con las dependencias instaladas. Si se elimina, el sistema no podrá iniciar hasta que se vuelva a instalar el entorno.

Si necesita mover la información, use la función **Exportar respaldo** desde el sistema.

---

## 13. Estructura general del proyecto

```text
proyecto/
├── app.py
├── models.py
├── config.py
├── database.db
├── requirements.txt
├── README.md
├── iniciar.bat
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
├── templates/
│   ├── base.html
│   ├── menu.html
│   ├── materiales/
│   ├── facturas/
│   └── respaldos/
└── venv/
```

---

## 14. Problemas frecuentes y soluciones

### 14.1. `python` no se reconoce

Use:

```bat
py --version
```

Si `py` tampoco funciona, instale Python 3.12.x y active la opción **Add python.exe to PATH** durante la instalación.

---

### 14.2. `pip` no se reconoce

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

### 14.3. PowerShell no permite activar el entorno virtual

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

### 14.4. Error al instalar dependencias

Primero actualice pip:

```bat
python -m pip install --upgrade pip setuptools wheel
```

Luego intente de nuevo:

```bat
python -m pip install -r requirements.txt
```

Si aparece un error relacionado con `greenlet` o con compilación de dependencias, revise que `requirements.txt` use las versiones recomendadas de este README y que esté usando Python 3.12.x.

---

### 14.5. Error por versiones antiguas de dependencias

Si el proyecto tenía un `requirements.txt` antiguo con dependencias como:

```text
greenlet==2.0.2
SQLAlchemy==1.4.54
Flask-SQLAlchemy==3.0.5
setuptools==58.1.0
```

reemplace el contenido por el listado recomendado de este README.

Después elimine la carpeta `venv` y vuelva a realizar la instalación manual desde la sección **6. Instalación inicial del sistema**.

---

### 14.6. Error extraño al leer `requirements.txt`

Si pip muestra errores raros de codificación, caracteres nulos o mensajes similares a `UnicodeDecodeError`, es posible que `requirements.txt` esté guardado con una codificación incorrecta.

Solución recomendada:

1. Abrir `requirements.txt` en un editor como Visual Studio Code.
2. Guardarlo con codificación **UTF-8**.
3. Reintentar:

```bat
python -m pip install -r requirements.txt
```

---

### 14.7. `iniciar.bat` dice que no existe `venv`

Esto significa que el sistema todavía no fue instalado en esa computadora o que la carpeta `venv` fue eliminada.

Solución:

1. Realizar la instalación manual desde la sección **6. Instalación inicial del sistema**.
2. Verificar que exista:

```text
venv\Scripts\python.exe
```

3. Volver a ejecutar:

```text
iniciar.bat
```

---

### 14.8. La página no abre en el navegador

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

### 14.9. El navegador no se abrió automáticamente

Si usa `iniciar.bat` y el navegador no se abre automáticamente, abra manualmente:

```text
http://127.0.0.1:5000
```

---

### 14.10. El puerto 5000 está ocupado

Si aparece un error indicando que el puerto está ocupado:

1. Cierre otras terminales donde se esté ejecutando el sistema.
2. Cierre otras ventanas de `iniciar.bat`.
3. Vuelva a ejecutar:

```text
iniciar.bat
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

### 14.11. No aparecen fotos o PDFs

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

### 14.12. Se perdió información después de importar

Importar un respaldo reemplaza la información actual.

Antes de importar, el sistema genera un respaldo automático interno en:

```text
backups/
```

Si necesita recuperar el estado anterior, localice el respaldo automático más reciente y vuelva a importarlo.

---

### 14.13. No puedo entrar al modo edición

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

## 15. Recomendaciones de mantenimiento

- Hacer respaldos frecuentes.
- Exportar respaldo antes de mover el sistema a otra computadora.
- Importar únicamente respaldos generados por este sistema.
- No editar `database.db` manualmente.
- No mover ni renombrar manualmente archivos dentro de `static/uploads/`.
- No ejecutar varias instancias del sistema sobre la misma base de datos.
- Cerrar primero el navegador y luego la ventana negra de `iniciar.bat`.
- Guardar copias externas de los respaldos importantes.

---

## 16. Uso prolongado del sistema

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

## 17. Modo desarrollo y modo entrega

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

## 18. Comandos rápidos

### Iniciar automáticamente en Windows

```text
iniciar.bat
```

### Crear entorno virtual manualmente

```bat
python -m venv venv
```

### Activar entorno virtual en Windows

```bat
venv\Scripts\activate
```

### Instalar dependencias manualmente

```bat
python -m pip install -r requirements.txt
```

### Ejecutar sistema manualmente

```bat
python app.py
```

### Abrir en navegador

```text
http://127.0.0.1:5000
```

### Cerrar sistema para usuario final

```text
Cerrar navegador → cerrar ventana negra con X
```

### Cerrar sistema desde terminal

```text
Ctrl + C → S → Enter
```

---

## 19. Nota final

Este sistema funciona como una aplicación local. La base de datos y los archivos viven en la computadora donde se ejecuta. Para conservar la información y moverla correctamente, use siempre el módulo de respaldos integrado.
