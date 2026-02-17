document.getElementById('btnExport').addEventListener('click', function() { 
    const noData = document.querySelector('.text-muted i.bi-search');

    if(noData) { 
        Swal.fire({ 
            tittle: 'Reporte vacio',
            text: 'No hay resultados para exportar',
            icon: 'info',
            confirmButtonColor: '#198754'
         });
     } else { 
        const form = this.closest('form');
        const urlParams = new URLSearchParams(new FormData(form));
        urlParams.append('export', '1');
        window.location.href = `${window.location.pathname}?${urlParams.toString()}`;
      }
 });