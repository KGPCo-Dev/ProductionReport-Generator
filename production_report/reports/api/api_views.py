from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db import connection
from ..queries import REPORT_CONFIG
from .serializers import ReportInputSerializer

# DataBase response gets formated #
def dicfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class ProductionDataAPI(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = ReportInputSerializer(data = request.GET)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        start_date = data['start_date']
        end_date = data['end_date']

        config = REPORT_CONFIG['production_report']
        query = config['query'].format(shift_clause="")

        with connection.cursor() as cursor:
            cursor.execute(query, [start_date, end_date])
            results = dicfetchall(cursor)
        
        return Response(results)