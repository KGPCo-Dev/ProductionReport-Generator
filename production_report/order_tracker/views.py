from django.shortcuts import render
from django.db import connection
from reports.queries import REPORT_CONFIG, ORDER_DETAILS_QUERY, ORDER_FAIL_RESULTS_QUERY
from reports.models import ProcessNames


def dicfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]

def order_tracker_view(request):

    build_id = request.GET.get('search')
    report_type = request.GET.get('report_type', 'order_process_results')
    test2_report_type = request.GET.get('report_type', 'production_report')
    results = None
    order_details = None
    headers = None
    test2_results = None
    process_results = None

    if request.method == 'GET':
        if build_id:

            process_results = get_process_results(request, build_id)
            test2_results = get_test2_results(request, build_id)
            
            production_orders_query = ORDER_DETAILS_QUERY

            with connection.cursor() as order_details_cursor:
                # Order Details Query #
                order_details_cursor.execute(production_orders_query, [build_id])
                order_details = dicfetchall(order_details_cursor)

    return render(request,'order_tracker/order_tracker_preview.html', { 
        'build_id': build_id,
        'process_results': process_results,
        'test2_results': test2_results,
        'order_details': order_details,
        'report_type': report_type
     })


def get_process_results(request, build_id):

    report_type = request.GET.get('report_type', 'order_process_results')
    print("report_type value on process_results:", report_type)

    # DB connection and config is created #
    config = REPORT_CONFIG.get(report_type, REPORT_CONFIG['order_process_results'])
    query = config['query']
    fails_results_query = ORDER_FAIL_RESULTS_QUERY
    results = []
    headers = []

    

    with connection.cursor() as fails_results_cursor:
        fails_results_cursor.execute(fails_results_query, [build_id])
        fails_results = dicfetchall(fails_results_cursor)


        if fails_results:
            fails_headers = [col[0] for col in fails_results_cursor.description]


    with connection.cursor() as process_results_cursor:
        process_results_cursor.execute(query, [build_id])
        results = dicfetchall(process_results_cursor)

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
        headers_process= headers.pop(0)

    print("Resultados en views: ", results)
    print("Headers en views: ", headers)


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
        results = dicfetchall(cursor)

        if results:
            headers = [col[0] for col in cursor.description]

    test2_results = [results, headers]

    return test2_results
