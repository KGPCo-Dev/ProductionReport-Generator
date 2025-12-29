from django.shortcuts import render
from django.http import HttpResponse
from .models import KgpTest2Results
import openpyxl
from django.utils import timezone
from django.db import connection

def report_produccion_view(request):
    results = None
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if request.method == 'POST':
        print("--- DEBUG: Se recibió una petición POST ---")
        if start_date and end_date:
            print(f"--- DEBUG: Fechas recibidas: {start_date} hasta {end_date} ---")

            query = """
                SELECT
                    results.entered_date,
                    CASE EXTRACT(DOW FROM (results.entered_date - INTERVAL '7 hours'))
                        WHEN 0 THEN 'Domingo'
                        WHEN 1 THEN 'Lunes'
                        WHEN 2 THEN 'Martes'
                        WHEN 3 THEN 'Miércoles'
                        WHEN 4 THEN 'Jueves'
                        WHEN 5 THEN 'Viernes'
                        WHEN 6 THEN 'Sábado'
                    END AS adjusted_day,
                    (results.entered_date - INTERVAL '7 hours')::DATE AS adjusted_date,
                    results.build_id,
                    orders.cable_type,
                    results.employee_number,
                    results.workplace,
                    results.production_cell,
                    results.production_shift
                FROM public.kgp_test2_results results
                JOIN public.kgp_production_orders orders ON results.build_id = orders.build_id
                WHERE results.workplace IS NOT NULL
                AND results.result_status != 'Rework'
                ORDER BY results.entered_date;
            """

            if 'export' in request.POST:
                return export_to_excel(results)
    
    print(f"--- DEBUG: Valor final de 'results' antes del render: {results} ---")
    return render(request, 'reports/report_preview.html', { 
        'results': results,
        'start_date': start_date,
        'end_date': end_date
     })

def export_to_excel(data):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Produccion.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resultados de Produccion"

    columns = ['Fecha', 'Dia', 'Fecha de Produccion', 'Order', 'Tipo de Cable', 'Empleado', 'Estacion', 'Celda', 'Turno']
    ws.append(columns)

    for row in data:

        date = row['entered_date']
        if date:
            date = timezone.localtime(date).replace(tzinfo=None)

        ws.append([ 
            date,
            row['adjusted_day'],
            row['adjusted_date'],
            row['build_id'],
            row['cable_type'],
            row['employee_number'],
            row['workplace'],
            row['production_cell'],
            row['production_shift']

         ])
    
    wb.save(response)
    return response