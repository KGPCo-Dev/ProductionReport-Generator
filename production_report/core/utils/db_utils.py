import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone

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
    print(f'FUNC: Hora en django: ${timezone.now()}')

    return (start_datetime, end_datetime)