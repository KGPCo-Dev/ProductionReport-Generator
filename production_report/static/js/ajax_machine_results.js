document.addEventListener('DOMContentLoaded', function() {
    const tableContainer = document.getElementById('dashboard-table-container');
    const tableTypeSelect = document.getElementById('table_type');

    if (!tableContainer || !tableTypeSelect) return;

    function updateTable() {

        const tableType = tableTypeSelect.value;
        const timestamp = new Date().getTime();
        
        console.log('Actualizando tabla en segundo plano:', tableType);
        
        fetch(`${window.location.pathname}?partial=true&table_type=${tableType}&_=${timestamp}`, {
            method: 'GET',
            cache: 'no-store',
            headers: { 'Cache-Control': 'no-cache' }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al actualizar la tabla de monitoreo')
            }
            return response.text();
        })
        .then(html => {
         
            tableContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Fallo en la sincronizacion con las base de datos', error);
        });
    }

    setInterval(updateTable, 5000);
})