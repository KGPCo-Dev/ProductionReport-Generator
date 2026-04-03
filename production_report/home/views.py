from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from datetime import date
from django.shortcuts import render
from core.utils.db_utils import dict_fetch_all

from django.db import connection
from reports.queries import KPI_CARD_SCRAP_QUERY, KPI_CARD_FIBERS_QUERY, KPI_CARD_TETHERS_QUERY


def get_production_data(query, topic_str):
    #---- This funciton gets the current week and the last week results in order to compare them ----#

    report_query = query

    current_date = datetime.now(ZoneInfo("America/Monterrey"))
    current_week_start = current_date - timedelta(days=current_date.weekday())

    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = current_date - timedelta(days=7)

    current_week_params = [current_week_start, current_date]
    last_week_params = [last_week_start, last_week_end]

    last_week_results = get_week_production(report_query, last_week_params)
    current_week_results = get_week_production(report_query, current_week_params)


    change = current_week_results - last_week_results
    diff_percentage = (change / last_week_results ) * 100 if last_week_results else 0

    results = [current_week_results, last_week_results, diff_percentage, topic_str]

    print("Current Date Value:", current_date)
    print("Current Week Start Value:", current_week_start)
    print("Last Week End:", last_week_end)
    print("Last Week Start Value:", last_week_start)

    return results


def get_week_production(report_query, params):

    query = report_query

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = dict_fetch_all(cursor)

    print(results)
    return results[0].get('total_amount', 0)



def home_view(request):

    test2_query = KPI_CARD_TETHERS_QUERY
    finaltest_query = KPI_CARD_FIBERS_QUERY
    scrap_query = KPI_CARD_SCRAP_QUERY

    tethers_str = 'Tethers'
    fibers_str = 'Fibras'
    scrap_str = 'Scrap'

    test2_results = get_production_data(test2_query, tethers_str)
    finaltest_results = get_production_data(finaltest_query, fibers_str) 
    scrap_results = get_production_data(scrap_query, scrap_str)   

    return render(request, 'home/home_preview.html', {
        'test2_results': test2_results,
        'finaltest_results': finaltest_results,
        'scrap_results': scrap_results
    })
# Create your views here.
