from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db import connection
from ..api_queries import REPORT_CONFIG
from .serializers import ReportInputSerializer


def dicfetchall(cursor):

    columns = [col[0] for col in cursor.description]
    return [ 
        dict(zip(columns, row))
        for row in cursor.fetchall()
     ]

class AllDataAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = REPORT_CONFIG
        results = {}

        for table_name in data:
            config = REPORT_CONFIG[table_name]
            query = config['query']

            with connection.cursor() as cursor:
                cursor.execute(query)
                consult = dicfetchall(cursor)
            
            results[table_name] = consult
        return Response(results)