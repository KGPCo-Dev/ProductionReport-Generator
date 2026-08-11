from reports.models import KgpFinaltestResults

#---- This file is intended to manage FinalTest operations queries ----#

def get_finaltest_results(start_date, end_date):
  return KgpFinaltestResults.objects.filter(
    entered_date__gte=start_date,
    entered_date__lt=end_date
    ).exclude(
      workplace__isnull=True
    ).exclude(
      workplace__exact=''
    )