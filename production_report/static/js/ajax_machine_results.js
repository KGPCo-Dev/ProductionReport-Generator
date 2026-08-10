document.addEventListener('DOMContentLoaded', function() {
    const tableContainer = document.getElementById('dashboard-table-container');
    const tableTypeSelect = document.getElementById('table_type');

    if (!tableContainer || !tableTypeSelect) return;

    // Objeto para gestionar las órdenes que están en su "periodo de gracia" antes de ser eliminadas.
    // Formato: { "orderId": { timer: setTimeout_id, element: rowElement } }
    const pendingDeletion = {};
    const DELETION_GRACE_PERIOD = 120000; // 30 segundos en milisegundos. ¡Ajusta este valor!

    function updateTable() {
        const tableType = tableTypeSelect.value;
        const timestamp = new Date().getTime();
        
        // console.log('Actualizando tabla en segundo plano:', tableType); // Deshabilitado para producción
        
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
            // 1. Crear un contenedor temporal para analizar el nuevo HTML sin afectar el DOM actual.
            const tempContainer = document.createElement('div');
            tempContainer.innerHTML = html;

            const newTable = tempContainer.querySelector('table');
            if (!newTable) return; // Si no hay tabla en la respuesta, no hacemos nada.

            const currentTableBody = tableContainer.querySelector('tbody');
            const newTableBody = newTable.querySelector('tbody');

            // 2. Obtener los IDs de las órdenes actuales y las nuevas.
            const currentOrderIds = new Set(Array.from(currentTableBody.querySelectorAll('tr[data-order-id]')).map(tr => tr.dataset.orderId));
            const newOrderIds = new Set(Array.from(newTableBody.querySelectorAll('tr[data-order-id]')).map(tr => tr.dataset.orderId));

            // 3. Identificar órdenes que desaparecieron.
            currentOrderIds.forEach(orderId => {
                if (!newOrderIds.has(orderId) && !pendingDeletion[orderId]) {
                    const rowElement = document.getElementById(`order-row-${orderId}`);
                    if (rowElement) {
                        console.log(`Orden ${orderId} desapareció. Iniciando periodo de gracia.`);
                        
                        // Mover la fila al principio de la tabla
                        rowElement.parentElement.prepend(rowElement);

                        // Aplicar clase y variable CSS para la animación
                        rowElement.style.setProperty('--deletion-grace-period', `${DELETION_GRACE_PERIOD}ms`);
                        rowElement.classList.add('row-pending-deletion');
                        
                        // Iniciar temporizador para eliminar la fila después del periodo de gracia.
                        const timer = setTimeout(() => {
                            rowElement.remove();
                            delete pendingDeletion[orderId];
                        }, DELETION_GRACE_PERIOD);

                        pendingDeletion[orderId] = { timer, element: rowElement };
                    }
                }
            });

            // 4. Identificar órdenes que reaparecieron o son nuevas.
            newOrderIds.forEach(orderId => {
                // Si la orden estaba pendiente de eliminación, cancelamos el proceso.
                if (pendingDeletion[orderId]) {
                    console.log(`Orden ${orderId} reapareció. Cancelando eliminación.`);
                    clearTimeout(pendingDeletion[orderId].timer);
                    pendingDeletion[orderId].element.style.removeProperty('--deletion-grace-period');
                    pendingDeletion[orderId].element.classList.remove('row-pending-deletion');
                    delete pendingDeletion[orderId];
                }

                const newRow = newTableBody.querySelector(`#order-row-${orderId}`);
                const currentRow = currentTableBody.querySelector(`#order-row-${orderId}`);

                if (currentRow) {
                    // La fila ya existe, actualizamos su contenido.
                    currentRow.innerHTML = newRow.innerHTML;
                } else {
                    // La fila es nueva, la añadimos al final de la tabla.
                    currentTableBody.appendChild(newRow);
                }
            });

            // Manejar el caso de tabla vacía
            const noDataRow = newTableBody.querySelector('td[colspan]');
            const currentNoDataRow = currentTableBody.querySelector('td[colspan]');
            if (noDataRow && currentTableBody.children.length === 0) {
                currentTableBody.innerHTML = newTableBody.innerHTML;
            } else if (!noDataRow && currentNoDataRow) {
                currentNoDataRow.parentElement.remove();
            }

            // 5. Re-ordenar la tabla: pendientes de eliminación arriba, luego las completadas.
            const tableBody = tableContainer.querySelector('tbody');
            // Solo seleccionamos filas con datos, no la de "no se encontraron ordenes".
            const rows = Array.from(tableBody.querySelectorAll('tr[data-order-id]'));

            if (rows.length > 0) {
                rows.sort((a, b) => {
                    const getRank = (row) => {
                        if (row.classList.contains('row-pending-deletion')) {
                            return 0; // Máxima prioridad: a punto de ser eliminadas.
                        }
                        // Buscamos las insignias de estado "Realizado".
                        const doneBadges = row.querySelectorAll('.status-badge-done');
                        if (doneBadges.length === 2) {
                            return 1; // Segunda prioridad: completadas.
                        }
                        return 2; // Prioridad normal.
                    };
                    return getRank(a) - getRank(b);
                });
                rows.forEach(row => tableBody.appendChild(row));
            }
        })
        .catch(error => {
            console.error('Fallo en la sincronización con la base de datos', error);
        });
    }

    // Ejecutar la primera vez y luego cada 5 segundos.
    updateTable();
    setInterval(updateTable, 20000);
});
