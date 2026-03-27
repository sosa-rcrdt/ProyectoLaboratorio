document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("archivoModal");
    const modalTitulo = document.getElementById("modalTitulo");
    const modalBody = document.getElementById("modalBody");
    const cerrarModal = document.getElementById("cerrarModal");
    const botonesModal = document.querySelectorAll(".btn-modal");

    botonesModal.forEach((boton) => {
        boton.addEventListener("click", function () {
            const tipo = this.dataset.tipo;
            const titulo = this.dataset.titulo;
            const archivo = this.dataset.archivo;

            modalTitulo.textContent = titulo;
            modalBody.innerHTML = "";

            let archivoUrl = archivo;
            if (archivoUrl && !archivoUrl.startsWith("http") && !archivoUrl.startsWith("/")) {
                archivoUrl = "/static/" + archivoUrl;
            }

            if (tipo === "foto") {
                modalBody.innerHTML = `
                    <img src="${archivoUrl}" alt="${titulo}" class="modal-imagen">
                `;
            }

            if (tipo === "pdf") {
                modalBody.innerHTML = `
                    <iframe src="${archivoUrl}" class="modal-pdf"></iframe>
                `;
            }

            modal.style.display = "flex";
        });
    });

    cerrarModal.addEventListener("click", function () {
        modal.style.display = "none";
        modalBody.innerHTML = "";
    });

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
            modalBody.innerHTML = "";
        }
    });
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
        const id = this.dataset.id;
        const nombre = this.dataset.nombre;

        mensajeEliminar.textContent = `¿Estás seguro de eliminar "${nombre}"?`;

        formEliminar.action = `/materiales/eliminar/${id}`;

        eliminarModal.style.display = "flex";
    });
});

// Cerrar modal
cerrarEliminarModal.addEventListener("click", () => {
    eliminarModal.style.display = "none";
});

cancelarEliminar.addEventListener("click", () => {
    eliminarModal.style.display = "none";
});

// Cerrar al hacer click fuera
window.addEventListener("click", function (event) {
    if (event.target === eliminarModal) {
        eliminarModal.style.display = "none";
    }
});

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
        if (esVacio(ubicacion)) errores.push("La ubicación es obligatoria.");
        if (esVacio(estadoPrestamo)) errores.push("Debes seleccionar un estado.");

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
        if (esVacio(ubicacion)) errores.push("La ubicación es obligatoria.");
        if (esVacio(estadoPrestamo)) errores.push("Debes seleccionar un estado.");

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
            errores.push("Debes escribir el numero de serie o nombre para buscar.");
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