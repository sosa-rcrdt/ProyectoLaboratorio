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

            if (tipo === "foto") {
                modalBody.innerHTML = `
                    <img src="${archivo}" alt="${titulo}" class="modal-imagen">
                `;
            }

            if (tipo === "pdf") {
                modalBody.innerHTML = `
                    <iframe src="${archivo}" class="modal-pdf"></iframe>
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