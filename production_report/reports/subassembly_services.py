from core.utils.db_utils import date_report_formatting
from reports.models import KgpSubassemblyResults, KgpCuttingResults, KgpProductionOrders
from django.db.models import OuterRef, Subquery, Exists, F

#---- This file is intended to manage SubAssembly operation queries ----#

def get_subassemble_table():
    # 1. Subconsulta para Corte: tomamos la orden con mayor prioridad (status_id 3 > 4)
    # DISTINCT ON (build_id) selecciona la primera fila del orden especificado
    relevant_cutting = (
        KgpCuttingResults.objects.filter(
            build_id=OuterRef('build'),
            status_id__in=[3, 4]
        )
        .order_by('build_id', 'status_id', 'stack_id')  # 3 va antes que 4
    )

    # 2. Subconsulta para Subensamble: tomamos el registro más reciente (último id)
    latest_subassembly = (
        KgpSubassemblyResults.objects.filter(
            build_id=OuterRef('build'),
            kit_delivered=False
        )
        .order_by('-id')
    )

    # 3. Subconsulta booleana ultra rápida para verificar si se entregó el kit
    kit_delivered_exists = KgpSubassemblyResults.objects.filter(
        build_id=OuterRef('build'),
        kit_delivered=True
    )

    # 4. Consulta Principal (Limpia y Ejecutada en 1 sola consulta SQL)
    orders_data = (
        KgpProductionOrders.objects.annotate(
            cutting_status=Subquery(relevant_cutting.values('status__status_description_spanish')[:1]),
            cutting_wip_code=Subquery(relevant_cutting.values('cutting_wip_area__cutting_wip_code')[:1]),
            sub_status=Subquery(latest_subassembly.values('status__status_description_spanish')[:1]),
            has_kit_delivered=Exists(kit_delivered_exists)
        )
        .filter(
            cutting_status__isnull=False,  # Tiene registro válido en corte
            has_kit_delivered=False        # El kit NO ha sido entregado
        )
        .values(
            'build', 
            'cable_type', 
            'tethers', 
            'cutting_status', 
            'sub_status', 
            'cutting_wip_code'
        )
        .annotate(order=F('build'))
    )

    return list(orders_data)

def get_subassemble_report_date(start_date_str, end_date_str, shift=""):

    start_datetime, end_datetime = date_report_formatting(start_date_str, end_date_str)

    queryset = KgpSubassemblyResults.objects.filter(
        entered_date__gte=start_datetime,
        entered_date__lt=end_datetime,
    )
    return None