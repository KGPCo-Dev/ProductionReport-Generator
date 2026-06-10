from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from reports.queries import MONITORING_TABLE_CONFIG

@login_required
def live_dashboards_view(request):

    table_type = request.GET.get('table_type', 'subassembly_status_table')
    is_partial = request.GET.get('partial') == 'true'

    if request.method =='GET':
        if table_type:
            config = MONITORING_TABLE_CONFIG.get(table_type, MONITORING_TABLE_CONFIG['subassembly_status_table'])
            partial_template_config = MONITORING_TABLE_CONFIG.get(table_type, MONITORING_TABLE_CONFIG['subassembly_status_table'])

            query_fuction = config.get('query')
            partial_template = partial_template_config.get('partial_template') 

            table_results = query_fuction()

    if is_partial:
        return render(request, partial_template, {
            'results': table_results
        })
    
    return render(request, 'live_dashboards/live_dashboards.html', {
        'partial_template': partial_template,
        'results': table_results,
        'table_type': table_type
    })
