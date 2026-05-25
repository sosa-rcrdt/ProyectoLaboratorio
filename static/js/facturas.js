document.addEventListener("DOMContentLoaded", function () {
    inicializarLimpiezaErroresFactura();
    inicializarValidacionCrearFactura();
    inicializarValidacionEditarFactura();
    inicializarValidacionBuscarFactura();
    inicializarValidacionProfesorFactura();
});


function inicializarLimpiezaErroresFactura() {
    [
        "doctor_responsable_factura",
        "presupuesto_factura",
        "archivo_pdf_factura",
        "busqueda_factura",
        "doctor_responsable_factura_filtro"
    ].forEach((campoId) => {
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


function limpiarErroresCamposFactura() {
    limpiarErroresCampos([
        "doctor_responsable_factura",
        "presupuesto_factura",
        "archivo_pdf_factura",
        "busqueda_factura",
        "doctor_responsable_factura_filtro"
    ]);
}


function inicializarValidacionCrearFactura() {
    const formCrear = document.getElementById("formCrearFactura");
    const erroresCrear = document.getElementById("erroresCrearFactura");

    if (!formCrear) return;

    formCrear.addEventListener("submit", function (event) {
        const errores = [];
        const erroresCampos = {};

        limpiarErroresCamposFactura();

        const errorBackendCrear = document.getElementById("errorBackendCrearFactura");
        if (errorBackendCrear) {
            errorBackendCrear.style.display = "none";
        }

        validarFormularioFactura(errores, erroresCampos, {
            pdfObligatorio: true,
            incluirAdvertencias: true,
            formulario: formCrear
        });

        if (errores.length > 0 || hayErroresCampos(erroresCampos)) {
            event.preventDefault();
            mostrarErrores(erroresCrear, errores);
            mostrarErroresCampos(erroresCampos);
            return;
        }

        const camposVacios = obtenerCamposVaciosFactura({
            formulario: formCrear,
            pdfObligatorio: true
        });

        if (camposVacios.length > 0 && formCrear.dataset.confirmadoCamposVacios !== "true") {
            event.preventDefault();
            limpiarErrores(erroresCrear);

            mostrarModalCamposVacios(camposVacios, function () {
                formCrear.dataset.confirmadoCamposVacios = "true";
                formCrear.submit();
            }, {
                subtitulo: "La factura se guardará con información incompleta."
            });

            return;
        }

        limpiarErrores(erroresCrear);
    });
}


function inicializarValidacionEditarFactura() {
    const formEditar = document.getElementById("formEditarFactura");
    const erroresEditar = document.getElementById("erroresEditarFactura");

    if (!formEditar) return;

    formEditar.addEventListener("submit", function (event) {
        const errores = [];
        const erroresCampos = {};

        limpiarErroresCamposFactura();

        const errorBackendEditar = document.getElementById("errorBackendEditarFactura");
        if (errorBackendEditar) {
            errorBackendEditar.style.display = "none";
        }

        validarFormularioFactura(errores, erroresCampos, {
            pdfObligatorio: false,
            incluirAdvertencias: true,
            formulario: formEditar
        });

        if (errores.length > 0 || hayErroresCampos(erroresCampos)) {
            event.preventDefault();
            mostrarErrores(erroresEditar, errores);
            mostrarErroresCampos(erroresCampos);
            return;
        }

        const camposVacios = obtenerCamposVaciosFactura({
            formulario: formEditar,
            pdfObligatorio: false
        });

        if (camposVacios.length > 0 && formEditar.dataset.confirmadoCamposVacios !== "true") {
            event.preventDefault();
            limpiarErrores(erroresEditar);

            mostrarModalCamposVacios(camposVacios, function () {
                formEditar.dataset.confirmadoCamposVacios = "true";
                formEditar.submit();
            }, {
                subtitulo: "La factura se guardará con información incompleta."
            });

            return;
        }

        limpiarErrores(erroresEditar);
    });
}


function inicializarValidacionBuscarFactura() {
    const formBuscar = document.getElementById("formBuscarFactura");
    const erroresBuscar = document.getElementById("erroresBuscarFactura");

    if (!formBuscar) return;

    formBuscar.addEventListener("submit", function (event) {
        const erroresCampos = {};
        const busqueda = document.getElementById("busqueda_factura")?.value || "";

        limpiarErrores(erroresBuscar);
        limpiarErrorCampo("busqueda_factura");

        if (esVacio(busqueda)) {
            agregarErrorCampo(
                erroresCampos,
                "busqueda_factura",
                "Debes escribir algo para buscar."
            );
        }

        if (hayErroresCampos(erroresCampos)) {
            event.preventDefault();
            mostrarErroresCampos(erroresCampos);
        }
    });
}


function inicializarValidacionProfesorFactura() {
    const formProfesor = document.getElementById("formProfesorFactura");
    const erroresProfesor = document.getElementById("erroresProfesorFactura");

    if (!formProfesor) return;

    formProfesor.addEventListener("submit", function (event) {
        const erroresCampos = {};
        const profesor = document.getElementById("doctor_responsable_factura_filtro")?.value || "";

        limpiarErrores(erroresProfesor);
        limpiarErrorCampo("doctor_responsable_factura_filtro");

        if (esVacio(profesor)) {
            agregarErrorCampo(
                erroresCampos,
                "doctor_responsable_factura_filtro",
                "Debes seleccionar un profesor."
            );
        }

        if (hayErroresCampos(erroresCampos)) {
            event.preventDefault();
            mostrarErroresCampos(erroresCampos);
        }
    });
}


function validarFormularioFactura(errores, erroresCampos, opciones = {}) {
    const doctorResponsable = document.getElementById("doctor_responsable_factura")?.value || "";
    const presupuesto = document.getElementById("presupuesto_factura")?.value || "";
    const archivoPdf = document.getElementById("archivo_pdf_factura");

    const presupuestosValidos = [
        "Secihti",
        "POA",
        "Fondo Fijo",
        "VIEP",
        "PROME",
        "PFCE-PIFI"
    ];

    if (esVacio(doctorResponsable)) {
        agregarErrorCampo(
            erroresCampos,
            "doctor_responsable_factura",
            "Debes seleccionar un profesor responsable."
        );
    }

    if (esVacio(presupuesto)) {
        agregarErrorCampo(
            erroresCampos,
            "presupuesto_factura",
            "Debes seleccionar de qué presupuesto sale la factura."
        );
    } else if (!presupuestosValidos.includes(presupuesto)) {
        agregarErrorCampo(
            erroresCampos,
            "presupuesto_factura",
            "El presupuesto seleccionado no es válido."
        );
    }

    validarArchivoPDFFactura(archivoPdf, erroresCampos, {
        obligatorio: opciones.pdfObligatorio === true
    });
}


function validarArchivoPDFFactura(inputArchivo, erroresCampos, opciones = {}) {
    if (!inputArchivo) return;

    const archivos = inputArchivo.files ? Array.from(inputArchivo.files) : [];

    if (opciones.obligatorio && archivos.length === 0) {
        agregarErrorCampo(
            erroresCampos,
            "archivo_pdf_factura",
            "Debes subir el PDF de la factura."
        );
        return;
    }

    if (archivos.length === 0) return;

    const archivo = archivos[0];
    const nombre = archivo.name || "";

    if (!nombre.includes(".")) {
        agregarErrorCampo(
            erroresCampos,
            "archivo_pdf_factura",
            "Solo se permiten archivos PDF."
        );
        return;
    }

    const extension = nombre.split(".").pop().toLowerCase();

    if (extension !== "pdf") {
        agregarErrorCampo(
            erroresCampos,
            "archivo_pdf_factura",
            "Solo se permiten archivos PDF."
        );
    }
}


function obtenerCamposVaciosFactura(opciones = {}) {
    const campos = [
        {
            id: "fecha_factura",
            etiqueta: "Fecha de la factura"
        },
        {
            id: "descripcion_factura",
            etiqueta: "Descripción"
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

    const form = opciones.formulario;
    const pdfActual = form?.dataset?.pdfActual === "true";
    const inputPdf = document.getElementById("archivo_pdf_factura");
    const tienePdfNuevo = inputPdf && inputPdf.files && inputPdf.files.length > 0;

    if (!opciones.pdfObligatorio && !pdfActual && !tienePdfNuevo) {
        camposVacios.push("Archivo PDF");
    }

    return camposVacios;
}