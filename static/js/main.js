document.addEventListener("DOMContentLoaded", function () {
    inicializarToasts();
    inicializarModalArchivos();
    inicializarModalEliminar();
});

// ===== TOASTS GLOBALES =====
function inicializarToasts() {
    const toasts = document.querySelectorAll(".toast");

    if (!toasts || toasts.length === 0) return;

    toasts.forEach((toast) => {
        const botonCerrar = toast.querySelector(".toast-close");
        const duracion = obtenerDuracionToast(toast);
        let timeoutId = null;

        function cerrarToast() {
            if (!toast || toast.classList.contains("toast-hide")) return;

            toast.classList.add("toast-hide");

            toast.addEventListener("animationend", function manejarFinAnimacion() {
                toast.removeEventListener("animationend", manejarFinAnimacion);
                toast.remove();
            });

            setTimeout(function () {
                if (toast && toast.parentNode) {
                    toast.remove();
                }
            }, 350);
        }

        if (botonCerrar) {
            botonCerrar.addEventListener("click", function () {
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }

                cerrarToast();
            });
        }

        if (toast.dataset.autoclose === "true") {
            timeoutId = setTimeout(cerrarToast, duracion);
        }

        toast.addEventListener("mouseenter", function () {
            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
        });

        toast.addEventListener("mouseleave", function () {
            if (toast.dataset.autoclose === "true" && !toast.classList.contains("toast-hide")) {
                timeoutId = setTimeout(cerrarToast, obtenerDuracionToast(toast) / 2);
            }
        });
    });
}


function obtenerDuracionToast(toast) {
    if (toast.classList.contains("toast-success")) {
        return 4000;
    }

    if (toast.classList.contains("toast-info")) {
        return 5000;
    }

    if (toast.classList.contains("toast-warning")) {
        return 6000;
    }

    if (toast.classList.contains("toast-error")) {
        return 7000;
    }

    return 5000;
}

// ===== MODAL GLOBAL DE ARCHIVOS =====
function inicializarModalArchivos() {
    const modal = document.getElementById("archivoModal");
    const modalTitulo = document.getElementById("modalTitulo");
    const modalBody = document.getElementById("modalBody");
    const cerrarModal = document.getElementById("cerrarModal");
    const botonesModal = document.querySelectorAll(".btn-modal");

    if (!modal || !modalTitulo || !modalBody) return;

    botonesModal.forEach((boton) => {
        boton.addEventListener("click", function () {
            const tipo = this.dataset.tipo;
            const titulo = this.dataset.titulo || "Vista previa";
            const archivos = leerArchivosDesdeBoton(this);

            modalTitulo.textContent = titulo;

            if (tipo === "fotos" || tipo === "foto") {
                mostrarFotosEnModal(archivos, titulo, modalBody);
            }

            if (tipo === "pdfs" || tipo === "pdf") {
                mostrarPDFsEnModal(archivos, modalBody);
            }

            modal.style.display = "flex";
        });
    });

    if (cerrarModal) {
        cerrarModal.addEventListener("click", function () {
            cerrarModalArchivos(modal, modalBody);
        });
    }

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            cerrarModalArchivos(modal, modalBody);
        }
    });
}


function cerrarModalArchivos(modal, modalBody) {
    if (modal) {
        modal.style.display = "none";
    }

    if (modalBody) {
        modalBody.innerHTML = "";
    }
}


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


function mostrarFotosEnModal(archivos, titulo, modalBody) {
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


function mostrarPDFsEnModal(archivos, modalBody) {
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


// ===== MODAL GLOBAL DE ELIMINACIÓN =====
function inicializarModalEliminar() {
    const eliminarModal = document.getElementById("eliminarModal");
    const cerrarEliminarModal = document.getElementById("cerrarEliminarModal");
    const cancelarEliminar = document.getElementById("cancelarEliminar");
    const mensajeEliminar = document.getElementById("mensajeEliminar");
    const formEliminar = document.getElementById("formEliminar");
    const botonesEliminar = document.querySelectorAll(".btn-eliminar");

    if (!eliminarModal || !mensajeEliminar || !formEliminar) return;

    botonesEliminar.forEach((boton) => {
        boton.addEventListener("click", function () {
            const id = this.dataset.id;
            const nombre = this.dataset.nombre || "este registro";
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
}


// ===== HELPERS GLOBALES DE VALIDACIÓN =====
function limpiarErrores(contenedor) {
    if (contenedor) {
        contenedor.innerHTML = "";
    }
}


function mostrarErrores(contenedor, errores) {
    if (!contenedor) return;

    if (!errores || errores.length === 0) {
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


function limpiarErroresCampos(campos) {
    campos.forEach((campo) => {
        limpiarErrorCampo(campo);
    });
}


function mostrarErroresCampos(erroresCampos) {
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


// ===== MODAL GLOBAL DE CAMPOS VACÍOS =====
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
                    <h3 id="tituloModalCamposVacios" style="margin: 0; font-size: 1.05rem; color: var(--text-color, #0f172a);">
                        Campos incompletos
                    </h3>
                    <p id="subtituloModalCamposVacios" style="margin: 6px 0 0; font-size: 0.85rem; color: var(--text-muted, #64748b);">
                        El registro se guardará con información incompleta.
                    </p>
                </div>

                <button type="button" id="cerrarModalCamposVacios" class="btn btn-secondary" style="padding: 6px 10px;">
                    ✕
                </button>
            </div>

            <div style="padding: 20px 22px;">
                <p id="introModalCamposVacios" style="margin-top: 0; color: var(--text-color, #0f172a);">
                    Los siguientes campos están vacíos:
                </p>

                <ul id="listaCamposVacios" style="
                    margin: 0 0 18px 20px;
                    color: var(--text-muted, #64748b);
                    line-height: 1.7;
                    max-height: 220px;
                    overflow: auto;
                "></ul>

                <p id="notaModalCamposVacios" style="
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


function mostrarModalCamposVacios(camposVacios, alConfirmar, opciones = {}) {
    const modal = obtenerOCrearModalCamposVacios();
    const titulo = document.getElementById("tituloModalCamposVacios");
    const subtitulo = document.getElementById("subtituloModalCamposVacios");
    const intro = document.getElementById("introModalCamposVacios");
    const nota = document.getElementById("notaModalCamposVacios");
    const lista = document.getElementById("listaCamposVacios");
    const cerrar = document.getElementById("cerrarModalCamposVacios");
    const cancelar = document.getElementById("cancelarModalCamposVacios");
    const continuar = document.getElementById("continuarModalCamposVacios");

    if (!lista || !cerrar || !cancelar || !continuar) return;

    if (titulo) {
        titulo.textContent = opciones.titulo || "Campos incompletos";
    }

    if (subtitulo) {
        subtitulo.textContent = opciones.subtitulo || "El registro se guardará con información incompleta.";
    }

    if (intro) {
        intro.textContent = opciones.intro || "Los siguientes campos están vacíos:";
    }

    if (nota) {
        nota.textContent = opciones.nota || "Puedes regresar para completarlos o continuar de todas formas.";
    }

    if (continuar && opciones.textoContinuar) {
        continuar.textContent = opciones.textoContinuar;
    } else {
        continuar.textContent = "Continuar y guardar";
    }

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