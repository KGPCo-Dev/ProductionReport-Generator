from datetime import tzinfo
from email.utils import localtime
from django.shortcuts import render
from django.http import HttpResponse
from .models import KgpTest2Results
import openpyxl
from django.utils import timezone
from django.db import connection
from .queries import REPORT_CONFIG

def dicfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]

def production_report_view(request):
    results = None
    headers = None
    report_type = request.GET.get('report_type', 'production_report')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    shift = request.GET.get('shift', 'all')

    if request.method == 'GET':
        if start_date and end_date:
            params = [start_date, end_date]
            shift_clause = ""
            if shift in ['1', '2']:
                shift_clause = "AND results.production_shift = %s"
                params.append(int(shift))
            
            config = REPORT_CONFIG.get(report_type, REPORT_CONFIG['production_report'])
            query = config['query'].format(shift_clause=shift_clause)

            with connection.cursor() as cursor:
                cursor.execute(query, params)
                results = dicfetchall(cursor)

                if results:
                    headers = [col[0] for col in cursor.description]

            if 'export' in request.GET:
                return export_to_excel(results, headers, config['filename'], config['sheet_name'])

    return render(request, 'reports/report_preview.html', { 
        'results': results,
        'headers': headers,
        'start_date': start_date,
        'end_date': end_date,
        'shift': shift,
        'report_type': report_type
     })

def export_to_excel(data, headers, filename_prefix="Reporte", sheet_name="Resultados"):
    if not data or not headers:
        return HttpResponse("No hay datos para exportar")

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename_prefix}.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    ws.append(headers)

    for row in data:
        row_data = []
        for header in headers:

            value = row.get(header)
            if value and hasattr(value, 'tzinfo'):
                value = timezone.localtime(value).replace(tzinfo=None)
            row_data.append(value)
        ws.append(row_data)
    wb.save(response)
    return response
