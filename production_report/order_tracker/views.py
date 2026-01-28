from django.shortcuts import render
from django.db import connection
from reports.queries import REPORT_CONFIG, ORDER_DETAILS_QUERY
from reports.models import ProcessNames


def dicfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]

def order_tracker_view(request):

    build_id = request.GET.get('search')
    report_type = request.GET.get('report_type', 'order_process_report')
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

    report_type = request.GET.get('report_type', 'order_process_report')
    print("report_type value on process_results:", report_type)

    config = REPORT_CONFIG.get(report_type, REPORT_CONFIG['order_process_report'])
    query = config['query']
    
    results = []
    headers = []

    with connection.cursor() as cursor:
        cursor.execute(query, [build_id])
        results = dicfetchall(cursor)

        if results:
            headers = [col[0] for col in cursor.description]

            for row in results:
                original_name = row['Proceso']
                try:
                    row['Proceso'] = ProcessNames(original_name).label
                except ValueError:
                    row['Proceso'] = f"Desconocido ({ original_name })"

    
    process_results = [results, headers]
    print("Headers on process_results", headers)
    return process_results

def get_test2_results(request, build_id):

    report_type = request.GET.get('report_type', 'order_status_report')
    print("report_type value on test2_results:", report_type)

    config = REPORT_CONFIG.get(report_type, REPORT_CONFIG['order_status_report'])
    query = config['query']
    
    results = []
    headers = []

    with connection.cursor() as cursor:
        cursor.execute(query, [build_id])
        results = dicfetchall(cursor)

        if results:
            headers = [col[0] for col in cursor.description]

    test2_results = [results, headers]
    print("Headers on test2_results", headers)
    return test2_results
