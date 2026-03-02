/**
 * Función genérica para cerrar alertas automáticamente
 * @param {string} alertId - ID del elemento de alerta
 * @param {number} delayMs - Tiempo en milisegundos antes de desaparecer (default: 1500)
 */
function autoCloseAlert(alertId, delayMs = 1500) {
    const alert = document.getElementById(alertId);
    if (alert) {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, delayMs);
    }
}

/**
 * Cierra todas las alertas automáticamente (útil para múltiples alertas)
 * @param {string} containerSelector - Selector CSS del contenedor de alertas
 * @param {number} delayMs - Tiempo en milisegundos antes de desaparecer
 */
function autoCloseAllAlerts(containerSelector = '.alert', delayMs = 1500) {
    const alerts = document.querySelectorAll(containerSelector);
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, delayMs);
    });
}

/**
 * Escucha cambios en un contenedor y cierra alertas nuevas automáticamente
 * @param {string} containerId - ID del contenedor donde aparecen alertas
 * @param {number} delayMs - Tiempo en milisegundos antes de desaparecer
 */
function autoCloseNewAlerts(containerId, delayMs = 1500) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const observer = new MutationObserver(() => {
        const alerts = container.querySelectorAll('.alert');
        alerts.forEach(alert => {
            // Solo procesar alertas que no tengan el atributo data-processed
            if (!alert.hasAttribute('data-processed')) {
                alert.setAttribute('data-processed', 'true');
                autoCloseAlert(alert.id, delayMs);
            }
        });
    });

    // Observar cambios en el contenedor
    observer.observe(container, {
        childList: true,
        subtree: true
    });
}
