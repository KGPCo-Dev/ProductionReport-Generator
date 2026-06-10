from datetime import timedelta
from django.db.models import Case, Value, When, IntegerField, FilteredRelation, Q, F, Subquery, OuterRef, TextField
from django.db.models.expressions import RawSQL
from reports.models import (KgpTest2Results, KgpFinaltestResults, KgpProductionOrders, KpgProcessFails, 
                            KpgProductionProcessResults, KgpPlanningOrders, KgpCuttingMachines, 
                            KgpCuttingResults, KgpSubassemblyResults)
from core.utils.db_utils import clear_date
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

def get_single_order_cutting_results(build_id):
  return KgpCuttingResults.objects.filter(
    build = build_id,
    status_id__in=[8,4]
  ).select_related('build')

def get_machines_status():
  active_results = KgpCuttingResults.objects.filter(
    machine_id=OuterRef('machine_id'),
    status_id__in=[4, 8]
  ).annotate(
    status_priority=Case(
      When(status_id=4, then=Value(0)),
      default=Value(1),
      output_field=IntegerField(),
    )
  ).order_by(
    'status_priority',
    'stack_id'
  )


  return list(
    KgpCuttingMachines.objects.annotate(
      build_id=Subquery(active_results.values('build_id')[:1]),
      status_description=Subquery(active_results.values('status__status_description_spanish')[:1]),
      cable_type=Subquery(active_results.values('build__cable_type')[:1]),
      master_reel=Subquery(active_results.values('master_reel')[:1]),
      stack_id=Subquery(active_results.values('stack_id')[:1]),
      cutting_wip_code=Subquery(active_results.values('cutting_wip_area__cutting_wip_code')[:1]),
      has_master_reel=Subquery(active_results.values('has_master_reel')[:1]),
      raw_next_master_reel=Subquery(active_results.values('master_reel')[1:2])
    ).annotate(
      next_master_reel=Case(
        When(raw_next_master_reel=F('master_reel'), then=Value(None)),
        default=F('raw_next_master_reel'),
        output_field=TextField()
      )
    ).values(
      'machine_id',
      'build_id',
      'status_description',
      'cable_type',
      'master_reel',
      'stack_id',
      'cutting_wip_code',
      'has_master_reel',
      'next_master_reel'
    ).order_by('machine_id')
  )

def get_subassemble_table():
  cutting_subquery = KgpCuttingResults.objects.filter(
    build_id= OuterRef('build'),
    status_id__in =[3, 4]
  ).annotate(
    status_priority=Case(
      When(status_id=3, then=Value(0)),
      default=Value(1),
      output_field=IntegerField(),
    )
  ).order_by('status_priority', 'stack_id').values('status__status_description_spanish')[:1]
  
  subassembly_subquery = KgpSubassemblyResults.objects.filter(
    build_id=OuterRef('build')
  ).order_by('-id').values('status__status_description_spanish')[:1]

  orders_data = (
    KgpProductionOrders.objects.annotate(
      cutting_status=Subquery(cutting_subquery),
      sub_status=Subquery(subassembly_subquery),
      order=F('build')
    )
    .filter(cutting_status__isnull=False)
    .values(
      'order',
      'cutting_status',
      'sub_status',
      'cable_type',
      'tethers'
    )
  )
  return list(orders_data)

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

def get_cutting_machines():
  return KgpCuttingMachines.objects.all().order_by('machine_id')

def count_registered_orders(machine):
  return KgpCuttingResults.objects.filter(machine=machine, status_id__in=[8, 4]).count()

def get_order_planning_details(build_id):
  return KgpPlanningOrders.objects.filter(
    build=build_id
  ).only(
    'priority', 
    'production_deliver_date'
  ).select_related('priority').first()

def get_order_details(build_id):
  return KgpProductionOrders.objects.filter(

    build__iexact=build_id
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

  start_date = clear_date(start_date_str)
  end_date = clear_date(end_date_str)

  if start_date is None or end_date is None:
    return []
  
  start_date = start_date + timedelta(hours=7)
  end_date = end_date + timedelta(days=1, hours=7)

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
      "Estacion": row.workplace if row.workplace else "-",
       "Hora": row.production_hour if row.production_hour else "-",
       "Turno": row.production_shift if row.production_shift else "0" 
    })
  return data

def get_production_report_date(start_date_str, end_date_str, shift=""):

  start_date = clear_date(start_date_str)
  end_date = clear_date(end_date_str)

  if start_date is None or end_date is None:
    return []
  
  start_date = start_date + timedelta(hours=7)
  end_date = end_date + timedelta(days=1, hours=7)

  queryset = KgpTest2Results.objects.filter(
    entered_date__gte=start_date,
    entered_date__lt=end_date,
  ).exclude(
    workplace__isnull=True
  ).exclude(
    workplace__exact=""
  ).exclude(
    production_cell__isnull=True
  ).exclude(
    result_status='Rework'
  ).select_related('build').order_by('-entered_date')

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
      "Celda": row.production_cell if row.production_cell else "-",
      "Turno": row.production_shift if row.production_shift else "-"
    })
  return data

def get_fibers_report_date(start_date_str, end_date_str, shift=""):
  start_date = clear_date(start_date_str)
  end_date = clear_date(end_date_str)

  if start_date is None or end_date is None:
    return []
  
  start_date = start_date + timedelta(hours=7)
  end_date = end_date + timedelta(days=1, hours=7)

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

MONITORING_TABLE_CONFIG = {
  'machines_status_table': {
    'query': get_machines_status,
    'partial_template': 'includes/machines_assignation_table.html'
  },
  'subassembly_status_table': {
    'query': get_subassemble_table,
    'partial_template': 'includes/available_subassembly_orders_table.html'
  }
}