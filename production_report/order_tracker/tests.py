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
from reports.queries import ORDER_RESULTS_QUERY, ORDER_FAIL_RESULTS_QUERY

# Create your tests here.
def dictfetchall(cursor):

    print("Cursor value on dictfetchall: ", cursor)
    print("Cursor Description value on dictfetchall: ", cursor.description)

    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]



order_results_query =  ORDER_RESULTS_QUERY
order_fails_results_query = ORDER_FAIL_RESULTS_QUERY
build_id = "CCS1487777"

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
print("order_results value: ", order_results[2], order_results[3])
print("order_results_headers value: ", order_results_headers)

print("order_fail_results value: ", order_fails_results[2], order_fails_results[3])