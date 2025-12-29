from django.shortcuts import render
from django.http import HttpResponse
from .models import KgpTest2Results
import openpyxl

def report_produccion_view(request):
    results = None
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if request.method == 'POST':
        if start_date and end_date:
            # CORRECCIÓN: Se usa doble guion bajo (__) para los filtros especiales como range
            results = KgpTest2Results.objects.filter(entered_date__range=[start_date, end_date])

            if 'export' in request.POST:
                return export_to_excel(results)
    
    return render(request, 'reports/report_preview.html', { 
        'results': results,
        'start_date': start_date,
        'end_date': end_date
     })

def export_to_excel(queryset):
    # CORRECCIÓN: 'application' lleva doble 'p'
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Produccion.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resultados de Produccion"

    columns = ['ID', 'Fecha', 'Build ID', 'Empleado', 'Resultado', 'Workplace']
    ws.append(columns)

    for row in queryset:
        date = row.entered_date.replace(tzinfo=None) if row.entered_date else ''
        ws.append([ 
            row.id,
            date,
            row.build_id,
            row.employee_number,
            row.result_status,
            row.workplace
         ])
    
    wb.save(response)
    return response