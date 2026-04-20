from datetime import timedelta
from reports.models import KgpTest2Results, KgpFinaltestResults, KgpProductionOrders, KpgProcessFails, KpgProductionProcessResults
from django.db.models import F
import pandas as pd

def get_single_order_test2_results(build_id):
  return KgpTest2Results.objects.filter(
    build=build_id
  ).exclude(
    result_status='Rework'
  ).exclude(
    workplace__isnull=True
  ).exclude(
    workplace__exact=''
  ).select_related('build')

def get_test2_results(start_date, end_date):
  return KgpTest2Results.objects.filter(
    entered_date__gte=start_date,
    entered_date__lt=end_date
  ).exclude(
    result_status='Rework'
  ).exclude(
    workplace__isnull=True
  ).exclude(
    workplace__exact=''
  )

def get_finaltest_results(start_date, end_date):
  return KgpFinaltestResults.objects.filter(
    entered_date__gte=start_date,
    entered_date__lt=end_date
    ).exclude(
      workplace__isnull=True
    ).exclude(
      workplace__exact=''
    )

def get_scrap_results(start_date, end_date):
  return KgpTest2Results.objects.filter(
    result_status='Scrap',
    entered_date__gte=start_date,
    entered_date__lt=end_date
  ).exclude(
    workplace__exact=''
  )

def get_order_details(build_id):
  return KgpProductionOrders.objects.filter(
    build=build_id
  ).first()

def get_fails_results(build_id):
  return KpgProcessFails.objects.filter(
    build=build_id
  ).select_related('fail').order_by('-fail_amount')

def get_process_results(build_id):
  return KpgProductionProcessResults.objects.filter(
    build=build_id
  ).select_related('process').order_by('-entered_date')

def get_scrap_report_data(start_date_str, end_date_str, shift=""):
  start_date = pd.to_datetime(start_date_str) + timedelta(hours=7)
  end_date = pd.to_datetime(end_date_str) + timedelta(days=1, hours=7)

  queryset = KgpTest2Results.objects.filter(
    entered_date__gte=start_date,
    entered_date__lt=end_date,
    result_status='Scrap'
  ).select_related('build')

  if shift in ['1', '2']:
    queryset = queryset.filter(production_shift=int(shift))

  data=[]
  days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

  for row in queryset:
    production_date = row.entered_date - timedelta(hours=7)

    data.append({
      "Orden": row.build.build if row.build else "-",
      "Fecha de Registro": row.entered_date.strftime('%Y-%m-%d'),
      "Hora de Registro": row.entered_date.strftime('%H:%M'),
      "Dia": days[production_date.weekday()],
      "Fecha de Incidencia": production_date.strftime('%Y-%m-%d'),
      "Tipo de Cable": row.build.cable_type if row.build else "-",
      "Empleado": row.employee_number if row.employee_number else "-",
      "Estacion": row.workstation if row.workstation else "-",
       "Hora": row.production_hour if row.production_hour else "-",
       "Turno": row.shift if row.shift else "0" 
    })
  return data

def get_production_report_date(start_date_str, end_date_str, shift=""):
  start_date = pd.to_datetime(start_date_str) + timedelta(hours=7)
  end_date = pd.to_datetime(end_date_str) + timedelta(days=1, hours=7)

  queryset = KgpTest2Results.objects.filter(
    entered_date__gte=start_date,
    entered_date__lt=end_date,
  ).exclude(
    workplace__isnull=True,
    workplace__exact="",
    result_status='Rework'
  ).select_related('build')

  if shift in ['1', '2']:
    queryset = queryset.filter(production_shift=int(shift))

  data=[]
  days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

  for row in queryset:
    production_date = row.entered_date - timedelta(hours=7)
    data.append({
      "Orden": row.build.build if row.build.build else "-",
      "Fecha de Registro": row.entered_date.strftime("%Y-%m-%d"),
      "Hora de Registro": row.entered_date.strftime("%H:%M"),
      "Dia de Produccion": days[production_date.weekday()],
      "Tipo de Cable": row.build.cable_type if row.build else "-",
      "Empleado": row.employee_number if row.employee_number else "-" ,
      "Estacion":row.workplace if row.workplace else "-",
      "Turno": row.production_shift if row.production_shift else "-"
    })
  return data

def get_fibers_report_date(start_date_str, end_date_str, shift=""):
  start_date = pd.to_datetime(start_date_str) + timedelta(hours=7)
  end_date = pd.to_datetime(end_date_str) + timedelta(days=1, hours=7)

  queryset = KgpFinaltestResults.objects.filter(
    entered_date__gte=start_date,
    entered_date__lt=end_date
  ).exclude(
    workplace__isnull=True,
    workplace__exact=""
  ).select_related('build')

  if shift in ['1', '2']:
    queryset= queryset.filter(production_shift=int(shift))

  data =[]
  days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

  for row in queryset:
    passed_fibers = row.passed_fibers or 0
    failed_fibers = row.failed_fibers or 0
    done_fibers = failed_fibers +passed_fibers

    data.append({
      "Orden": row.build.build if row.build.build else "-",
      "Empleado": row.employee_number if row.employee_number else "-",
      "Mesa": row.workplace if row.workplace else "-",
      "Turno": row.production_shift if row.production_shift else "-",
      "Fecha de Registro": row.entered_date.strftime("%Y-%m-%d"),
      "Hora de Registro": row.entered_date.strftime("%H:%M"),
      "Fibras Totales": row.build.fiber_count if row.build.fiber_count else "-",
      "Fibras Probadas": passed_fibers if passed_fibers else "-",
      "Fbras Fallidas": failed_fibers if failed_fibers else "-",
      "Estatus": "Terminado" if done_fibers >= row.build.fiber_count else "No Terminado" 
    })
  return data

REPORT_CONFIG = { 
    'scrap_report': { 
        'query': get_scrap_report_data,
        'filename': 'Reporte de Scrap',
        'sheet_name': 'Scrap',
        'chart_config': { 
            'date_col': 'Fecha del Scrap',
            'hour_col': 'Hora',
            'label': 'Ordenes Scrap',
            'base_color': '#da1d1df1',
            'lighter_color': 'rgba(223, 59, 59, 0.99)',
            'darker_color': 'rgba(253, 13, 13, 0.3)'
         }
    },
    'final_test_report': { 
        'query': get_fibers_report_date,
        'filename': 'Reporte Final Test',
        'sheet_name': 'Final Test',
        'chart_config': { 
            'date_col': 'Fecha de Registro',
            'hour_col': 'Hora',
            'label': 'Fibras',
            'base_color': '#29b457cb',
            'lighter_color': 'rgba(41, 187, 41, 0.8)',
            'darker_color': 'rgba(13, 253, 53, 0.3)'
        }
    },
    'production_report': { 
        'query': get_production_report_date,
        'filename': 'Reporte de Produccion',
        'sheet_name': 'Produccion',
        'chart_config': { 
            'date_col': 'Fecha de Registro',
            'hour_col': 'Hora',
            'label': 'Tethers Producidos',
            'base_color': '#0d6efd',
            'lighter_color': 'rgba(13, 110, 253, 0.8)',
            'darker_color': 'rgba(13, 110, 253, 0.3)'
         }
    },
 }