
from reports.models import KgpTest2Results, KgpFinaltestResults
from datetime import timedelta
from core.utils.db_utils import date_report_formatting, AtTimeZone

#---- This file is intended to manage kgp_test2_results queries ----#

def get_single_order_test2_results(build_id):
  #---- Test2 results displayed in orders_details page ----#
  return KgpTest2Results.objects.filter(
    build=build_id
  ).exclude(
    result_status='Rework'
  ).exclude(
    workplace__isnull=True
  ).exclude(
    workplace__exact=''
  ).select_related('build').order_by('entered_date')

def get_single_order_last_test2_status(build_id):
  #---- Get last result to verify if order can be assigned to a machine ----#
  return KgpTest2Results.objects.filter(
    build=build_id
  ).order_by(
    '-entered_date').first()

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

def get_scrap_results(start_date, end_date):
  return KgpTest2Results.objects.filter(
    result_status='Scrap',
    entered_date__gte=start_date,
    entered_date__lt=end_date
  ).exclude(
    workplace__exact=''
  )

def get_scrap_report_data(start_date_str, end_date_str, shift=""):

  start_datetime, end_datetime = date_report_formatting(start_date_str, end_date_str)

  queryset = KgpTest2Results.objects.filter(
    entered_date__gte=start_datetime,
    entered_date__lt=end_datetime,
    result_status='Scrap'
  ).annotate(
      raw_entered=AtTimeZone('entered_date', 'UTC')
    ).select_related('build')

  if shift in ['1', '2']:
    queryset = queryset.filter(production_shift=int(shift))

  data=[]
  days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

  for row in queryset:
    supabase_date = row.raw_entered
    production_date = supabase_date - timedelta(hours=1)

    data.append({
      "Orden": row.build.build if row.build else "-",
      "Fecha de Registro": supabase_date.strftime("%d/%m/%Y"),
      "Hora de Registro": supabase_date.strftime('%H:%M'),
      "Dia de Scrap": f"{days[production_date.weekday()]} {production_date.strftime('%d/%m')}",
      "Fecha de Incidencia": production_date.strftime("%d/%m/%Y"),
      "production_date_obj": production_date.date(),
      "Tipo de Cable": row.build.cable_type if row.build else "-",
      "Empleado": row.employee_number if row.employee_number else "-",
      "Estacion": row.workplace if row.workplace else "-",
       "Hora": row.production_hour if row.production_hour else "-",
       "Turno": row.production_shift if row.production_shift else "0" 
    })
  return data

def get_production_report_date(start_date_str, end_date_str, shift=""):
    
    start_datetime, end_datetime = date_report_formatting(start_date_str, end_date_str)

    queryset = KgpTest2Results.objects.filter(
        entered_date__gte=start_datetime,
        entered_date__lt=end_datetime,
    ).exclude(
        workplace__isnull=True
    ).exclude(
        workplace__exact=""
    ).exclude(
        production_cell__isnull=True
    ).exclude(
        result_status='Rework'
    ).exclude(
        result_status='Scrap'
    ).annotate(
      raw_entered=AtTimeZone('entered_date', 'UTC')
    ).select_related('build').order_by('-entered_date')

    if shift in ['1', '2']:
        queryset = queryset.filter(production_shift=int(shift))

    data = []
    days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    for row in queryset:

        supabase_date = row.raw_entered
        production_date = supabase_date - timedelta(hours=7)

        data.append({
            "Fecha de Produccion": production_date.strftime('%d/%m/%Y'),
            "Dia de Produccion": f"{days[production_date.weekday()]}",
            "Orden": row.build.build if row.build and row.build.build else "-",
            "Hora de Registro": supabase_date.strftime("%H:%M"),
            "production_date_obj": production_date.date(),
            "Tipo de Cable": row.build.cable_type if row.build else "-",
            "Empleado": row.employee_number if row.employee_number else "-",
            "Estacion": row.workplace if row.workplace else "-",
            "Celda": row.production_cell if row.production_cell else "-",
            "Turno": row.production_shift if row.production_shift else "-",
            "Fecha de Registro": supabase_date.strftime("%d/%m/%Y"),
        })

    return data

def get_fibers_report_date(start_date_str, end_date_str, shift=""):

  start_datetime, end_datetime = date_report_formatting(start_date_str, end_date_str)
  
  queryset = KgpFinaltestResults.objects.filter(
    entered_date__gte=start_datetime,
    entered_date__lt=end_datetime
  ).exclude(
    workplace__isnull=True,
    workplace__exact=""
  ).annotate(
      raw_entered=AtTimeZone('entered_date', 'UTC')
    ).select_related('build')

  if shift in ['1', '2']:
    queryset= queryset.filter(production_shift=int(shift))

  data =[]
  days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

  for row in queryset:
    supabase_date = row.raw_entered
    production_date = supabase_date - timedelta(hours=1)
    passed_fibers = row.passed_fibers or 0
    failed_fibers = row.failed_fibers or 0
    done_fibers = failed_fibers +passed_fibers

    data.append({
      "Orden": row.build.build if row.build.build else "-",
      "Empleado": row.employee_number if row.employee_number else "-",
      "Mesa": row.workplace if row.workplace else "-",
      "Turno": row.production_shift if row.production_shift else "-",
      "Dia de Produccion": f"{days[production_date.weekday()]} {production_date.strftime('%d/%m')}",
      "Fecha de Registro": supabase_date.strftime("%Y-%m-%d"),
      "production_date_obj": production_date.date(),
      "Hora de Registro": supabase_date.strftime("%H:%M"),
      "Fibras Totales": row.build.fiber_count if row.build.fiber_count else "-",
      "Fibras Probadas": passed_fibers if passed_fibers else "-",
      "Fbras Fallidas": failed_fibers if failed_fibers else "-",
      "Estatus": "Terminado" if done_fibers >= row.build.fiber_count else "No Terminado" 
    })
  return data