document.addEventListener('DOMContentLoaded', function () { const tableContainer = document.getElementById( 'dashboard-table-container' ); const tableTypeSelect = document.getElementById('table_type');

if (!tableContainer || !tableTypeSelect) return;

// =========================================================
// CONFIGURACIÓN
// =========================================================

const DELETION_GRACE_PERIOD = 120000; // 2 minutos
const PAGE_SIZE = 8;                  // 8 órdenes por página
const PAGE_DURATION = 20000;          // 20 segundos por página
const REQUEST_TIMEOUT = 30000;        // Timeout de 30 segundos
const INITIAL_RETRY_DELAY = 20000;    // Primer reintento: 20 segundos
const MAX_RETRY_DELAY = 120000;        // Máximo: 2 minutos
const MAX_RETRY_ATTEMPTS = 5;          // Reintentos consecutivos

// Órdenes pendientes de eliminación.
const pendingDeletion = {};

let currentPage = 0;
let cycleTimer = null;
let requestController = null;
let requestInProgress = false;
let pageIsLeaving = false;
let retryDelay = INITIAL_RETRY_DELAY;
let retryAttempts = 0;
let activeRequestId = 0;

// =========================================================
// UTILIDADES
// =========================================================

function getCurrentRows() {
    const tableBody = tableContainer.querySelector('tbody');

    if (!tableBody) return [];

    return Array.from(
        tableBody.querySelectorAll('tr[data-order-id]')
    );
}

function clearCycleTimer() {
    if (cycleTimer !== null) {
        clearTimeout(cycleTimer);
        cycleTimer = null;
    }
}

function getRowRank(row) {
    if (row.classList.contains('row-pending-deletion')) {
        return 0;
    }

    const doneBadges = row.querySelectorAll(
        '.status-badge-done'
    );

    if (doneBadges.length === 2) {
        return 1;
    }

    return 2;
}

function reorderRows(tableBody) {
    const rows = Array.from(
        tableBody.querySelectorAll('tr[data-order-id]')
    );

    rows.sort((a, b) => getRowRank(a) - getRowRank(b));

    rows.forEach(row => tableBody.appendChild(row));
}

// =========================================================
// PAGINACIÓN
// =========================================================

function renderPagination() {
    const tableBody = tableContainer.querySelector('tbody');

    if (!tableBody) return;

    const isSubassembly =
        tableTypeSelect.value === 'subassembly_status_table';

    const rows = Array.from(
        tableBody.querySelectorAll('tr[data-order-id]')
    );

    // En máquinas de corte se muestran todas las filas.
    if (!isSubassembly || rows.length === 0) {
        rows.forEach(row => {
            row.style.display = '';
        });

        return;
    }

    const totalPages = Math.ceil(rows.length / PAGE_SIZE);

    if (currentPage >= totalPages || currentPage < 0) {
        currentPage = 0;
    }

    const startIndex = currentPage * PAGE_SIZE;
    const endIndex = startIndex + PAGE_SIZE;

    rows.forEach((row, index) => {
        row.style.display =
            index >= startIndex && index < endIndex
                ? ''
                : 'none';
    });
}

// =========================================================
// PROGRAMACIÓN DE LA SIGUIENTE ACTUALIZACIÓN
// =========================================================

function scheduleNextCycle(delay = PAGE_DURATION) {
    if (pageIsLeaving) return;

    clearCycleTimer();

    cycleTimer = setTimeout(() => {
        cycleTimer = null;

        if (pageIsLeaving) return;

        // No iniciar una petición mientras exista otra activa.
        if (requestInProgress) return;

        const isSubassembly =
            tableTypeSelect.value === 'subassembly_status_table';

        const rows = getCurrentRows();

        const totalPages =
            Math.ceil(rows.length / PAGE_SIZE) || 1;

        if (
            isSubassembly &&
            rows.length > PAGE_SIZE &&
            currentPage + 1 < totalPages
        ) {
            // Mostrar la siguiente página del carrusel.
            currentPage++;

            renderPagination();
            scheduleNextCycle();

        } else {
            // Terminó el carrusel: consultar nuevamente el servidor.
            currentPage = 0;
            updateTable();
        }
    }, delay);
}

// =========================================================
// PERÍODO DE GRACIA PARA ÓRDENES DESAPARECIDAS
// =========================================================

function markOrderForDeletion(orderId, rowElement) {
    if (pendingDeletion[orderId]) return;

    // La fila debe seguir presente antes de marcarla.
    if (!rowElement.isConnected) return;

    rowElement.style.setProperty(
        '--deletion-grace-period',
        `${DELETION_GRACE_PERIOD}ms`
    );

    rowElement.classList.add('row-pending-deletion');

    const timer = setTimeout(() => {
        if (pendingDeletion[orderId]?.element === rowElement) {
            rowElement.remove();
            delete pendingDeletion[orderId];

            renderPagination();
        }
    }, DELETION_GRACE_PERIOD);

    pendingDeletion[orderId] = {
        timer,
        element: rowElement
    };

    // Las órdenes pendientes de eliminación aparecen primero.
    const tableBody = tableContainer.querySelector('tbody');

    if (tableBody) {
        tableBody.prepend(rowElement);
    }
}

function cancelPendingDeletion(orderId) {
    const pending = pendingDeletion[orderId];

    if (!pending) return;

    clearTimeout(pending.timer);

    pending.element.style.removeProperty(
        '--deletion-grace-period'
    );

    pending.element.classList.remove('row-pending-deletion');

    delete pendingDeletion[orderId];
}

// =========================================================
// PROCESAMIENTO DE LA TABLA RECIBIDA
// =========================================================

function processTableResponse(html) {
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = html;

    const newTable = tempContainer.querySelector('table');

    if (!newTable) {
        throw new Error(
            'La respuesta del servidor no contiene una tabla.'
        );
    }

    const newTableBody = newTable.querySelector('tbody');
    const currentTableBody = tableContainer.querySelector('tbody');

    if (!newTableBody || !currentTableBody) {
        throw new Error(
            'No se encontró el cuerpo de la tabla (tbody).'
        );
    }

    // Identificar las órdenes actuales y las recibidas.
    const currentRows = Array.from(
        currentTableBody.querySelectorAll('tr[data-order-id]')
    );

    const newRows = Array.from(
        newTableBody.querySelectorAll('tr[data-order-id]')
    );

    const currentOrderIds = new Set(
        currentRows.map(row => row.dataset.orderId)
    );

    const newOrderIds = new Set(
        newRows.map(row => row.dataset.orderId)
    );

    // 1. Órdenes que desaparecieron: iniciar período de gracia.
    currentOrderIds.forEach(orderId => {
        if (!newOrderIds.has(orderId)) {
            const rowElement = currentRows.find(
                row => row.dataset.orderId === orderId
            );

            if (rowElement) {
                markOrderForDeletion(orderId, rowElement);
            }
        }
    });

    // 2. Órdenes nuevas o que reaparecieron.
    newRows.forEach(newRow => {
        const orderId = newRow.dataset.orderId;

        // Si reaparece, cancelar la eliminación pendiente.
        cancelPendingDeletion(orderId);

        const currentRow = Array.from(
            currentTableBody.querySelectorAll('tr[data-order-id]')
        ).find(row => row.dataset.orderId === orderId);

        if (currentRow) {
            // Actualizar el contenido conservando el elemento DOM.
            currentRow.innerHTML = newRow.innerHTML;

        } else {
            // Agregar la nueva orden.
            currentTableBody.appendChild(newRow);
        }
    });

    // 3. Manejo de la tabla sin datos.
    const noDataRow = newTableBody.querySelector('td[colspan]');
    const currentNoDataRow =
        currentTableBody.querySelector('td[colspan]');

    if (noDataRow && currentTableBody.children.length === 0) {
        currentTableBody.innerHTML = newTableBody.innerHTML;

    } else if (!noDataRow && currentNoDataRow) {
        currentNoDataRow.parentElement.remove();
    }

    // 4. Reordenar: pendientes de eliminación, completadas y restantes.
    reorderRows(currentTableBody);

    // 5. Aplicar paginación.
    renderPagination();
}

// =========================================================
// ACTUALIZACIÓN AJAX CON TIMEOUT Y CONTROL DE ERRORES
// =========================================================

async function updateTable() {
    if (pageIsLeaving || requestInProgress) return;

    requestInProgress = true;

    const requestId = ++activeRequestId;
    const tableType = tableTypeSelect.value;

    const url =
        `${window.location.pathname}` +
        `?partial=true` +
        `&table_type=${encodeURIComponent(tableType)}` +
        `&_=${Date.now()}`;

    const controller = new AbortController();

    requestController = controller;

    let timedOut = false;
    let nextDelay = PAGE_DURATION;

    const timeoutId = setTimeout(() => {
        timedOut = true;
        controller.abort();
    }, REQUEST_TIMEOUT);

    try {
        const response = await fetch(url, {
            method: 'GET',
            cache: 'no-store',
            signal: controller.signal,
            headers: {
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const html = await response.text();

        if (pageIsLeaving || requestId !== activeRequestId) {
            return;
        }

        // Procesar el contenido recibido.
        processTableResponse(html);

        // Reiniciar los reintentos después de una actualización correcta.
        retryAttempts = 0;
        retryDelay = INITIAL_RETRY_DELAY;

        nextDelay = PAGE_DURATION;

    } catch (error) {
        if (pageIsLeaving) return;

        if (timedOut) {
            console.warn(
                `[Dashboard] Timeout después de ` +
                `${REQUEST_TIMEOUT / 1000} segundos.`
            );

        } else if (error.name === 'AbortError') {
            console.info(
                '[Dashboard] Petición cancelada.'
            );

        } else {
            console.error(
                '[Dashboard] Error de actualización:',
                error.message || error
            );
        }

        retryAttempts++;

        if (retryAttempts <= MAX_RETRY_ATTEMPTS) {
            // Reintentos progresivos: 20, 40, 80, 120, 120 segundos.
            nextDelay = retryDelay;

            retryDelay = Math.min(
                retryDelay * 2,
                MAX_RETRY_DELAY
            );

            console.warn(
                `[Dashboard] Reintento ${retryAttempts}/` +
                `${MAX_RETRY_ATTEMPTS} en ` +
                `${Math.round(nextDelay / 1000)} segundos.`
            );

        } else {
            // Evitar reintentos demasiado frecuentes cuando el
            // servidor sigue sin responder.
            nextDelay = MAX_RETRY_DELAY;

            retryDelay = MAX_RETRY_DELAY;

            console.error(
                '[Dashboard] Se alcanzó el límite de reintentos. ' +
                'Se continuará intentando cada 120 segundos.'
            );
        }

    } finally {
        clearTimeout(timeoutId);

        if (requestController === controller) {
            requestController = null;
        }

        requestInProgress = false;

        // La siguiente actualización se programa al terminar
        // la petición actual, tanto si tuvo éxito como si falló.
        if (!pageIsLeaving) {
            scheduleNextCycle(nextDelay);
        }
    }
}

// =========================================================
// CAMBIO DE TIPO DE TABLA
// =========================================================

tableTypeSelect.addEventListener('change', () => {
    // Evitar que una respuesta de la tabla anterior se procese
    // después de seleccionar otro tipo de tabla.
    activeRequestId++;

    if (requestController) {
        requestController.abort();
    }

    currentPage = 0;
    retryAttempts = 0;
    retryDelay = INITIAL_RETRY_DELAY;

    // El formulario original recarga la página al cambiar
    // de tabla, por lo que no iniciamos otra petición aquí.
});

// =========================================================
// LIMPIEZA AL ABANDONAR LA PÁGINA
// =========================================================

window.addEventListener('pagehide', () => {
    pageIsLeaving = true;

    clearCycleTimer();

    activeRequestId++;

    if (requestController) {
        requestController.abort();
        requestController = null;
    }

    Object.values(pendingDeletion).forEach(item => {
        clearTimeout(item.timer);
    });

    Object.keys(pendingDeletion).forEach(orderId => {
        delete pendingDeletion[orderId];
    });
});

// =========================================================
// INICIALIZACIÓN
// =========================================================

renderPagination();
scheduleNextCycle();
});