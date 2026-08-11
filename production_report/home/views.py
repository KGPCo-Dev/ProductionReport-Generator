from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from datetime import date
from django.contrib.auth.decorators import login_required
from core.utils.db_utils import clear_date
from django.shortcuts import render
from reports.final_test_services import get_finaltest_results
from reports.test2_services import get_test2_results, get_scrap_results

@login_required
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
    local_date = datetime.now().replace(tzinfo=None)
    date_str = local_date.strftime('%Y-%m-%d')
    current_date = clear_date(date_str)

    #---- current_week_start is used to get the other dates, 
    # with timedelta it is seted to Current's week Monday at 7:00am ----#
    current_week_start = (current_date - timedelta(days=current_date.weekday())).replace(hour=7, minute=0, second=0, microsecond=0)
    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = local_date - timedelta(days=7)

    last_week_results = int(fetch_function(last_week_start, last_week_end).count())
    current_week_results = int(fetch_function(current_week_start, local_date).count())


    change = current_week_results - last_week_results
    diff_percentage = (change / last_week_results ) * 100 if last_week_results else 0

    print("Current Date Value with ORM:", current_date)
    print("Current Week Start Value:", current_week_start)
    print("Last Week End:", last_week_end)
    print("Last Week Start Value:", last_week_start)

    return [current_week_results, last_week_results, diff_percentage, topic_str]
