from reports.models import KgpCuttingResults, KgpCuttingMachines, KgpPlanningOrders
from django.db.models import (
  Subquery, OuterRef, Case, Value, IntegerField, When, TextField, F
  )
from core.utils.db_utils import date_report_utc_formatting, AtTimeZone

#---- This file is intended to manage kgp_cutting_results queries ----#

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

def get_cutting_report_date(start_date_str, end_date_str, shift=""):

  #---- This funciton gets cutting results ----#
  start_datetime, end_datetime = date_report_utc_formatting(start_date_str, end_date_str)
  print(start_datetime)
  print(end_datetime)
  data = []
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