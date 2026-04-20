from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from datetime import date
from django.shortcuts import render
from reports.queries import get_test2_results, get_finaltest_results, get_scrap_results

def home_view(request):

    tethers_str = 'Tethers'
    fibers_str = 'Fibras'
    scrap_str = 'Scrap'

    test2_results = count_production_data(get_test2_results, tethers_str)
    finaltest_results = count_production_data(get_finaltest_results, fibers_str)
    scrap_results =  count_production_data(get_scrap_results, scrap_str)

    return render(request, 'home/home_preview.html', {
        'test2_results': test2_results,
        'finaltest_results': finaltest_results,
        'scrap_results': scrap_results
    })


def count_production_data(fetch_function, topic_str):
    #---- This funciton gets the current week and the last week results in order to compare them ----#
    time_local = ZoneInfo("America/Monterrey")
    current_date = datetime.now(time_local)

    #---- current_week_start is used to get the other dates, 
    # with timedelta it is seted to Current's week Monday at 7:00am ----#
    current_week_start = (current_date - timedelta(days=current_date.weekday())).replace(hour=7, minute=0, second=0, microsecond=0)
    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = current_date - timedelta(days=7)

    start_last_week = last_week_start.replace(tzinfo=None)
    end_last_week = last_week_end.replace(tzinfo=None)
    start_current_week = current_week_start.replace(tzinfo=None)
    end_current_week = current_date.replace(tzinfo=None)

    last_week_results = int(fetch_function(start_last_week, end_last_week).count())
    current_week_results = int(fetch_function(start_current_week, end_current_week).count())


    change = current_week_results - last_week_results
    diff_percentage = (change / last_week_results ) * 100 if last_week_results else 0

    print("Current Date Value with ORM:", current_date)
    print("Current Week Start Value:", current_week_start)
    print("Last Week End:", last_week_end)
    print("Last Week Start Value:", last_week_start)

    return [current_week_results, last_week_results, diff_percentage, topic_str]
