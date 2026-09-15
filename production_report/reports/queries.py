from datetime import timedelta
from reports.cutting_services import get_machines_status
from core.utils.db_utils import OrderStatus
from reports.subassembly_services import get_subassemble_table
from reports.models import (
  KgpProductionOrders,
  KpgProcessFails,
  KpgProductionProcessResults
  )
from reports.test2_services import (
  get_fibers_report_date,
  get_production_report_date,
  get_scrap_report_data,
  get_single_order_last_test2_status
  )
from reports.cutting_services import (
  get_cutting_report_date,
  get_single_order_lastest_cutting_result
  )
from reports.subassembly_services import (
  get_subassembly_report_date,
  get_single_order_lastest_subassembly_results)

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

def get_tracking_results(build_id):
  #---- This function gets: 
  #   cutting, 
  #   subassy
  #   test2 
  # results for progress view on order-tracker_preview.html ----#

  # Step 1 Order has  been Assigned
  # Step 2 Order has been Cutted
  # Step 3 KIT in WIP
  # Step 4 KIT Produced
  # Step 5 KIt Delivered
  # Step 6 Test 2 Result Registered

  cutting_result = get_single_order_lastest_cutting_result(build_id)

  print("Cutting Results")
  print("Type:", type(cutting_result))
  print("Value:", cutting_result)
  if cutting_result:
    print(vars(cutting_result))
    last_cutting_date = cutting_result.entered_date

  test2_result = get_single_order_last_test2_status(build_id)

  if (
    test2_result
    and test2_result.entered_date
    and last_cutting_date
    and test2_result.entered_date < last_cutting_date
  ):
    test2_result = None

  subassembly_result = get_single_order_lastest_subassembly_results(build_id)

  if (
    subassembly_result
    and subassembly_result.entered_date
    and last_cutting_date
    and subassembly_result.entered_date < last_cutting_date
  ):
    subassembly_result = None

  #---- STEP 1 ----#
  has_cutting = cutting_result is not None
  machine_name = (
    cutting_result.machine.machine_number
    if has_cutting and cutting_result.machine
    else "Sin Asignar"
  )
  step1_complete = has_cutting and cutting_result.status_id in [
    OrderStatus.QUEUE,
    OrderStatus.WIP,
    OrderStatus.DONE
  ]
  tooltip_1 = f"<b>Orden Asignada</b><br>Máquina: {machine_name}"

  #---- STEP 2  ----#
  wip_area_code = (
    cutting_result.cutting_wip_area.cutting_wip_code
    if has_cutting and cutting_result.cutting_wip_area
    else "Sin área de WIP"
  )
  step2_in_progress = has_cutting and cutting_result.status_id == OrderStatus.WIP

  step2_complete = (
    has_cutting and (
      cutting_result.status_id == OrderStatus.DONE or
      subassembly_result is not None or
      test2_result is not None
    )
  )
  tooltip_2 = f"<b>Orden Cortada</b><br>Máquina: {machine_name}<br>Área de WIP: {wip_area_code}"

  #---- STEP 3 ----#
  has_subassy = subassembly_result is not None
  subassy_entered = (
    subassembly_result.entered_date.strftime("%d/%m/%Y %H:%M")
    if has_subassy and subassembly_result.entered_date
    else "Sin registro"
  )
  step3_in_progress = has_subassy and subassembly_result.status_id == OrderStatus.WIP

  step3_complete = (
    has_subassy and (
      subassembly_result.status_id in [OrderStatus.WIP, OrderStatus.DONE, OrderStatus.KIT_DLV] or
      subassembly_result.kit_delivered or
      test2_result is not None
    )
  )
  tooltip_3 = f"<b>KIT en proceso</b><br>Fecha Inicio: {subassy_entered}"

  #---- STEP 4 ----#
  finish_dt = (
    subassembly_result.finish_date.strftime("%d/%m/%Y %H:%M")
    if has_subassy and subassembly_result.finish_shift
    else "N/A"
  )

  finish_shift = (
    subassembly_result.finish_shift
    if has_subassy and subassembly_result.finish_shift
    else "N/A"
  )
  step4_in_progress = has_subassy and subassembly_result.status_id == OrderStatus.WIP and subassembly_result.finish_date is not None

  step4_complete = (
    has_subassy and (
      subassembly_result.status_id in [OrderStatus.DONE, OrderStatus.KIT_DLV] or
      subassembly_result.finish_date is not None or
      subassembly_result.kit_delivered or
      test2_result is not None
    )
  )
  tooltip_4 = f"<b>KIT Armado</b><br>Armado el: {finish_dt}<br>Turno: {finish_shift}"

  #---- STEP 5 ----#
  del_cell = (
    subassembly_result.delivered_cell
    if has_subassy and subassembly_result.delivered_employee
    else "N/A"
  )
  del_emp = (
    subassembly_result.delivered_employee
    if has_subassy and subassembly_result.delivered_employee
    else "N/A"
  )
  step5_in_progress = has_subassy and subassembly_result.status_id == OrderStatus.DONE and not subassembly_result.kit_delivered

  step5_complete = (
    has_subassy and (
      subassembly_result.kit_delivered is True or
      subassembly_result.status_id == OrderStatus.KIT_DLV or
      subassembly_result.delivered_date is not None or
      test2_result is not None
    )
  )
  tooltip_5 = f"<b>KIT Entregado</b><br>Celda: {del_cell}<br>Recibe: {del_emp}"

  #---- STEP 6 ----#
  has_test2 = test2_result is not None
  prod_cell = (
    test2_result.production_cell
    if has_test2 and test2_result.production_cell
    else "N/A"
  )
  step6_is_scrap = has_test2 and (test2_result.result_status == "Scrap" or getattr(test2_result, 'scrap', False) is True)

  tethers_completed = test2_result.tethers_completed if has_test2 and test2_result.tethers_completed is not None else 0
  tethers_total = test2_result.tethers_total if has_test2 and test2_result.tethers_total is not None else 0

  if has_test2 and not step6_is_scrap:
    if tethers_total > 0:
      step6_complete = tethers_completed >= tethers_total
      step6_in_progress = tethers_completed > 0 and tethers_completed < tethers_total
    else:
      step6_complete = test2_result.result_status == "Pass"
      step6_in_progress = not step6_complete
  else:
    step6_complete = False
    step6_in_progress = False

  tooltip_6 = f"<b>Prueba 2</b><br>Celda: {prod_cell}"
  if has_test2 and tethers_total > 0:
    tooltip_6 += f"<br>Avance: {tethers_completed}/{tethers_total}" 

  tracking_steps = [
    {"name": "Orden Asignada", "is_complete": step1_complete, "is_in_progress": False, "is_scrap": False, "tooltip": tooltip_1},
    {"name": "Orden Cortada", "is_complete": step2_complete, "is_in_progress": step2_in_progress, "is_scrap": False, "tooltip": tooltip_2},
    {"name": "KIT en proceso", "is_complete": step3_complete, "is_in_progress": step3_in_progress, "is_scrap": False, "tooltip": tooltip_3},
    {"name": "KIT Armado", "is_complete": step4_complete, "is_in_progress": step4_in_progress, "is_scrap": False, "tooltip": tooltip_4},
    {"name": "KIT Entregado", "is_complete": step5_complete, "is_in_progress": step5_in_progress, "is_scrap": False, "tooltip": tooltip_5},
    {"name": "Prueba 2", "is_complete": step6_complete, "is_in_progress": step6_in_progress, "is_scrap": step6_is_scrap, "tooltip": tooltip_6},
  ]
  return tracking_steps


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
    'subassembly_report': { 
        'query': get_subassembly_report_date,
        'filename': 'Reporte de Sub-Ensamble',
        'sheet_name': 'Produccion',
        'chart_config': { 
            'date_col': 'Dia de Produccion',
            'hour_col': 'Hora',
            'label': 'Kits Producidos',
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