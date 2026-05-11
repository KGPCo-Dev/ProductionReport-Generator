
function editDeliveryDate(updateUrl) {

    const buildId = document.getElementById('current_build_id').innerText.trim();
    const currentDate = document.getElementById('display_delivery_date').innerText.trim()

    Swal.fire({
        title: 'Actualizar Fecha de Entrega',
        html:'<input type="date" id="swal-input-date" class="swal2-input" value="' + currentDate + '">',
        showCancelButton: true,
        confirmButton: true,
        confirmButtonText:`Aceptar`,
        cancelButtonText: 'Cancelar',
        customClass: {
            cancelButton: 'kgp-cancel-button',
            confirmButton: 'kgp-confirm-button'
        },
        preConfirm: () => {
            const newDate = document.getElementById('swal-input-date').value;
            if (!newDate) {
                Swal.showValidationMessage('Selecciona una fecha valida');
            }
            return newDate;
        }
    }).then((result) =>{
        if (result.isConfirmed) {
            const newDate = result.value;
            Swal.fire({
                title:'Guardando...',
                allowOutsideClick: false,
                didOpen: () => {Swal.showLoading();}
            });

            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]') ? 
                                document.querySelector('[name=csrfmiddlewaretoken]').value : 
                                getCookie('csrftoken');

            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    build_id: buildId,
                    new_date: newDate
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('Actualizado!', data.message, 'success');
                    document.getElementById('display_delivery_date').innerText = newDate;
                } else {
                    Swal.fire('Accesso Denegado', data.error || 'Ocurrio un error', 'error');
                }
            })
            .catch(error => {
                    Swal.fire('Error', 'No se pudo conectar con el servidor', 'error');
                });
        }
    });

}
