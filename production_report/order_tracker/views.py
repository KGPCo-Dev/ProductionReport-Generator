from django.shortcuts import render
from django.db import connection
from reports.queries import REPORT_CONFIG


def dicfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]

def order_tracker_view(request):

    build_id = request.GET.get('search')
    report_type = request.GET.get('report_type', 'order_status_report')
    results = None
    headers = None

    if request.method == 'GET':
        if build_id:

            config = REPORT_CONFIG.get(report_type, REPORT_CONFIG['order_status_report'])
            query = config['query']

            with connection.cursor() as cursor:
                cursor.execute(query, [build_id])
                results = dicfetchall(cursor)

                if results:
                    headers = [col[0] for col in cursor.description]

    return render(request,'order_tracker/order_tracker_preview.html', { 
        'build_id': build_id,
        'results': results,
        'headers': headers,
        'report_type': report_type
     })
