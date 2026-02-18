from django.shortcuts import render
from django.http import HttpResponse
import openpyxl
from django.utils import timezone
from django.db import connection
from .queries import REPORT_CONFIG
import pandas as pd
import json
from django.utils.formats import date_format

def dicfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]

def production_report_view(request):
    results = None
    results = None
    headers = None
    chart_data = None
    production_results = []
    report_type = request.GET.get('report_type', 'production_report')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    shift = request.GET.get('shift', 'all')

    if request.method == 'GET':
        if start_date and end_date:
            is_short_range = False
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

                if cursor.description:
                    headers = [col[0] for col in cursor.description]
            
            #We create the structure to render de Dashboard
            results_df = pd.DataFrame(results, columns=headers)
            
            #We define if start and end date is bigger than one day to decide wich templete to use
            try:
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)

                if start_dt.date() == end_dt.date():
                    is_short_range = True
                else:
                    is_short_range = False

            except Exception as e:
                pass

            if not results_df.empty:
                chart_conf = config.get('chart_config')

                if chart_conf:
                    date_col = chart_conf['date_col']
                    hour_col = chart_conf['hour_col']
                    
                    if is_short_range and hour_col and hour_col in results_df.columns:
                        group_col = hour_col

                        graph_df = results_df.groupby(group_col).size().reset_index(name='Amount')
                        graph_df = graph_df.sort_values(by=group_col)

                        chart_labels = graph_df[group_col].to_list()

                    else:
                        results_df[date_col] = pd.to_datetime(results_df[date_col])

                        #We create a DF based on the results, grouped by Date#
                        graph_df = results_df.groupby(date_col).size().reset_index(name='Amount')
        
                        chart_labels = [date_format(date, "Y-F-d") for date in graph_df[date_col]]
                    
                    chart_values = graph_df['Amount'].tolist()
        
                    chart_data = { 
                        'labels': chart_labels,
                        'data': chart_values,
                        'label': chart_conf['label'],
                        'base_color': chart_conf['base_color'],
                        'lighter_color': chart_conf['lighter_color'],
                        'darker_color': chart_conf['darker_color']
                    }
                        

            if 'export' in request.GET:
                return export_to_excel(results, headers, config['filename'], config['sheet_name'])

            hour_col_name = config.get('chart_config', {}).get('hour_col')

            if hour_col_name and headers and results:
                if hour_col_name in headers:
                    headers.remove(hour_col_name)
                
                for row in results:
                    if hour_col_name in row:
                        del row[hour_col_name]

            if headers:
                production_results = [results, headers]
        

    return render(request, 'reports/report_preview.html', { 
        'results': results,
        'headers': headers,
        'start_date': start_date,
        'production_results': production_results,
        'end_date': end_date,
        'shift': shift,
        'report_type': report_type,
        'chart_data': json.dumps(chart_data) if chart_data else None
     })

def export_to_excel(data, headers, filename_prefix="Reporte", sheet_name="Resultados"):
    if not data or not headers:
        return HttpResponse("No hay datos para exportar")

    headers.append("Tethers")
    for result in data:
        result['Tethers'] = 1

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
