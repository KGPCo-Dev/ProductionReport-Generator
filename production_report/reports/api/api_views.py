from operator import call
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from reports.api_queries import REPORT_CONFIG
from core.utils.db_utils import dict_fetch_all

class AllDataAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = {}
        for table_name, config in REPORT_CONFIG.items():
            query_func = config['query']
            results[table_name] = query_func() if callable(query_func) else query_func
        return Response(results)

class TableAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, table_name):

        config = REPORT_CONFIG.get(table_name)
        if not config:
            return Response({'error': f'Tabla "{table_name}" no existe.'}, status=404)
        
        query_func = config['query']
        results = query_func() if callable(query_func) else query_func
        return Response(results)
