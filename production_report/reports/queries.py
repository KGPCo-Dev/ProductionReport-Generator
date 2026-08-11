from datetime import timedelta
from reports.cutting_services import get_machines_status
from reports.subassembly_services import get_subassemble_table
from reports.test2_services import get_fibers_report_date, get_production_report_date, get_scrap_report_data
from reports.cutting_services import get_cutting_report_date
from reports.models import (KgpProductionOrders, KpgProcessFails, KpgProductionProcessResults)



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


REPORT_CONFIG = { 
    'scrap_report': { 
        'query': get_scrap_report_data,
        'filename': 'Reporte de Scrap',
        'sheet_name': 'Scrap',
        'chart_config': { 
            'date_col': 'Dia de Scrap',
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
            'date_col': 'Dia de Produccion',
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
            'date_col': 'Dia de Produccion',
            'hour_col': 'Hora',
            'label': 'Tethers Producidos',
            'base_color': '#0d6efd',
            'lighter_color': 'rgba(13, 110, 253, 0.8)',
            'darker_color': 'rgba(13, 110, 253, 0.3)'
         }
    },
    'cutting_report': { 
        'query': get_cutting_report_date,
        'filename': 'Reporte de Corte',
        'sheet_name': 'Produccion',
        'chart_config': { 
            'date_col': 'Dia de Produccion',
            'hour_col': 'Hora',
            'label': 'Ordenes Cortadas',
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