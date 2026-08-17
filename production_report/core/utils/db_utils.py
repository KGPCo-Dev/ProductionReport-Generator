import pandas as pd
from datetime import datetime, timedelta, time,timezone as py_tz
from django.db.models import Func, DateTimeField
from django.utils import timezone as django_tz
import zoneinfo

def dict_fetch_all(cursor):
    columns = [col[0] for col in cursor.description] 
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

#---- Clear date on production_report ----#
def clear_date(date_str):
    try:
        return pd.to_datetime(date_str)
    except Exception as e:
        print(f"Fecha Invalida: {e}")
        return None

def date_report_utc_formatting(start_date_str, end_date_str):
    print(f'StartDate en UTC Formatting: {start_date_str}')
    print(f'EndDate en UTC Formatting: {end_date_str}')

    start_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date_obj= datetime.strptime(end_date_str, "%Y-%m-%d").date()

    local_time_start = datetime.combine(start_date_obj, time(7, 0, 0))
    local_time_end = datetime.combine(end_date_obj + timedelta(days=1), time(7, 0, 0))

    cdmx_tz = zoneinfo.ZoneInfo('America/Mexico_City')

    start_local = django_tz.make_aware(local_time_start, timezone=cdmx_tz)
    end_local = django_tz.make_aware(local_time_end, timezone=cdmx_tz)

    start_utc = start_local.astimezone(py_tz.utc)
    end_utc = end_local.astimezone(py_tz.utc)

    return start_utc, end_utc

def date_report_formatting(start_date_str, end_date_str):

#---- This function prepares the date given by user to extract the report
#---- acording to plant-production times
#---- 1 production day is:
#----   from selected_day + 7 hours
#----   until selected_day + (1 day + 7 hours)#

    print(f'Start date recibed: ${start_date_str}')
    print(f'End date recibed: ${end_date_str}')

    start_date_obj = clear_date(start_date_str)
    end_date_obj = clear_date(end_date_str)

    if start_date_obj and end_date_obj is None:
        return []
    
    print(f'Start cleared date: ${start_date_obj}')
    print(f'End cleared date: ${end_date_obj}')

    start_datetime = datetime.combine(
        start_date_obj, datetime.min.time().replace(hour=1)
        )
    
    end_datetime = datetime.combine(
        end_date_obj + timedelta(days=1), datetime.min.time()
        ).replace(hour=1)
    print(f'FUNC: Hora inicio que se manda para reporte: ${start_datetime}')
    print(f'FUNC: Hora final que se manda para reporte: ${end_datetime}')
    print(f'FUNC: Hora en django: ${django_tz.now()}')

    return (start_datetime, end_datetime)

class AtTimeZone(Func):
    """THIS SHOULD NOT BE THE CASE BUT I WANNA SLEEP"""
    function = 'AT TIME ZONE'
    template = "%(expressions)s %(function)s '%(zone)s'"

    def __init__(self, expression, zone, **extra):
        super().__init__(expression, zone=zone, output_field=DateTimeField(), **extra)