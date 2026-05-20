from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from reports.queries import get_cutting_machines, get_order_details

@login_required
def cutting_machine_assignation_view(request):
    cutting_machines = []

    cutting_machines_results = get_cutting_machines()

    for machine in cutting_machines_results:
        print(machine.machine_code)

    return render(request, 'cutting_machine_assignation/cutting_machine_assignation.html', {
        'cutting_machines': cutting_machines,
    })

@login_required
def get_requested_order(request):
    build_id = request.GET.get('search')

    selected_order = get_order_details(build_id)

    if selected_order is not None and selected_order.build is not None:
        data = {
            'success': True,
            'build_id': selected_order.build,
            'tethers': getattr(selected_order.tethers, 'tethers', 0),
            'cable_type': getattr(selected_order.cable_type, 'cable_type', 'N/A' )
        }
        return JsonResponse(request, 'api/search-order/', data, status=200)
    
    return JsonResponse({
        'success': False,
        'error': f'La orden { build_id } no fue encontrada'
    }, status=404)