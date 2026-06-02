document.addEventListener("DOMContentLoaded", function () {
    configurarCampoInventario();
    inicializarSelectoresArchivosMaterial();
    inicializarLimpiezaErroresMaterial();
    inicializarValidacionCrearMaterial();
    inicializarValidacionEditarMaterial();
    inicializarValidacionBuscarMaterial();
    inicializarValidacionProfesorMaterial();
});

// ===== INVENTARIADO =====
function configurarCampoInventario() {
    const inventariado = document.getElementById("inventariado");
    const numeroInventario = document.getElementById("numero_inventario");

    if (!inventariado || !numeroInventario) return;

    function actualizarEstado() {
        if (inventariado.value === "Inventariado") {
            numeroInventario.disabled = false;
            numeroInventario.required = false;
            numeroInventario.placeholder = "Escribe el número de inventario";
        } else {
            numeroInventario.value = "";
            numeroInventario.disabled = true;
            numeroInventario.required = false;
            numeroInventario.placeholder = "No aplica";
        }
    }

    inventariado.addEventListener("change", actualizarEstado);
    actualizarEstado();
}


// ===== SELECCIÓN ACUMULATIVA DE ARCHIVOS =====
function inicializarSelectoresArchivosMaterial() {
    inicializarSelectorArchivosMaterial("fotos");
    inicializarSelectorArchivosMaterial("pdfs");
}


function inicializarSelectorArchivosMaterial(inputId) {
    const input = document.getElementById(inputId);

    if (!input) return;

    const previewId = input.dataset.preview;
    const preview = previewId ? document.getElementById(previewId) : null;

    if (!preview) return;

    let archivosSeleccionados = [];

    input.addEventListener("change", function () {
        const nuevosArchivos = Array.from(input.files || []);
        const maxArchivos = parseInt(input.dataset.maxArchivos || "5", 10);
        const archivosActuales = parseInt(input.dataset.actuales || "0", 10);
        const espaciosDisponibles = Math.max(maxArchivos - archivosActuales, 0);

        nuevosArchivos.forEach((archivo) => {
            if (archivosSeleccionados.length >= espaciosDisponibles) {
                return;
            }

            const yaExiste = archivosSeleccionados.some((existente) => {
                return archivosSonIgualesMaterial(existente, archivo);
            });

            if (!yaExiste) {
                archivosSeleccionados.push(archivo);
            }
        });

        actualizarInputConArchivosMaterial(input, archivosSeleccionados);
        renderizarArchivosSeleccionadosMaterial(input, preview, archivosSeleccionados);
    });

    renderizarArchivosSeleccionadosMaterial(input, preview, archivosSeleccionados);
}


function archivosSonIgualesMaterial(archivoA, archivoB) {
    return archivoA.name === archivoB.name &&
        archivoA.size === archivoB.size &&
        archivoA.lastModified === archivoB.lastModified;
}


function actualizarInputConArchivosMaterial(input, archivos) {
    const dataTransfer = new DataTransfer();

    archivos.forEach((archivo) => {
        dataTransfer.items.add(archivo);
    });

    input.files = dataTransfer.files;
}


function renderizarArchivosSeleccionadosMaterial(input, preview, archivos) {
    const maxArchivos = parseInt(input.dataset.maxArchivos || "5", 10);
    const archivosActuales = parseInt(input.dataset.actuales || "0", 10);
    const tipo = input.dataset.tipo || "archivo";
    const etiquetaPlural = input.dataset.etiquetaPlural || "archivos";
    const espaciosDisponibles = Math.max(maxArchivos - archivosActuales, 0);

    preview.innerHTML = "";

    const resumen = document.createElement("div");
    resumen.style.fontSize = "0.78rem";
    resumen.style.color = "var(--text-muted)";
    resumen.style.marginTop = "8px";
    resumen.style.marginBottom = "8px";
    resumen.textContent = `${archivos.length}/${espaciosDisponibles} ${etiquetaPlural} nuevos seleccionados`;
    preview.appendChild(resumen);

    if (archivos.length === 0) {
        const vacio = document.createElement("p");
        vacio.style.fontSize = "0.78rem";
        vacio.style.color = "var(--text-muted)";
        vacio.style.margin = "0";
        vacio.textContent = `Aún no has seleccionado ${etiquetaPlural} nuevos.`;
        preview.appendChild(vacio);
        return;
    }

    const lista = document.createElement("div");
    lista.style.display = "grid";
    lista.style.gap = "10px";

    archivos.forEach((archivo, index) => {
        const item = document.createElement("div");
        item.style.display = "flex";
        item.style.alignItems = "center";
        item.style.justifyContent = "space-between";
        item.style.gap = "12px";
        item.style.padding = "10px";
        item.style.border = "1px solid var(--border-color)";
        item.style.borderRadius = "var(--radius-md)";
        item.style.background = "var(--surface)";
        item.style.minWidth = "0";
        item.style.width = "100%";
        item.style.boxSizing = "border-box";

        const info = document.createElement("div");
        info.style.display = "flex";
        info.style.alignItems = "center";
        info.style.gap = "10px";
        info.style.minWidth = "0";
        info.style.flex = "1";

        if (tipo === "foto") {
            const img = document.createElement("img");
            img.src = URL.createObjectURL(archivo);
            img.alt = archivo.name;
            img.style.width = "44px";
            img.style.height = "44px";
            img.style.borderRadius = "8px";
            img.style.objectFit = "cover";
            img.style.border = "1px solid var(--border-color)";
            info.appendChild(img);
        } else {
            const icono = document.createElement("i");
            icono.className = "material-symbols-rounded";
            icono.textContent = "picture_as_pdf";
            icono.style.color = "var(--primary)";
            info.appendChild(icono);
        }

        const texto = document.createElement("div");
        texto.style.minWidth = "0";
        texto.style.flex = "1";

        const nombre = document.createElement("div");
        nombre.textContent = archivo.name;
        nombre.style.fontSize = "0.8rem";
        nombre.style.fontWeight = "600";
        nombre.style.whiteSpace = "nowrap";
        nombre.style.overflow = "hidden";
        nombre.style.textOverflow = "ellipsis";
        nombre.style.maxWidth = "100%";

        const tamano = document.createElement("div");
        tamano.textContent = formatearTamanoArchivoMaterial(archivo.size);
        tamano.style.fontSize = "0.72rem";
        tamano.style.color = "var(--text-muted)";

        texto.appendChild(nombre);
        texto.appendChild(tamano);
        info.appendChild(texto);

        const botonQuitar = document.createElement("button");
        botonQuitar.type = "button";
        botonQuitar.className = "btn btn-danger";
        botonQuitar.style.padding = "6px 10px";
        botonQuitar.style.fontSize = "0.72rem";
        botonQuitar.textContent = "Quitar";
        botonQuitar.style.flexShrink = "0";

        botonQuitar.addEventListener("click", function () {
            archivos.splice(index, 1);
            actualizarInputConArchivosMaterial(input, archivos);
            renderizarArchivosSeleccionadosMaterial(input, preview, archivos);
        });

        item.appendChild(info);
        item.appendChild(botonQuitar);
        lista.appendChild(item);
    });

    preview.appendChild(lista);
}


function formatearTamanoArchivoMaterial(bytes) {
    if (!bytes && bytes !== 0) return "";

    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}


// ===== LIMPIEZA DE ERRORES POR CAMPO =====
function inicializarLimpiezaErroresMaterial() {
    ["doctor_responsable", "estado_prestamo", "busqueda"].forEach((campoId) => {
        const campo = document.getElementById(campoId);

        if (campo) {
            campo.addEventListener("input", function () {
                limpiarErrorCampo(campoId);
            });

            campo.addEventListener("change", function () {
                limpiarErrorCampo(campoId);
            });
        }
    });
}


function limpiarErroresCamposMaterial() {
    limpiarErroresCampos([
        "doctor_responsable",
        "estado_prestamo",
        "anio",
        "busqueda"
    ]);
}


// ===== VALIDACIÓN CREAR MATERIAL =====
function inicializarValidacionCrearMaterial() {
    const formCrear = document.getElementById("formCrearMaterial");
    const erroresCrear = document.getElementById("erroresCrear");

    if (!formCrear) return;

    formCrear.addEventListener("submit", function (event) {
        const errores = [];
        const erroresCampos = {};

        limpiarErroresCamposMaterial();

        const errorBackendCrear = document.getElementById("errorBackendCrear");
        if (errorBackendCrear) {
            errorBackendCrear.style.display = "none";
        }

        validarFormularioMaterial(errores, erroresCampos);

        if (errores.length > 0 || hayErroresCampos(erroresCampos)) {
            event.preventDefault();
            mostrarErrores(erroresCrear, errores);
            mostrarErroresCampos(erroresCampos);
            return;
        }

        const camposVacios = obtenerCamposVaciosMaterial();

        if (camposVacios.length > 0 && formCrear.dataset.confirmadoCamposVacios !== "true") {
            event.preventDefault();
            limpiarErrores(erroresCrear);

            mostrarModalCamposVacios(camposVacios, function () {
                formCrear.dataset.confirmadoCamposVacios = "true";
                formCrear.submit();
            }, {
                subtitulo: "El material se guardará con información incompleta."
            });

            return;
        }

        limpiarErrores(erroresCrear);
    });
}


// ===== VALIDACIÓN EDITAR MATERIAL =====
function inicializarValidacionEditarMaterial() {
    const formEditar = document.getElementById("formEditarMaterial");
    const erroresEditar = document.getElementById("erroresEditar");

    if (!formEditar) return;

    formEditar.addEventListener("submit", function (event) {
        const errores = [];
        const erroresCampos = {};

        limpiarErroresCamposMaterial();

        const errorBackendEditar = document.getElementById("errorBackendEditar");
        if (errorBackendEditar) {
            errorBackendEditar.style.display = "none";
        }

        validarFormularioMaterial(errores, erroresCampos);

        if (errores.length > 0 || hayErroresCampos(erroresCampos)) {
            event.preventDefault();
            mostrarErrores(erroresEditar, errores);
            mostrarErroresCampos(erroresCampos);
            return;
        }

        const camposVacios = obtenerCamposVaciosMaterial();

        if (camposVacios.length > 0 && formEditar.dataset.confirmadoCamposVacios !== "true") {
            event.preventDefault();
            limpiarErrores(erroresEditar);

            mostrarModalCamposVacios(camposVacios, function () {
                formEditar.dataset.confirmadoCamposVacios = "true";
                formEditar.submit();
            }, {
                subtitulo: "El material se guardará con información incompleta."
            });

            return;
        }

        limpiarErrores(erroresEditar);
    });
}


// ===== VALIDACIÓN BUSCAR MATERIAL =====
function inicializarValidacionBuscarMaterial() {
    const formBuscar = document.getElementById("formBuscarMaterial");
    const erroresBuscar = document.getElementById("erroresBuscar");

    if (!formBuscar) return;

    formBuscar.addEventListener("submit", function (event) {
        const erroresCampos = {};
        const busqueda = document.getElementById("busqueda")?.value || "";

        limpiarErrores(erroresBuscar);
        limpiarErrorCampo("busqueda");

        if (esVacio(busqueda)) {
            agregarErrorCampo(
                erroresCampos,
                "busqueda",
                "Debes escribir algo para buscar."
            );
        }

        if (hayErroresCampos(erroresCampos)) {
            event.preventDefault();
            mostrarErroresCampos(erroresCampos);
        }
    });
}


// ===== VALIDACIÓN FILTRAR POR PROFESOR =====
function inicializarValidacionProfesorMaterial() {
    const formProfesor = document.getElementById("formProfesor");
    const erroresProfesor = document.getElementById("erroresProfesor");

    if (!formProfesor) return;

    formProfesor.addEventListener("submit", function (event) {
        const erroresCampos = {};
        const profesor = document.getElementById("doctor_responsable")?.value || "";

        limpiarErrores(erroresProfesor);
        limpiarErrorCampo("doctor_responsable");

        if (esVacio(profesor)) {
            agregarErrorCampo(
                erroresCampos,
                "doctor_responsable",
                "Debes seleccionar un profesor."
            );
        }

        if (hayErroresCampos(erroresCampos)) {
            event.preventDefault();
            mostrarErroresCampos(erroresCampos);
        }
    });
}


// ===== VALIDACIONES DE MATERIAL =====
function validarFormularioMaterial(errores, erroresCampos) {
    validarReglasMaterialBloqueantes(errores, erroresCampos);

    validarLimiteArchivos("fotos", errores, "fotos");
    validarLimiteArchivos("pdfs", errores, "PDFs");

    validarExtensionesArchivos(
        "fotos",
        errores,
        ["png", "jpg", "jpeg", "gif", "webp"],
        "Solo se permiten imágenes con extensión: png, jpg, jpeg, gif o webp."
    );

    validarExtensionesArchivos(
        "pdfs",
        errores,
        ["pdf"],
        "Solo se permiten archivos PDF."
    );
}


function validarReglasMaterialBloqueantes(errores, erroresCampos = {}) {
    const inventariado = document.getElementById("inventariado")?.value || "";
    const doctorResponsable = document.getElementById("doctor_responsable")?.value || "";
    const anio = document.getElementById("anio")?.value || "";
    const estadoPrestamo = document.getElementById("estado_prestamo")?.value || "";

    const inventariadoValidos = ["Inventariado", "No Inventariado"];
    const estadosValidos = [
        "Disponible",
        "En préstamo",
        "Fuera de servicio",
        "En mantenimiento"
    ];

    if (!esVacio(inventariado) && !inventariadoValidos.includes(inventariado)) {
        errores.push("El valor de inventariado no es válido.");
    }

    if (esVacio(doctorResponsable)) {
        agregarErrorCampo(
            erroresCampos,
            "doctor_responsable",
            "Debes seleccionar un profesor responsable."
        );
    }

    if (esVacio(estadoPrestamo)) {
        agregarErrorCampo(
            erroresCampos,
            "estado_prestamo",
            "Debes seleccionar un estado."
        );
    } else if (!estadosValidos.includes(estadoPrestamo)) {
        agregarErrorCampo(
            erroresCampos,
            "estado_prestamo",
            "El estado seleccionado no es válido."
        );
    }

    if (!esVacio(anio)) {
        if (!/^\d+$/.test(anio.trim())) {
            agregarErrorCampo(
                erroresCampos,
                "anio",
                "El año debe ser un número entero."
            );
        } else {
            const anioActual = new Date().getFullYear();
            const anioNumero = parseInt(anio, 10);

            if (anioNumero < 1990) {
                agregarErrorCampo(
                    erroresCampos,
                    "anio",
                    "El año no puede ser menor a 1990."
                );
            } else if (anioNumero > anioActual) {
                agregarErrorCampo(
                    erroresCampos,
                    "anio",
                    "El año no puede ser mayor al actual."
                );
            }
        }
    }
}


function obtenerCamposVaciosMaterial() {
    const campos = [
        {
            id: "nombre_material",
            etiqueta: "Nombre del material"
        },
        {
            id: "numero_serie",
            etiqueta: "Número de serie"
        },
        {
            id: "no_fabricante",
            etiqueta: "No. fabricante"
        },
        {
            id: "marca",
            etiqueta: "Marca"
        },
        {
            id: "anio",
            etiqueta: "Año"
        },
        {
            id: "descripcion",
            etiqueta: "Descripción"
        },
        {
            id: "software",
            etiqueta: "Software"
        },
        {
            id: "inventariado",
            etiqueta: "Inventariado"
        },
        {
            id: "ubicacion",
            etiqueta: "Ubicación"
        }
    ];

    const camposVacios = [];

    campos.forEach((campo) => {
        const elemento = document.getElementById(campo.id);

        if (!elemento) return;

        if (esVacio(elemento.value || "")) {
            camposVacios.push(campo.etiqueta);
        }
    });

    const inventariado = document.getElementById("inventariado")?.value || "";
    const numeroInventario = document.getElementById("numero_inventario")?.value || "";

    if (inventariado === "Inventariado" && esVacio(numeroInventario)) {
        camposVacios.push("Número de inventario");
    }

    return camposVacios;
}