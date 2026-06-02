from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from reports.queries import get_machines_status

@login_required
def live_dashboards_view(request):
    test_value = []
    machines_assignation_results = get_machines_status()

    print(f"Valores de get_machines_satatus: {machines_assignation_results}")

    return render(request, 'live_dashboards/live_dashboards.html', {
        'machines_assignation_results': machines_assignation_results
    })