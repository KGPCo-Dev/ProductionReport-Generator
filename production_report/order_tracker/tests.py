import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'production_report.settings')
django.setup()

from django.test import TestCase
from django.db import connection
from reports.queries import ORDER_RESULTS_QUERY, ORDER_FAIL_RESULTS_QUERY,ORDER_DETAILS_QUERY

# Create your tests here.
def dictfetchall(cursor):

    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]



order_results_query =  ORDER_RESULTS_QUERY
order_fails_results_query = ORDER_FAIL_RESULTS_QUERY
build_id = "CCS1487777"

production_orders_query = ORDER_DETAILS_QUERY
with connection.cursor() as order_details_cursor:
# Order Details Query #
    order_details_cursor.execute(production_orders_query, [build_id])
    order_details = dictfetchall(order_details_cursor)

with connection.cursor() as order_fails_cursor: 
    order_fails_cursor.execute(order_fails_results_query, [build_id])
    order_fails_results = dictfetchall(order_fails_cursor)

    if order_fails_results:
        order_fails_results_headers = [col[0] for col in order_fails_cursor.description]

with connection.cursor() as order_results_cursor:
    order_results_cursor.execute(order_results_query, [build_id])
    order_results = dictfetchall(order_results_cursor)

    if order_results:
        order_results_headers = [col[0] for col in order_results_cursor.description]
    else:
        order_results_headers = "No value"

for row in order_results:
    row['fails'] = [ 
        { 
            'Descripcion': fail['fail_description'],
            'Intentos': fail['fail_amount']
        }
         for fail in order_fails_results
        if fail['process_id'] == row['process_id']
        and fail['global_tether'] == row['Numero de Tether']
     ]



print("ORDE results VALUE BASE", order_results)


def order_current_state(order_details, process_results):
    progress_context = {}
    try:
        # Validamos que existan tethers
        total_tethers = int(order_details[0].get('tethers', 0))
        
        # SET de tethers completados (usamos set para búsqueda O(1))
        completed_tethers = {
            row['Numero de Tether'] 
            for row in process_results[0] 
            if str(row.get('Proceso', '')).upper() in ['TEST_2', 'TEST 2']
        }
        # Generamos la lista de objetos para el template
        progress_context['tethers'] = [
            {'id': i, 'completed': i in completed_tethers}
            for i in range(1, total_tethers + 1)
        ]
        # Ultimo proceso registrado (el primero de la lista ordenada)
        progress_context['latest_process'] = process_results[0][0].get('Proceso', 'Inicio')
        
        # Calculamos porcentaje
        progress_context['percent'] = (len(completed_tethers) / total_tethers * 100) if total_tethers > 0 else 0
        return progress_context
    except (ValueError, IndexError, TypeError) as e:
        print(f"Error en order_current_state: {e}")
        return None