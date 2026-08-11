from hashlib import new
from distutils.command.build import build
import json
from posixpath import split
from django.shortcuts import render
from datetime import datetime
from django.contrib.auth.decorators import login_required
from reports.models import ProcessNames
from reports.queries import get_order_details, get_fails_results, get_process_results
from reports.test2_services import get_single_order_test2_results
from reports.cutting_services import get_order_planning_details
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from reports.models import KgpPlanningOrders

@login_required
def order_tracker_view(request):

    build_id = request.GET.get('search')
    order_details = None
    test2_results = None
    process_results = None
    order_progress = None

    if request.method == 'GET':
        build_id = request.GET.get('search')
        if build_id:
            build_id = build_id.strip().upper()

            try:
                order_details = get_order_details(build_id)
                planning_details = clear_planning_results(build_id)
                process_results = get_results(build_id)
                test2_results = get_single_order_test2_results(build_id)

                if order_details and process_results:
                    order_progress = get_tethers_status(order_details, process_results)

            except Exception as error_fatal:
                print(f"Critical Error on DB: {error_fatal}")
                order_details = None

    return render(request,'order_tracker/order_tracker_preview.html', { 
        'build_id': build_id,
        'process_results': process_results,
        'test2_results': test2_results,
        'order_details': order_details,
        'planning_details':planning_details,
        'order_progress': order_progress
     })


def get_results(build_id):

    process_results = get_process_results(build_id)
    fails_results = get_fails_results(build_id)

    for row in process_results:
        row.fails = [
            f for f in fails_results
            if f.process == row.process
            and f.global_tether == row.global_tether
        ]

    return process_results


def get_tethers_status(order_details, process_results):

    get_tethers_status = []

    try:
        total_tethers = order_details.tethers if order_details else 0
    except (ValueError, IndexError, TypeError):
        total_tethers = 0

    results = process_results if process_results and process_results else []

    for i in range(1, total_tethers + 1):
        tethers_data = {
            'number': i,
            'percentage': 0,
            'current_process': 'Sin registrar',
            'workplace': '-',
            'location': 'Sin Montar',
            'is_complete': False
        }

        tethers_scans = [r for r in results if r.global_tether == i]

        if tethers_scans:
            lastest = max(tethers_scans, key=lambda x: x.entered_date)
            last_process_id = lastest.process_id if lastest.process_id else 0

            print("Last Process Value:", last_process_id)

            percentage = (last_process_id / 8) * 100
            if percentage > 100: percentage = 100
            if last_process_id == 9:
                percentage = (1/8) * 100
            tethers_data.update({
                'percentage': int(percentage),
                'current_process': lastest.process.display_name,
                'workplace': lastest.workplace,
                'location': lastest.tap_number,
                'is_complete': last_process_id >= 8 and last_process_id != 9
            })

        get_tethers_status.append(tethers_data)

    return get_tethers_status

def clear_planning_results(build_id):

    try:
        planning_details = get_order_planning_details(build_id)

        planning_details.production_deliver_date = datetime.fromisoformat(
            str(planning_details.production_deliver_date)
        ).date()
    
    except Exception as e:
        print("Planning_details value Error: ", e)
        return []

    return planning_details

@login_required
@require_POST
def update_delivery_date(request):

    if not (request.user.is_superuser or request.user.groups.filter(name='Planning').exists()):
        return JsonResponse({'success': False, 'error': 'Need permission'}, status=403)
    
    try:
        data = json.loads(request.body)
        build_id = data.get('build_id')
        new_date_str = data.get('new_date')

        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()

        planning_order = KgpPlanningOrders.objects.filter(
            build_id=build_id
        ).first()

        planning_order.production_deliver_date = new_date
        planning_order.save()

        return JsonResponse({'success': True, 'message': 'Date updated'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Server Error'}, status=500)