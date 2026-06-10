from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from reports.queries import get_machines_status, get_subassemble_table

@login_required
def live_dashboards_view(request):

    sub_table = get_subassemble_table()
    if sub_table:
        print(f"Tabla de SUB: ${sub_table}")
    else:
        print("No hay resultados")
        
    machines_assignation_results = get_machines_status()
    if request.GET.get('partial') == 'true':
        template_name = 'includes/machines_assignation_table.html'
    else:
        template_name = 'live_dashboards/live_dashboards.html'

    return render(request, template_name, {
        'machines_assignation_results': machines_assignation_results,
        'results': machines_assignation_results
    })

