document.addEventListener('DOMContentLoaded', function() {
    const tableContainer = document.getElementById('machine-assignation-container');

    if (!tableContainer) return;

    function updateTable() {

        console.log('updateTable inicializado');
        
        fetch('?partial=true')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al actualizar la tabla de monitoreo')
            }
            return response.text();
        })
        .then(html => {
            if (html.trim()) {
                tableContainer.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Fallo en la sincronizacion con las base de datos', error);
        });
    }

    setInterval(updateTable, 5000);
})