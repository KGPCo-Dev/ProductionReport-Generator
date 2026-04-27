document.getElementById('logoutConfirmBtn').addEventListener('click', function(){
    const url = this.getAttribute('data-url');

    Swal.fire({
        title:"<strong>Seguro que quieres cerrar sesion?</strong>",
        icon: 'info',
        html: `
            Puedes ingresar en cualquier otro momento usando tus credenciales.
        `,
        showCloseButton: true,
        showCancelButton: true,
        focusConfirm: false,
        confirmButtonText:`Cerrar Sesion`,
        cancelButtonText: `Cancelar`,
        customClass: {
            cancelButton: 'logout-cancel-button',
            confirmButton: 'log-out-confirm-button'

        }
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('logoutFormSecret').submit();
        }
    });
});