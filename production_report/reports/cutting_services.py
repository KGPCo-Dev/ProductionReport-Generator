from reports.models import KgpCuttingResults, KgpCuttingMachines, KgpPlanningOrders
from django.db.models import (
  Subquery, OuterRef, Case, Value, IntegerField, When, TextField, F, Q, Count
  )
from core.utils.db_utils import date_report_utc_formatting, AtTimeZone

#---- This file is intended to manage kgp_cutting_results queries ----#

def get_cutting_machines():
  return KgpCuttingMachines.objects.all().order_by('machine_id')

def count_registered_orders(machine):
  return KgpCuttingResults.objects.filter(machine=machine, status_id__in=[8, 4]).count()


def get_assigned_orders_for_machine():
  #---- For card dropdown-menu
  # This function get the orders per machine ----#
  machines = list(KgpCuttingMachines.objects.all().order_by('machine_id'))
  assigned_orders = KgpCuttingResults.objects.filter(
    status_id__in=[8,4]
  ).select_related(
    'status'
  ).order_by(
    'machine_id', 'stack_id'
  )

  machine_data = {
    machine.machine_id: {
      'machine_info': machine,
      'orders': []
    } for machine in machines
  }

  for order in assigned_orders:
    if order.machine_id in machine_data:
      machine_data[order.machine_id]['orders'].append(order)

  return list(machine_data.values())

def get_order_planning_details(build_id):
  return KgpPlanningOrders.objects.filter(
    build=build_id
  ).only(
    'priority', 
    'production_deliver_date'
  ).select_related('priority').first()

def get_cutting_report_date(start_date_str, end_date_str, shift=""):

  #---- This funciton gets cutting results ----#
  start_datetime, end_datetime = date_report_utc_formatting(start_date_str, end_date_str)

  date_filter = (
    Q(entered_date__gte=start_datetime, entered_date__lt=end_datetime) |
    Q(start_date__gte=start_datetime, start_date__lt=end_datetime) |
    Q(finish_date__gte=start_datetime, finish_date__lt=end_datetime)
  )
  queryset = KgpCuttingResults.objects.filter(
    date_filter
  ).order_by('entered_date')

  if shift in ['1', '2']:
    shift_int = int(shift)
    queryset = queryset.filter(
      Q(assignation_shift=shift_int) |
      Q(start_shift=shift_int) |
      Q(production_shift=shift_int)
    )

  data = []

  raw_data = queryset.values(
    'build_id',
    'entered_date',
    'status__status_description_spanish',       # KgpOrdersStatus
    'machine__machine_spanish_name',             # KgpCuttingMachines
    'master_reel',
    'employee_number',
    'cutting_wip_area__cutting_wip_code',        # KgpCuttingWipAreas
    'production_shift',
    'start_feet',
    'finish_feet',
    'length_gap',
    'start_date',
    'finish_date',
    'start_shift',
    'assignation_shift'
  )

  for row in raw_data.iterator():

    start_date = row['start_date'] if row['start_date'] else None
    end_date = row['finish_date'] if row['finish_date'] else None
    entered_date = row['entered_date'] if row['entered_date'] else None

    data.append({
      "Orden": row['build_id'] or "-",
      "Fecha de Asignación": entered_date.strftime("%d/%m/%Y") if entered_date else "-",
      "Hora de Asignación": entered_date.strftime("%H:%M:%S") if entered_date else "-",
      "Turno de Asignación": row['assignation_shift'] or "-",
      "Inicio de Corte": start_date.strftime("%d/%m/%Y") if start_date else "-",
      "Hora Inicio Corte": start_date.strftime("%H:%M:%S") if start_date else "-",
      "Turno de Inicio": row['start_shift'] or "-",
      "Fecha Fin Corte": end_date.strftime("%d/%m/%Y") if end_date else "-",
      "Hora Fin Corte": end_date.strftime("%H:%M:%S") if end_date else "-",
      "Turno de Corte": row['production_shift'] or "-",
      "Estatus": row['status__status_description_spanish'] or "-",
      "Máquina": row['machine__machine_spanish_name'] or "-",
      "Master Reel": row['master_reel'] or "-",
      "Empleado": row['employee_number'] or "-",
      "Area de WIP": row['cutting_wip_area__cutting_wip_code'] or "-",
      "Pies Iniciales": row['start_feet'] if row['start_feet'] is not None else "-",
      "Pies Finales": row['finish_feet'] if row['finish_feet'] is not None else "-",
      "Desfase": row['length_gap'] or "-",
    })
  return data

def get_single_order_cutting_results(build_id):
  #---- Validates if an order is on 
  #     queue: status_id = 8
  #     wip: status_id = 4 ----#
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