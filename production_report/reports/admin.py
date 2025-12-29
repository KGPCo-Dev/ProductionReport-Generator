from django.contrib import admin
from .models import KgpTest2Results

@admin.register(KgpTest2Results)
class KgpTest2ResultsAdmin(admin.ModelAdmin):
    list_display = ('entered_date', 'build_id', 'employee_number', 'workplace', 'production_shift', 'production_cell',)