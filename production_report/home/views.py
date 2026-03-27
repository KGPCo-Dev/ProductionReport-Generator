from datetime import datetime, timedelta
from datetime import date
from django.shortcuts import render

from django.db import connection
from reports.queries import PRODUCTION_REPORT_QUERY

def get_production_data():
    #---- This funciton gest the current week and the last week results in order to compare them ----#

    current_date = date.today()
    current_wkst = current_date - timedelta(days=current_date.weekday())

    last_wkst = current_wkst - timedelta(days=7)
    last_wkend = current_date - timedelta(days=7)

    current_wk_params = [current_wkst, current_date]
    last_wk_params = [last_wkst, last_wkend]

    last_wk_results = get_week_production(last_wk_params)
    current_wk_results = get_week_production(current_wk_params)


    change = current_wk_results - last_wk_results
    diff_percentage = (change / last_wk_results ) * 100 if last_wk_results else 0

    results = [current_wk_results, last_wk_results, diff_percentage]

    return results


def get_week_production(params):
    shift_clause = ""

    query = PRODUCTION_REPORT_QUERY.format(shift_clause=shift_clause)

    with connection.cursor() as cursor:
        cursor.execute(query, params)

        return len(cursor.fetchall())



def home_view(request):

    production_results = get_production_data()

    return render(request, 'home/home_preview.html', {
        'production_results': production_results
    })
# Create your views here.
