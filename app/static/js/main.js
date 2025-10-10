// ==========================================================================
// SISTEMA DE TURISMO - JAVASCRIPT MODULAR
// ==========================================================================

// 1. CONFIGURACIÓN GLOBAL
const TurismoApp = {
    config: {
        debounceTime: 300,
        animationSpeed: 'fast',
        dateFormat: 'DD/MM/YYYY'
    },
    
    // Estado global de la aplicación
    state: {
        currentModule: null,
        user: null,
        filters: {}
    }
};

// 2. UTILIDADES GENERALES
const Utils = {
    // Debounce para optimizar búsquedas
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Mostrar notificaciones
    showNotification: function(message, type = 'info') {
        // TODO: Implementar sistema de notificaciones
        console.log(`[${type.toUpperCase()}] ${message}`);
    },
    
    // Validar formularios
    validateForm: function(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
};

// 3. MÓDULO INSTITUCIONES
const ModuloInstituciones = {
    init: function() {
        console.log('Módulo Instituciones inicializado');
        this.initFormulario();
        this.initFiltros();
    },
    
    initFormulario: function() {
        const form = document.querySelector('#formulario-solicitud');
        if (form) {
            form.addEventListener('submit', this.handleSubmit.bind(this));
        }
    },
    
    initFiltros: function() {
        // TODO: Implementar filtrado de prestadores
        console.log('Filtros de prestadores listos');
    },
    
    handleSubmit: function(e) {
        e.preventDefault();
        const form = e.target;
        
        if (Utils.validateForm(form)) {
            Utils.showNotification('Enviando solicitud...', 'info');
            // TODO: Enviar datos al backend
        } else {
            Utils.showNotification('Por favor completa todos los campos requeridos', 'danger');
        }
    }
};

// 4. MÓDULO ADMIN
const ModuloAdmin = {
    init: function() {
        console.log('Módulo Admin inicializado');
        this.initDashboard();
        this.initTablas();
    },
    
    initDashboard: function() {
        // TODO: Cargar estadísticas del dashboard
        console.log('Dashboard admin listo');
    },
    
    initTablas: function() {
        // TODO: Implementar DataTables para listas
        console.log('Tablas admin listas');
    },
    
    confirmarVisita: function(solicitudId) {
        if (confirm('¿Confirmar esta visita?')) {
            // TODO: Enviar confirmación al backend
            Utils.showNotification('Visita confirmada correctamente', 'success');
        }
    }
};

// 5. MÓDULO PRESTADOR
const ModuloPrestador = {
    init: function() {
        console.log('Módulo Prestador inicializado');
        this.initDashboard();
        this.initExportacion();
    },
    
    initDashboard: function() {
        // TODO: Cargar visitas del prestador
        console.log('Dashboard prestador listo');
    },
    
    initExportacion: function() {
        const btnExport = document.querySelector('#btn-exportar');
        if (btnExport) {
            btnExport.addEventListener('click', this.exportarDatos);
        }
    },
    
    exportarDatos: function() {
        Utils.showNotification('Generando reporte...', 'info');
        // TODO: Implementar exportación
    }
};

// 6. INICIALIZACIÓN GLOBAL
document.addEventListener('DOMContentLoaded', function() {
    // Detectar módulo actual basado en la URL
    const path = window.location.pathname;
    
    if (path.includes('/admin')) {
        TurismoApp.state.currentModule = 'admin';
        ModuloAdmin.init();
    } else if (path.includes('/prestador')) {
        TurismoApp.state.currentModule = 'prestador';
        ModuloPrestador.init();
    } else {
        TurismoApp.state.currentModule = 'instituciones';
        ModuloInstituciones.init();
    }
    
    // Inicializar Bootstrap tooltips y popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    console.log(`Sistema de Turismo cargado - Módulo: ${TurismoApp.state.currentModule}`);
});