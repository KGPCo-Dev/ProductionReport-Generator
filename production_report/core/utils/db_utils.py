import pandas as pd

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