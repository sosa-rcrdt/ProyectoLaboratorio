document.addEventListener("DOMContentLoaded", function () {
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
        const nombreSinUuid = nombre.replace(/^[a-f0-9]{32}_/, "");

        return nombreSinUuid;
    }

    function leerArchivosDesdeBoton(boton) {
        if (boton.dataset.archivos) {
            try {
                return JSON.parse(boton.dataset.archivos);
            } catch (error) {
                console.error("No se pudieron leer los archivos del botón:", error);
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
        grid.style.alignItems = "start";

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
        cerrarEliminarModal.addEventListener("click", () => {
            eliminarModal.style.display = "none";
        });
    }

    if (cancelarEliminar) {
        cancelarEliminar.addEventListener("click", () => {
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

    // ===== VALIDACIÓN CREAR =====
    const formCrear = document.getElementById("formCrearMaterial");
    const erroresCrear = document.getElementById("erroresCrear");

    if (formCrear) {
        formCrear.addEventListener("submit", function (event) {
            const errores = [];

            const errorBackendCrear = document.getElementById("errorBackendCrear");
            if (errorBackendCrear) {
                errorBackendCrear.style.display = "none";
            }

            validarCamposMaterial(errores);
            validarLimiteArchivos("fotos", errores, "fotos");
            validarLimiteArchivos("pdfs", errores, "PDFs");

            if (errores.length > 0) {
                event.preventDefault();
                mostrarErrores(erroresCrear, errores);
            } else {
                limpiarErrores(erroresCrear);
            }
        });
    }

    // ===== VALIDACIÓN EDITAR =====
    const formEditar = document.getElementById("formEditarMaterial");
    const erroresEditar = document.getElementById("erroresEditar");

    if (formEditar) {
        formEditar.addEventListener("submit", function (event) {
            const errores = [];

            const errorBackendEditar = document.getElementById("errorBackendEditar");
            if (errorBackendEditar) {
                errorBackendEditar.style.display = "none";
            }

            validarCamposMaterial(errores);
            validarLimiteArchivos("fotos", errores, "fotos");
            validarLimiteArchivos("pdfs", errores, "PDFs");

            if (errores.length > 0) {
                event.preventDefault();
                mostrarErrores(erroresEditar, errores);
            } else {
                limpiarErrores(erroresEditar);
            }
        });
    }

    // ===== VALIDACIÓN BUSCAR =====
    const formBuscar = document.getElementById("formBuscarMaterial");
    const erroresBuscar = document.getElementById("erroresBuscar");

    if (formBuscar) {
        formBuscar.addEventListener("submit", function (event) {
            const errores = [];
            const busqueda = formBuscar.querySelector('input[name="busqueda"]')?.value || "";

            if (esVacio(busqueda)) {
                errores.push("Debes escribir el número de serie o nombre para buscar.");
            }

            if (errores.length > 0) {
                event.preventDefault();
                mostrarErrores(erroresBuscar, errores);
            } else {
                limpiarErrores(erroresBuscar);
            }
        });
    }

    // ===== VALIDACIÓN PROFESOR =====
    const formProfesor = document.getElementById("formProfesor");
    const erroresProfesor = document.getElementById("erroresProfesor");

    if (formProfesor) {
        formProfesor.addEventListener("submit", function (event) {
            const errores = [];
            const profesor = document.getElementById("doctor_responsable")?.value || "";

            if (esVacio(profesor)) {
                errores.push("Debes seleccionar o escribir un profesor.");
            }

            if (errores.length > 0) {
                event.preventDefault();
                mostrarErrores(erroresProfesor, errores);
            } else {
                limpiarErrores(erroresProfesor);
            }
        });
    }
});

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

            const yaExiste = archivosSeleccionados.some((existente) => archivosSonIguales(existente, archivo));

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

        const info = document.createElement("div");
        info.style.display = "flex";
        info.style.alignItems = "center";
        info.style.gap = "10px";
        info.style.minWidth = "0";

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

        const nombre = document.createElement("div");
        nombre.textContent = archivo.name;
        nombre.style.fontSize = "0.8rem";
        nombre.style.fontWeight = "600";
        nombre.style.whiteSpace = "nowrap";
        nombre.style.overflow = "hidden";
        nombre.style.textOverflow = "ellipsis";
        nombre.style.maxWidth = "280px";

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

// ===== FUNCIONES AUXILIARES DE VALIDACIÓN =====
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

function esVacio(valor) {
    return !valor || valor.trim() === "";
}

function validarCamposMaterial(errores) {
    const numeroSerie = document.getElementById("numero_serie")?.value || "";
    const nombreMaterial = document.getElementById("nombre_material")?.value || "";
    const marca = document.getElementById("marca")?.value || "";
    const doctorResponsable = document.getElementById("doctor_responsable")?.value || "";
    const anio = document.getElementById("anio")?.value || "";
    const ubicacion = document.getElementById("ubicacion")?.value || "";
    const estadoPrestamo = document.getElementById("estado_prestamo")?.value || "";

    if (esVacio(numeroSerie)) errores.push("El número de serie es obligatorio.");
    if (esVacio(nombreMaterial)) errores.push("El nombre del material es obligatorio.");
    if (esVacio(marca)) errores.push("La marca es obligatoria.");
    if (esVacio(doctorResponsable)) errores.push("El doctor responsable es obligatorio.");
    if (esVacio(anio)) errores.push("El año es obligatorio.");

    const anioActual = new Date().getFullYear();
    if (!esVacio(anio) && parseInt(anio) > anioActual) {
        errores.push("El año no puede ser mayor al actual.");
    }

    if (esVacio(ubicacion)) errores.push("La ubicación es obligatoria.");
    if (esVacio(estadoPrestamo)) errores.push("Debes seleccionar un estado.");
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