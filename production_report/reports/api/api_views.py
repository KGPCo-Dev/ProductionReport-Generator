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

class TableAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, table_name):

        config = REPORT_CONFIG.get(table_name)
        if not config:
            return Response({'error': f'Tabla "{table_name}" no existe.'}, status=404)
        
        query = config['query']
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = dicfetchall(cursor)
        
        return Response(results)
