from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Max, Q
from django.utils import timezone
from datetime import timezone as py_tz
import zoneinfo
from reports.queries import get_order_details
from reports.cutting_services import get_single_order_cutting_results, get_cutting_machines, count_registered_orders, get_order_planning_details
from reports.test2_services import get_single_order_last_test2_status
from reports.models import KgpCuttingResults, KgpCuttingMachines, KgpOrdersStatus
import json

def is_cutting_lead(user):
    return user.is_authenticated and (user.groups.filter(name="Cutting-Lead").exists() or user.is_superuser)

@login_required
@user_passes_test(is_cutting_lead)
def cutting_machine_assignation_view(request):

    cutting_machines = []
    cutting_machines_results = get_cutting_machines()

    for machine in cutting_machines_results:
        cutting_machines.append({
            'machine_spanish_name': machine.machine_spanish_name,
            'machine_code': machine.machine_code,
            'assigned_orders_count': count_registered_orders(machine),
        })

    return render(request, 'cutting_machine_assignation/cutting_machine_assignation.html', {
        'cutting_machines': cutting_machines,
    })

@login_required
def get_requested_order(request):

    if not is_cutting_lead(request.user):
        return JsonResponse({
            'success':False, 'error':'No tienes permisos para realizar esta accion.'
        }, status=403)
    
    build_id = request.GET.get('build_id', '').strip()

    if not build_id:
        return JsonResponse({
            'success': False, 'error': 'Por favor, introduce un número de orden.'
        }, status=400) 

    existing_assignation = get_single_order_cutting_results(build_id).exists()

    # 1. Validar si la orden ya está en una cola de corte o en proceso de corte.
    if existing_assignation:
        return JsonResponse({
            'success': False, 'error': 'Esta Orden ya se encuentra asignada a una maquina'
        }, status=400)
    
    # 2. Validar el estatus más reciente en el piso de producción (Test 2).
    last_prod_status = get_single_order_last_test2_status(build_id)
    if last_prod_status and last_prod_status.result_status != 'Scrap':
        return JsonResponse({
            'success': False,
            'error': f'La orden ya está en producción o terminada. Solo órdenes en "Scrap" pueden re-asignarse.'
        }, status=400)


    planning_details = get_order_planning_details(build_id)
    priority_id = planning_details.priority if planning_details else 0

    if priority_id and hasattr(priority_id, 'priority_id'):
        priority_id = priority_id.priority_id

    selected_order = get_order_details(build_id)

    if selected_order is not None and selected_order.build is not None:
        data = {
            'success': True,
            'build_id': selected_order.build,
            'tethers': selected_order.tethers or 0,
            'cable_length': selected_order.cable_length or 0,
            'cable_type': selected_order.cable_type or 'N/A',
            'priority': priority_id or 0
        } 
        return JsonResponse(data, status=200)
    
    return JsonResponse({
        'success': False,
        'error': f'La orden { build_id } no fue encontrada'
    }, status=404)

@login_required
def save_machine_assignation(request):
    # No es necesario definir la fecha aquí, la obtendremos dentro del bucle para mayor precisión.

    if not is_cutting_lead(request.user):
        return JsonResponse({
            'success':False, 'error':'No tienes permisos para realizar esta accion.'
        }, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            machine = data.get('machine')
            orders = data.get('orders', [])

            machine_instance = KgpCuttingMachines.objects.filter(machine_spanish_name=machine).first()
            if not machine_instance:
                return JsonResponse({'success': False, 'error': 'Máquina no encontrada.'}, status=404)

            with transaction.atomic():

                build_ids = [o.get('build_id') for o in orders if o.get('build_id')]
                duplicates = KgpCuttingResults.objects.filter(build_id__in=build_ids, status_id__in=[8, 4])
                if duplicates.exists():
                    dup_builds = ", ".join([d.build_id for d in duplicates])
                    return JsonResponse({
                        'success': False,
                        'error': f'Las siguientes órdenes ya están en cola o en proceso: {dup_builds}'
                    }, status=400)

                max_stack = KgpCuttingResults.objects.filter(
                    machine=machine_instance,
                    status_id=8
                ).aggregate(Max('stack_id'))['stack_id__max'] or 0

                queue_status = KgpOrdersStatus.objects.filter(status=8).first()
                if not queue_status:
                    queue_status = KgpOrdersStatus.objects.get_or_create(
                        status=8,
                        defaults={'status_code': 'QUEUE', 'status_description': 'Waiting for be cutted'}
                    )[0]

                results_to_create = []

                for i, order_data in enumerate(orders):
                    results_to_create.append(
                        KgpCuttingResults(
                            build_id=order_data.get('build_id'),
                            entered_date = timezone.now(),
                            machine=machine_instance,
                            master_reel=order_data.get('master_reel'),
                            status=queue_status,
                            stack_id=max_stack + i + 1,
                            has_master_reel=False
                        )
                    )

                KgpCuttingResults.objects.bulk_create(results_to_create)

            return JsonResponse({'success': True, 'message': 'Asignación recibida correctamente.'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)