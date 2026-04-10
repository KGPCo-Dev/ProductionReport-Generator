from django.shortcuts import render
from reports.models import ProcessNames
from reports.queries import get_order_details, get_fails_results
from django.db.models import F

def order_tracker_view(request):

    build_id = request.GET.get('search')
    report_type = request.GET.get('report_type', 'order_process_results')
    order_details = None
    test2_results = None
    process_results = None
    order_progress = None

    if request.method == 'GET':
        if build_id:

            order_details = get_order_details(build_id)
            process_results = get_process_results(request, build_id)
            test2_results = get_test2_results(request, build_id)

            if order_details and process_results and process_results[0]:
                order_progress = get_tethers_status(order_details, process_results)


    return render(request,'order_tracker/order_tracker_preview.html', { 
        'build_id': build_id,
        'process_results': process_results,
        'test2_results': test2_results,
        'order_details': order_details,
        'report_type': report_type,
        'order_progress': order_progress
     })


def get_process_results(request, build_id):

    report_type = request.GET.get('report_type', 'order_process_results')

    # DB connection and config is created #
    config = REPORT_CONFIG.get(report_type, REPORT_CONFIG['order_process_results'])
    query = config['query']
    fails_results = get_fails_results(build_id)
    results = []
    headers = []

    if fails_results:
        fails_headers = [col[0] for col in fails_results_cursor.description]

    with connection.cursor() as process_results_cursor:
        process_results_cursor.execute(query, [build_id])
        results = dict_fetch_all(process_results_cursor)

        if results:
            headers = [col[0] for col in process_results_cursor.description]

            # ProcesName is assigned insted of use proces.id number #
            for row in results:
                original_name = row['Proceso']
                try:
                    row['Proceso'] = ProcessNames(original_name).label
                except ValueError:
                    row['Proceso'] = f"Desconocido ({ original_name })"
            
            # fails Column is created and a list of dict is attatched to it #
            for row in results:
                row['fails'] = [ 
                    { 
                        'Descripcion': fail['fail_description'],
                        'Intentos': fail['fail_amount']
                    }
                    for fail in fails_results 
                    if fail['process_id'] == row['process_id'] 
                    and fail['global_tether'] == row['Numero de Tether']
                ]


    
    # Delete process_id value from headers if it exists #
    if results:
        headers_process = headers.pop(0)

    process_results = [results, headers]


    return process_results

def get_test2_results(request, build_id):

    report_type = request.GET.get('report_type', 'order_status_results')

    config = REPORT_CONFIG.get(report_type, REPORT_CONFIG['order_status_results'])
    query = config['query']
    
    results = []
    headers = []

    with connection.cursor() as cursor:
        cursor.execute(query, [build_id])
        results = dict_fetch_all(cursor)

        if results:
            headers = [col[0] for col in cursor.description]

    test2_results = [results, headers]

    return test2_results

def get_tethers_status(order_details, process_results):

    # In order to get the data for the TetherStatusView we need:
    #   get_tethers_status: List  of dict with the current state of oders's tethers
    #   total_tethers: oreder's tethers to render the amount of them
    #   results: we get the progress for current order
    #   tethers_data: dict with current status of each tether#

    get_tethers_status = []

    try:
        total_tethers = int(order_details[0].get('tethers', 0))
    except (ValueError, IndexError, TypeError):
        total_tethers = 0

    results = process_results[0] if process_results and process_results[0] else []
    
    for i in range(1, total_tethers + 1):
        tethers_data = { 
            'number': i,
            'percentage': 0,
            'current_process': 'Sin registrar',
            'workplace': '-',
            'location': 'Sin montar',
            'is_complete': False
        }

        tethers_scans = [r for r in results if r.get('Numero de Tether') == i]

        if tethers_scans:
            lastest = max(tethers_scans, key=lambda x: x.get('Fecha'))
            last_process = lastest.get('process_id', 0)

            print("Last Process value:", last_process)

            percentage = (last_process / 8) * 100
            if percentage > 100: percentage = 100

            if last_process == 9:
                percentage = (1 / 8) * 100

            tethers_data.update({
                'percentage': int(percentage),
                'current_process': lastest.get('Proceso', 'Sin registrar'),
                'workplace': lastest.get('Estacion', '-'),
                'location': lastest.get('Locacion', 'Sin montar'),
                'is_complete': last_process >= 8 and last_process != 9
             })
        get_tethers_status.append(tethers_data)    

    return get_tethers_status
