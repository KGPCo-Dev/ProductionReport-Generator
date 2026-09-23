document.addEventListener('DOMContentLoaded', function() {
    const tableContainer = document.getElementById('dashboard-table-container');
    const tableTypeSelect = document.getElementById('table_type');

    if (!tableContainer || !tableTypeSelect) return;

    // Configuración general
    const pendingDeletion = {};
    const DELETION_GRACE_PERIOD = 120000; // 2 minutos (120 seg)
    const PAGE_SIZE = 8;                  // 8 registros por vista
    const PAGE_DURATION = 20000;          // 20 segundos por vista
    
    let currentPage = 0;
    let cycleTimer = null;

    // Aplica la visibilidad de filas según la página actual
    function renderPagination() {
        const tableBody = tableContainer.querySelector('tbody');
        if (!tableBody) return;

        const isSubassembly = tableTypeSelect.value === 'subassembly_status_table';
        const rows = Array.from(tableBody.querySelectorAll('tr[data-order-id]'));

        // Si es máquinas o no hay filas, mostramos todo normalmente
        if (!isSubassembly || rows.length === 0) {
            rows.forEach(row => row.style.display = '');
            return;
        }

        const totalPages = Math.ceil(rows.length / PAGE_SIZE);
        if (currentPage >= totalPages) {
            currentPage = 0;
        }

        const startIndex = currentPage * PAGE_SIZE;
        const endIndex = startIndex + PAGE_SIZE;

        rows.forEach((row, index) => {
            if (index >= startIndex && index < endIndex) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // Programa el siguiente paso del ciclo (20 segundos)
    function scheduleNextCycle() {
        if (cycleTimer) clearTimeout(cycleTimer);

        cycleTimer = setTimeout(() => {
            const isSubassembly = tableTypeSelect.value === 'subassembly_status_table';
            const tableBody = tableContainer.querySelector('tbody');
            const rows = tableBody ? Array.from(tableBody.querySelectorAll('tr[data-order-id]')) : [];
            const totalPages = Math.ceil(rows.length / PAGE_SIZE) || 1;

            if (isSubassembly && rows.length > PAGE_SIZE && (currentPage + 1) < totalPages) {
                // Aún hay más páginas del query actual por mostrar
                currentPage++;
                renderPagination();
                scheduleNextCycle();
            } else {
                // Finalizó el carrusel completo o es máquinas: consultamos de nuevo a la BD
                currentPage = 0;
                updateTable();
            }
        }, PAGE_DURATION);
    }

    // Consulta la base de datos y actualiza el DOM
    function updateTable() {
        const tableType = tableTypeSelect.value;
        const timestamp = new Date().getTime();

        fetch(`${window.location.pathname}?partial=true&table_type=${tableType}&_=${timestamp}`, {
            method: 'GET',
            cache: 'no-store',
            headers: { 'Cache-Control': 'no-cache' }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al actualizar la tabla de monitoreo');
            }
            return response.text();
        })
        .then(html => {
            const tempContainer = document.createElement('div');
            tempContainer.innerHTML = html;

            const newTable = tempContainer.querySelector('table');
            if (!newTable) {
                scheduleNextCycle();
                return;
            }

            const currentTableBody = tableContainer.querySelector('tbody');
            const newTableBody = newTable.querySelector('tbody');

            const currentOrderIds = new Set(Array.from(currentTableBody.querySelectorAll('tr[data-order-id]')).map(tr => tr.dataset.orderId));
            const newOrderIds = new Set(Array.from(newTableBody.querySelectorAll('tr[data-order-id]')).map(tr => tr.dataset.orderId));

            // 1. Manejo de órdenes que desaparecen (Periodo de Gracia)
            currentOrderIds.forEach(orderId => {
                if (!newOrderIds.has(orderId) && !pendingDeletion[orderId]) {
                    const rowElement = document.getElementById(`order-row-${orderId}`);
                    if (rowElement) {
                        rowElement.parentElement.prepend(rowElement);
                        rowElement.style.setProperty('--deletion-grace-period', `${DELETION_GRACE_PERIOD}ms`);
                        rowElement.classList.add('row-pending-deletion');

                        const timer = setTimeout(() => {
                            rowElement.remove();
                            delete pendingDeletion[orderId];
                            renderPagination();
                        }, DELETION_GRACE_PERIOD);

                        pendingDeletion[orderId] = { timer, element: rowElement };
                    }
                }
            });

            // 2. Manejo de órdenes nuevas o que reaparecen
            newOrderIds.forEach(orderId => {
                if (pendingDeletion[orderId]) {
                    clearTimeout(pendingDeletion[orderId].timer);
                    pendingDeletion[orderId].element.style.removeProperty('--deletion-grace-period');
                    pendingDeletion[orderId].element.classList.remove('row-pending-deletion');
                    delete pendingDeletion[orderId];
                }

                const newRow = newTableBody.querySelector(`#order-row-${orderId}`);
                const currentRow = currentTableBody.querySelector(`#order-row-${orderId}`);

                if (currentRow) {
                    currentRow.innerHTML = newRow.innerHTML;
                } else if (newRow) {
                    currentTableBody.appendChild(newRow);
                }
            });

            // 3. Manejo de estado vacío
            const noDataRow = newTableBody.querySelector('td[colspan]');
            const currentNoDataRow = currentTableBody.querySelector('td[colspan]');
            if (noDataRow && currentTableBody.children.length === 0) {
                currentTableBody.innerHTML = newTableBody.innerHTML;
            } else if (!noDataRow && currentNoDataRow) {
                currentNoDataRow.parentElement.remove();
            }

            // 4. Re-ordenar (eliminaciones pendientes primero, luego realizadas)
            const rows = Array.from(currentTableBody.querySelectorAll('tr[data-order-id]'));
            if (rows.length > 0) {
                rows.sort((a, b) => {
                    const getRank = (row) => {
                        if (row.classList.contains('row-pending-deletion')) return 0;
                        const doneBadges = row.querySelectorAll('.status-badge-done');
                        if (doneBadges.length === 2) return 1;
                        return 2;
                    };
                    return getRank(a) - getRank(b);
                });
                rows.forEach(row => currentTableBody.appendChild(row));
            }

            // 5. Aplicar visibilidad de los 8 elementos y agendar siguiente cambio
            renderPagination();
            scheduleNextCycle();
        })
        .catch(error => {
            console.error('Fallo en la sincronización con la base de datos', error);
            scheduleNextCycle();
        });
    }

    // Inicialización inicial
    renderPagination();
    scheduleNextCycle();
});
