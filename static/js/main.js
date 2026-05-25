document.addEventListener("DOMContentLoaded", function () {
    configurarCampoInventario();

    // ===== MODAL DE ARCHIVOS =====
    const modal = document.getElementById("archivoModal");
    const modalTitulo = document.getElementById("modalTitulo");
    const modalBody = document.getElementById("modalBody");
    const cerrarModal = document.getElementById("cerrarModal");
    const botonesModal = document.querySelectorAll(".btn-modal");

    function construirUrlArchivo(archivo) {
        if (!archivo) return "";

        if (archivo.startsWith("http") || archivo.startsWith("/")) {
            return archivo;
        }

        return "/static/" + archivo;
    }

    function obtenerNombreArchivo(ruta) {
        if (!ruta) return "Archivo";

        const partes = ruta.split("/");
        const nombre = partes[partes.length - 1] || "Archivo";

        return nombre.replace(/^[a-f0-9]{32}_/, "");
    }

    function leerArchivosDesdeBoton(boton) {
        if (boton.dataset.archivos) {
            try {
                return JSON.parse(boton.dataset.archivos);
            } catch (error) {
                console.error("No se pudieron leer los archivos:", error);
                return [];
            }
        }

        if (boton.dataset.archivo) {
            return [boton.dataset.archivo];
        }

        return [];
    }

    function mostrarFotos(archivos, titulo) {
        if (!modalBody) return;

        modalBody.innerHTML = "";

        if (!archivos || archivos.length === 0) {
            modalBody.innerHTML = "<p>No hay fotos disponibles.</p>";
            return;
        }

        const grid = document.createElement("div");
        grid.style.display = "grid";
        grid.style.gridTemplateColumns = "repeat(auto-fit, minmax(220px, 1fr))";
        grid.style.gap = "16px";

        archivos.forEach((archivo, index) => {
            const contenedor = document.createElement("div");
            contenedor.style.border = "1px solid var(--border-color)";
            contenedor.style.borderRadius = "var(--radius-md)";
            contenedor.style.padding = "12px";
            contenedor.style.background = "var(--bg-color)";

            const imagen = document.createElement("img");
            imagen.src = construirUrlArchivo(archivo);
            imagen.alt = `${titulo} ${index + 1}`;
            imagen.className = "modal-imagen";
            imagen.style.width = "100%";
            imagen.style.maxHeight = "420px";
            imagen.style.objectFit = "contain";

            const texto = document.createElement("p");
            texto.textContent = `Foto ${index + 1}`;
            texto.style.marginTop = "8px";
            texto.style.fontSize = "0.75rem";
            texto.style.color = "var(--text-muted)";
            texto.style.textAlign = "center";

            contenedor.appendChild(imagen);
            contenedor.appendChild(texto);
            grid.appendChild(contenedor);
        });

        modalBody.appendChild(grid);
    }

    function mostrarPDFs(archivos) {
        if (!modalBody) return;

        modalBody.innerHTML = "";

        if (!archivos || archivos.length === 0) {
            modalBody.innerHTML = "<p>No hay PDFs disponibles.</p>";
            return;
        }

        const contenedor = document.createElement("div");
        contenedor.style.display = "grid";
        contenedor.style.gap = "16px";

        const barra = document.createElement("div");
        barra.style.display = "flex";
        barra.style.flexWrap = "wrap";
        barra.style.gap = "8px";

        const iframe = document.createElement("iframe");
        iframe.className = "modal-pdf";
        iframe.src = construirUrlArchivo(archivos[0]);

        archivos.forEach((archivo, index) => {
            const boton = document.createElement("button");
            boton.type = "button";
            boton.className = "btn btn-secondary";
            boton.style.padding = "8px 12px";
            boton.style.fontSize = "0.75rem";
            boton.textContent = `${index + 1}. ${obtenerNombreArchivo(archivo)}`;

            boton.addEventListener("click", function () {
                iframe.src = construirUrlArchivo(archivo);
            });

            barra.appendChild(boton);
        });

        contenedor.appendChild(barra);
        contenedor.appendChild(iframe);
        modalBody.appendChild(contenedor);
    }

    botonesModal.forEach((boton) => {
        boton.addEventListener("click", function () {
            if (!modal || !modalTitulo || !modalBody) return;

            const tipo = this.dataset.tipo;
            const titulo = this.dataset.titulo || "Vista previa";
            const archivos = leerArchivosDesdeBoton(this);

            modalTitulo.textContent = titulo;

            if (tipo === "fotos" || tipo === "foto") {
                mostrarFotos(archivos, titulo);
            }

            if (tipo === "pdfs" || tipo === "pdf") {
                mostrarPDFs(archivos);
            }

            modal.style.display = "flex";
        });
    });

    if (cerrarModal) {
        cerrarModal.addEventListener("click", function () {
            modal.style.display = "none";
            modalBody.innerHTML = "";
        });
    }

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
            modalBody.innerHTML = "";
        }
    });

    // ===== MODAL ELIMINAR =====
    const eliminarModal = document.getElementById("eliminarModal");
    const cerrarEliminarModal = document.getElementById("cerrarEliminarModal");
    const cancelarEliminar = document.getElementById("cancelarEliminar");
    const mensajeEliminar = document.getElementById("mensajeEliminar");
    const formEliminar = document.getElementById("formEliminar");
    const botonesEliminar = document.querySelectorAll(".btn-eliminar");

    botonesEliminar.forEach((boton) => {
        boton.addEventListener("click", function () {
            if (!eliminarModal || !mensajeEliminar || !formEliminar) return;

            const id = this.dataset.id;
            const nombre = this.dataset.nombre;
            const url = this.dataset.url;

            mensajeEliminar.textContent = `¿Estás seguro de eliminar ${nombre}?`;

            if (url) {
                formEliminar.action = url;
            } else {
                formEliminar.action = `/materiales/eliminar/${id}`;
            }

            eliminarModal.style.display = "flex";
        });
    });

    if (cerrarEliminarModal) {
        cerrarEliminarModal.addEventListener("click", function () {
            eliminarModal.style.display = "none";
        });
    }

    if (cancelarEliminar) {
        cancelarEliminar.addEventListener("click", function () {
            eliminarModal.style.display = "none";
        });
    }

    window.addEventListener("click", function (event) {
        if (event.target === eliminarModal) {
            eliminarModal.style.display = "none";
        }
    });

    // ===== SELECCIÓN ACUMULATIVA DE ARCHIVOS =====
    inicializarSelectorArchivos("fotos");
    inicializarSelectorArchivos("pdfs");

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

    // ===== VALIDACIÓN CREAR =====
    const formCrear = document.getElementById("formCrearMaterial");
    const erroresCrear = document.getElementById("erroresCrear");

    if (formCrear) {
        formCrear.addEventListener("submit", function (event) {
            const errores = [];
            const erroresCampos = {};
            limpiarErroresCamposMaterial();

            const errorBackendCrear = document.getElementById("errorBackendCrear");
            if (errorBackendCrear) {
                errorBackendCrear.style.display = "none";
            }

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

            if (errores.length > 0 || hayErroresCampos(erroresCampos)) {
                event.preventDefault();
                mostrarErrores(erroresCrear, errores);
                mostrarErroresCamposMaterial(erroresCampos);
                return;
            }

            const camposVacios = obtenerCamposVaciosMaterial();

            if (camposVacios.length > 0 && formCrear.dataset.confirmadoCamposVacios !== "true") {
                event.preventDefault();
                limpiarErrores(erroresCrear);

                mostrarModalCamposVacios(camposVacios, function () {
                    formCrear.dataset.confirmadoCamposVacios = "true";
                    formCrear.submit();
                });

                return;
            }

            limpiarErrores(erroresCrear);
        });
    }

    // ===== VALIDACIÓN EDITAR =====
    const formEditar = document.getElementById("formEditarMaterial");
    const erroresEditar = document.getElementById("erroresEditar");

    if (formEditar) {
        formEditar.addEventListener("submit", function (event) {
            const errores = [];
            const erroresCampos = {};
            limpiarErroresCamposMaterial();

            const errorBackendEditar = document.getElementById("errorBackendEditar");
            if (errorBackendEditar) {
                errorBackendEditar.style.display = "none";
            }

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

            if (errores.length > 0 || hayErroresCampos(erroresCampos)) {
                event.preventDefault();
                mostrarErrores(erroresEditar, errores);
                mostrarErroresCamposMaterial(erroresCampos);
                return;
            }

            const camposVacios = obtenerCamposVaciosMaterial();

            if (camposVacios.length > 0 && formEditar.dataset.confirmadoCamposVacios !== "true") {
                event.preventDefault();
                limpiarErrores(erroresEditar);

                mostrarModalCamposVacios(camposVacios, function () {
                    formEditar.dataset.confirmadoCamposVacios = "true";
                    formEditar.submit();
                });

                return;
            }

            limpiarErrores(erroresEditar);
        });
    }

    // ===== VALIDACIÓN BUSCAR =====
    const formBuscar = document.getElementById("formBuscarMaterial");
    const erroresBuscar = document.getElementById("erroresBuscar");

    if (formBuscar) {
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
                mostrarErroresCamposMaterial(erroresCampos);
            }
        });
    }

    // ===== VALIDACIÓN PROFESOR =====
    const formProfesor = document.getElementById("formProfesor");
    const erroresProfesor = document.getElementById("erroresProfesor");

    if (formProfesor) {
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
                mostrarErroresCamposMaterial(erroresCampos);
            }
        });
    }
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

// ===== FUNCIONES AUXILIARES DE ARCHIVOS =====
function inicializarSelectorArchivos(inputId) {
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
                return archivosSonIguales(existente, archivo);
            });

            if (!yaExiste) {
                archivosSeleccionados.push(archivo);
            }
        });

        actualizarInputConArchivos(input, archivosSeleccionados);
        renderizarArchivosSeleccionados(input, preview, archivosSeleccionados);
    });

    renderizarArchivosSeleccionados(input, preview, archivosSeleccionados);
}

function archivosSonIguales(archivoA, archivoB) {
    return archivoA.name === archivoB.name &&
        archivoA.size === archivoB.size &&
        archivoA.lastModified === archivoB.lastModified;
}

function actualizarInputConArchivos(input, archivos) {
    const dataTransfer = new DataTransfer();

    archivos.forEach((archivo) => {
        dataTransfer.items.add(archivo);
    });

    input.files = dataTransfer.files;
}

function renderizarArchivosSeleccionados(input, preview, archivos) {
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
        tamano.textContent = formatearTamanoArchivo(archivo.size);
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
            actualizarInputConArchivos(input, archivos);
            renderizarArchivosSeleccionados(input, preview, archivos);
        });

        item.appendChild(info);
        item.appendChild(botonQuitar);
        lista.appendChild(item);
    });

    preview.appendChild(lista);
}

function formatearTamanoArchivo(bytes) {
    if (!bytes && bytes !== 0) return "";

    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ===== VALIDACIONES =====
function limpiarErrores(contenedor) {
    if (contenedor) {
        contenedor.innerHTML = "";
    }
}

function mostrarErrores(contenedor, errores) {
    if (!contenedor) return;

    if (errores.length === 0) {
        contenedor.innerHTML = "";
        return;
    }

    let html = "<ul>";

    errores.forEach((error) => {
        html += `<li>${error}</li>`;
    });

    html += "</ul>";

    contenedor.innerHTML = html;
}

function agregarErrorCampo(erroresCampos, campo, mensaje) {
    if (!erroresCampos[campo]) {
        erroresCampos[campo] = [];
    }

    erroresCampos[campo].push(mensaje);
}


function hayErroresCampos(erroresCampos) {
    return Object.values(erroresCampos).some((errores) => errores.length > 0);
}


function limpiarErrorCampo(campo) {
    const contenedor = document.getElementById(`error_${campo}`);
    const input = document.getElementById(campo);

    if (contenedor) {
        contenedor.innerHTML = "";
    }

    if (input) {
        input.classList.remove("input-error");
    }
}


function limpiarErroresCamposMaterial() {
    limpiarErrorCampo("doctor_responsable");
    limpiarErrorCampo("estado_prestamo");
}


function mostrarErroresCamposMaterial(erroresCampos) {
    Object.keys(erroresCampos).forEach((campo) => {
        const contenedor = document.getElementById(`error_${campo}`);
        const input = document.getElementById(campo);

        if (!contenedor) return;

        contenedor.innerHTML = erroresCampos[campo]
            .map((mensaje) => `<div>${mensaje}</div>`)
            .join("");

        if (input) {
            input.classList.add("input-error");
        }
    });
}

function esVacio(valor) {
    return !valor || valor.trim() === "";
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
            errores.push("El año debe ser un número entero.");
        } else {
            const anioActual = new Date().getFullYear();

            if (parseInt(anio, 10) > anioActual) {
                errores.push("El año no puede ser mayor al actual.");
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

function validarLimiteArchivos(inputId, errores, etiqueta) {
    const input = document.getElementById(inputId);

    if (!input) return;

    const maxArchivos = parseInt(input.dataset.maxArchivos || "5", 10);
    const archivosActuales = parseInt(input.dataset.actuales || "0", 10);
    const archivosNuevos = input.files ? input.files.length : 0;

    if (archivosActuales + archivosNuevos > maxArchivos) {
        errores.push(`Solo puedes tener máximo ${maxArchivos} ${etiqueta} por material.`);
    }
}

function validarExtensionesArchivos(inputId, errores, extensionesPermitidas, mensajeError) {
    const input = document.getElementById(inputId);

    if (!input || !input.files) return;

    Array.from(input.files).forEach((archivo) => {
        const nombre = archivo.name || "";

        if (!nombre.includes(".")) {
            if (!errores.includes(mensajeError)) {
                errores.push(mensajeError);
            }
            return;
        }

        const extension = nombre.split(".").pop().toLowerCase();

        if (!extensionesPermitidas.includes(extension)) {
            if (!errores.includes(mensajeError)) {
                errores.push(mensajeError);
            }
        }
    });
}

function obtenerOCrearModalCamposVacios() {
    let modal = document.getElementById("modalCamposVacios");

    if (modal) return modal;

    modal = document.createElement("div");
    modal.id = "modalCamposVacios";
    modal.style.display = "none";
    modal.style.position = "fixed";
    modal.style.inset = "0";
    modal.style.background = "rgba(15, 23, 42, 0.55)";
    modal.style.zIndex = "9999";
    modal.style.alignItems = "center";
    modal.style.justifyContent = "center";
    modal.style.padding = "20px";

    modal.innerHTML = `
        <div style="
            width: min(520px, 100%);
            background: var(--surface, #ffffff);
            border-radius: var(--radius-lg, 18px);
            box-shadow: 0 20px 60px rgba(15, 23, 42, 0.25);
            overflow: hidden;
            border: 1px solid var(--border-color, #e2e8f0);
        ">
            <div style="
                padding: 20px 22px;
                border-bottom: 1px solid var(--border-color, #e2e8f0);
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
            ">
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; color: var(--text-color, #0f172a);">
                        Campos incompletos
                    </h3>
                    <p style="margin: 6px 0 0; font-size: 0.85rem; color: var(--text-muted, #64748b);">
                        El material se guardará con información incompleta.
                    </p>
                </div>

                <button type="button" id="cerrarModalCamposVacios" class="btn btn-secondary" style="padding: 6px 10px;">
                    ✕
                </button>
            </div>

            <div style="padding: 20px 22px;">
                <p style="margin-top: 0; color: var(--text-color, #0f172a);">
                    Los siguientes campos están vacíos:
                </p>

                <ul id="listaCamposVacios" style="
                    margin: 0 0 18px 20px;
                    color: var(--text-muted, #64748b);
                    line-height: 1.7;
                    max-height: 220px;
                    overflow: auto;
                "></ul>

                <p style="
                    margin: 0;
                    font-size: 0.86rem;
                    color: var(--text-muted, #64748b);
                ">
                    Puedes regresar para completarlos o continuar de todas formas.
                </p>
            </div>

            <div style="
                padding: 16px 22px 20px;
                display: flex;
                justify-content: flex-end;
                gap: 10px;
                border-top: 1px solid var(--border-color, #e2e8f0);
            ">
                <button type="button" id="cancelarModalCamposVacios" class="btn btn-secondary">
                    Revisar campos
                </button>

                <button type="button" id="continuarModalCamposVacios" class="btn btn-primary">
                    Continuar y guardar
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    return modal;
}


function mostrarModalCamposVacios(camposVacios, alConfirmar) {
    const modal = obtenerOCrearModalCamposVacios();
    const lista = document.getElementById("listaCamposVacios");
    const cerrar = document.getElementById("cerrarModalCamposVacios");
    const cancelar = document.getElementById("cancelarModalCamposVacios");
    const continuar = document.getElementById("continuarModalCamposVacios");

    if (!lista || !cerrar || !cancelar || !continuar) return;

    lista.innerHTML = "";

    camposVacios.forEach((campo) => {
        const item = document.createElement("li");
        item.textContent = campo;
        lista.appendChild(item);
    });

    function cerrarModal() {
        modal.style.display = "none";
    }

    cerrar.onclick = cerrarModal;
    cancelar.onclick = cerrarModal;

    continuar.onclick = function () {
        modal.style.display = "none";

        if (typeof alConfirmar === "function") {
            alConfirmar();
        }
    };

    modal.onclick = function (event) {
        if (event.target === modal) {
            cerrarModal();
        }
    };

    modal.style.display = "flex";
}