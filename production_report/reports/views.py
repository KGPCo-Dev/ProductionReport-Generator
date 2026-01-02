from django.shortcuts import render
from django.http import HttpResponse
from .models import KgpTest2Results
import openpyxl
from django.utils import timezone
from django.db import connection

def dicfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]

def production_report_view(request):
    results = None
    headers = None
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    shift = request.POST.get('shift', 'all')

    if request.method == 'POST':
        if start_date and end_date:
            params = [start_date, end_date]
            shift_clause = ""
            if shift in ['1', '2']:
                shift_clause = "AND results.production_shift = %s"
                params.append(int(shift))

            query = f"""
                SELECT
                    results.entered_date AS "Fecha de Registro",
                    CASE EXTRACT(DOW FROM (results.entered_date - INTERVAL '7 hours'))
                        WHEN 0 THEN 'Domingo'
                        WHEN 1 THEN 'Lunes'
                        WHEN 2 THEN 'Martes'
                        WHEN 3 THEN 'Miércoles'
                        WHEN 4 THEN 'Jueves'
                        WHEN 5 THEN 'Viernes'
                        WHEN 6 THEN 'Sábado'
                    END AS "Dia",
                    (results.entered_date - INTERVAL '7 hours')::DATE AS "Fecha de Produccion",
                    results.build_id AS "Orden",
                    orders.cable_type AS "Tipo de Cable",
                    results.employee_number AS "Empleado",
                    results.workplace AS "Estacion",
                    results.production_cell AS "Celda",
                    results.production_shift AS "Turno"
                FROM public.kgp_test2_results results
                JOIN public.kgp_production_orders orders ON results.build_id = orders.build_id
                WHERE results.entered_date >= (%s::DATE + INTERVAL '7 hours')
                    AND results.entered_date < (%s::DATE + INTERVAL '1 day' + INTERVAL '7 hours')
                    AND results.workplace IS NOT NULL
                    AND results.result_status != 'Rework'
                    {shift_clause}
                ORDER BY results.entered_date;
            """
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                results = dicfetchall(cursor)

                if results:
                    headers = [col[0] for col in cursor.description]

            if 'export' in request.POST:
                return export_to_excel(results)
    
    return render(request, 'reports/report_preview.html', { 
        'results': results,
        'headers': headers,
        'start_date': start_date,
        'end_date': end_date,
        'shift': shift
     })

def export_to_excel(data):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Produccion.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resultados de Produccion"

    columns = ['Fecha de Registro', 'Dia', 'Fecha de Produccion', 'Order', 'Tipo de Cable', 'Empleado', 'Estacion', 'Celda', 'Turno']
    ws.append(columns)

    for row in data:


        registered_date = row.get('Fecha de Registro')
        if registered_date and hasattr(registered_date, 'tzinfo'):
            registered_date = timezone.localtime(registered_date).replace(tzinfo=None)
        
        production_date = row.get('Fecha de Produccion')
        if production_date and hasattr(production_date, 'tzinfo'):
            production_date = timezone.localtime(production_date).replace(tzinfo=None)


        ws.append([ 
            registered_date,
            row['Dia'],
            production_date,
            row.get('build_id'),
            row.get('cable_type'),
            row.get('employee_number'),
            row.get('workplace'),
            row.get('production_cell'),
            row.get('production_shift')

         ])
    
    wb.save(response)
    return response
