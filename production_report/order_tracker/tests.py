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

process_results = [order_results, order_results_headers]


tethers_list = []

try:
    total_tethers = int(order_details[0].get('tethers', 0))
except (ValueError, IndexError, TypeError):
    total_tethers = 0

results = process_results[0] if process_results and process_results[0] else[0]

for i in range(1, total_tethers + 1):
    tethers_data = { 
        'number': i,
        'percentage': 0,
        'current_process': 'not_assigned',
        'workplace': '-',
        'location': 'Sin montar',
        'is_complete': False
     }

    tethers_scans = [r for r in results if r.get('Numero de Tether') == i]

    if tethers_scans:
        lastest = max(tethers_scans, key=lambda x: x.get('process_id', 0))
        max_pid = lastest.get('process_id', 0)

        percentage = (max_pid / 9) * 100
        if percentage > 100: percentage = 100

        tethers_data.update({ 
            'percentage': int(percentage),
            'current_process': lastest.get('Proceso', 'Desconocido'),
            'workplace': lastest.get('Estacion', '-'),
            'location': lastest.get('Locacion', '-'),
            'is_complete': max_pid >= 9
         })
    tethers_list.append(tethers_data)



print("Tethers_data value", tethers_list)


