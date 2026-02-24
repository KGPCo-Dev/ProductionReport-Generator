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
from reports.api_queries import REPORT_CONFIG_TEST


# Create your tests here.
def dictfetchall(cursor):

    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]

data = REPORT_CONFIG_TEST
empty_dict = {}

for table_name in data:

    config = REPORT_CONFIG_TEST[table_name]
    query = config['query']

    with connection.cursor() as cursor:
        cursor.execute(query)
        results = dictfetchall(cursor)
        
    empty_dict[table_name] = results

print(empty_dict)