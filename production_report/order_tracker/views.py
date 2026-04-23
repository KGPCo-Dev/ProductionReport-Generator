from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from reports.models import ProcessNames
from reports.queries import get_order_details, get_fails_results, get_process_results, get_single_order_test2_results
from django.db.models import F

@login_required
def order_tracker_view(request):

    build_id = request.GET.get('search')
    order_details = None
    test2_results = None
    process_results = None
    order_progress = None

    if request.method == 'GET':
        if build_id:

            order_details = get_order_details(build_id)
            process_results = get_results(build_id)
            test2_results = get_single_order_test2_results(build_id)

            if order_details and process_results:
                order_progress = get_tethers_status(order_details, process_results)


    return render(request,'order_tracker/order_tracker_preview.html', { 
        'build_id': build_id,
        'process_results': process_results,
        'test2_results': test2_results,
        'order_details': order_details,
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
