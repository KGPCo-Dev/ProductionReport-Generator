from core.utils.db_utils import OrderStatus
from django.db.models import ExpressionWrapper
from reports.models import (
  KgpTest2Results, QualityAuditors, KgpCuttingResults,
  KgpSubassemblyResults, KgpProductionOrders, KgpOrdersStatus
)
from django.db.models import F, Q, Value
from django.db.models.functions import Substr, Cast
from django.db.models import DateField
from datetime import timedelta
#---Manage consults that will be done by PowerBI to generate reports ----#

def get_api_test2_results():
  raw_data = (
    KgpTest2Results.objects
    .exclude(Q(workplace__isnull=True) | Q(workplace=''))
    .annotate(
      line=Substr('workplace', 2, 2),
      date=Cast(
        ExpressionWrapper(
          F('entered_date') - Value(timedelta(hours=7)),
          output_field=DateField()
        ),
        output_field=DateField()
      ),
    )
    .values(
      'build_id',
      'employee_number',
      'production_shift',
      'production_cell',
      'production_hour',
      'line',
      'date',
      'result_status'
    )
  )
  return list(raw_data)

def get_api_quality_auditors():
  raw_data = (
    QualityAuditors.objects
    .annotate(
      auditor_number=F('employee_number')
    )
    .values(
      'employee_name',
      'shift',
      'supervisor'
    )
  )
  return list(raw_data)

def get_api_cutting_results():
  raw_data = (
    KgpCuttingResults.objects
    .all()
    .annotate(
      cutting_machine=F('machine__machine_spanish_name')
    )
    .values()
  )

  results = list(raw_data)

  for row in results:
    row.pop('machine_id', None)

  return results

def get_api_subassembly_results():
  raw_data = (
    KgpSubassemblyResults.objects
    .all()
    .values()
  )
  return list(raw_data)

def get_api_production_orders():
  raw_data = (
    KgpProductionOrders.objects
    .all()
    .values()
  )
  return list(raw_data)

def get_api_orders_status():
  raw_data = (
    KgpOrdersStatus.objects
    .values(
      'status_code',
      'status_description',
      'status_description_spanish',
    )
  )
  return list(raw_data)

REPORT_CONFIG = { 
    'produced_tethers': { 
        'query': get_api_test2_results
    },
    'quality_auditors': { 
      'query': get_api_quality_auditors
    },
    'production_orders': { 
      'query': get_api_production_orders
    },
    'cutting_results': {
      'query': get_api_cutting_results
    },
    'subassembly_results': {
      'query': get_api_subassembly_results
    },
    'orders_status': {
      'query': get_api_orders_status
    },
 }
