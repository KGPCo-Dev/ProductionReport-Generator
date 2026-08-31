from core.utils.db_utils import date_report_formatting, AtTimeZone, PRODUCTION_DAYS_SPANISH
from reports.models import KgpSubassemblyResults, KgpCuttingResults, KgpProductionOrders, KgpSubassembleKitResults
from django.db.models import OuterRef, Subquery, Exists, F, Q
from datetime import timedelta

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

def get_subassembly_report_date(start_date_str, end_date_str, shift=""):

    #---- Date, Day, Hour
    #---- Shift, Employee, Status
    #----- CUTTING RESULTS DATE FORMATING ----#
    
    start_datetime, end_datetime = date_report_formatting(start_date_str, end_date_str)

    date_filter = (
        Q(entered_date__gte=start_datetime, entered_date__lt=end_datetime) |
        Q(finish_date__gte=start_datetime, finish_date__lt=end_datetime) |
        Q(delivered_date__gte=start_datetime, delivered_date__lt=end_datetime)
    )

    queryset = KgpSubassemblyResults.objects.filter(
        date_filter
    ).order_by('entered_date')

    if shift in ['1', '2']:
        shift_int = int(shift)
        queryset = queryset.filter(
            Q(start_shift=shift_int) |
            Q(finish_shift=shift_int) |
            Q(delivered_shift=shift_int) 
        )

    data = []
    days = PRODUCTION_DAYS_SPANISH

    raw_data = queryset.values(
        'build_id',
        'build_id__tethers', #KgpProductionOrders
        'entered_date',
        'start_shift',
        'status__status_description_spanish', #KgpOrdersStatus
        'employee_number',
        'finish_date',
        'finish_shift',
        'delivered_date',
        'delivered_shift',
        'delivered_employee',
        'delivered_cell'
    )

    for row in raw_data.iterator():
        finish_date = row['finish_date'] if row['finish_date'] else None
        delivered_date = row['delivered_date'] if row['delivered_date'] else None
        entered_date = row['entered_date'] if row['entered_date'] else None

        data.append({
            "Orden": row['build_id'] or "-",
            "Tethers Totales": row['build_id__tethers'] or "-",
            "Fecha de Inicio": entered_date.strftime("%d/%m/%Y") if entered_date else "-",
            "Turno de Inicio": row['start_shift'] or "-",
            "Estatus": row['status__status_description_spanish'] or "-",
            "Empleado": row['employee_number'] or "-",
            "Fecha de Finalización": finish_date.strftime("%d/%m/%Y") if finish_date else "-",
            "Turno de Finalización": row['finish_shift'] or "-",
            "Fecha de Entrega": delivered_date.strftime("%d/%m/%Y") if delivered_date else "-",
            "Turno de Entrega": row['delivered_shift'] or "-",
            "Empleado que Recibe": row['delivered_employee'] or "-",
            "Celda": row['delivered_cell'] or "-",
        })
    return data