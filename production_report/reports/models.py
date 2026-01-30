from django.db import models

class ProcessNames(models.TextChoices):
    ACCESS_1 = 'ACCESS_1', 'Access 1'
    ACCESS_2 = 'ACCESS_2', 'Access 2'
    SPLICE = 'SPLICE', 'Splice'
    TEST_1 = 'TEST_1', 'Test 1'
    PRE_MOLDING = 'PRE_MOLDING', 'Pre-Moldeo'
    MOLDING = 'MOLDING', 'Moldeo'
    TEST_2 = 'TEST_2', 'Test 2'
    PACKAGING = 'PACKAGING', 'Empaque'
    HANDLING = 'HANDLING', 'Manejador'
    FINAL_TEST = 'FINAL_TEST', 'Prueba Final'
    SUB_ASSY = 'SUB_ASSY', 'Sub-Ensamble'
    CUT ='CUT', 'Corte'



class KgpProductionOrders(models.Model):
    id = models.BigAutoField(primary_key=True)
    entered_date = models.DateTimeField()
    build_id = models.TextField(unique=True, blank=True, null=True)
    fiber_count = models.BigIntegerField(blank=True, null=True)
    planned_fibers = models.BigIntegerField(blank=True, null=True)
    spare_fibers = models.BigIntegerField(blank=True, null=True)
    tethers = models.BigIntegerField(blank=True, null=True)
    taps = models.BigIntegerField(blank=True, null=True)
    cable_type = models.TextField(blank=True, null=True)
    cable_length = models.BigIntegerField(blank=True, null=True)
    order_type = models.TextField(blank=True, null=True)
    installation_type = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_production_orders'
        db_table_comment = 'Any new orders added to the database'

class KgpProductionProcess(models.Model):
    process_id = models.AutoField(primary_key=True)
    process_name = models.TextField(unique=True)
    estimated_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'kgp_production_process'

class KgpEmployees(models.Model):
    employee_id = models.BigAutoField(primary_key=True)
    employee_number = models.BigIntegerField(unique=True)
    employee_name = models.TextField(blank=True, null=True)
    shift = models.IntegerField()
    supervisor = models.TextField(blank=True, null=True)
    is_auditor = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_employees'
        
class QualityAuditors(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee_number = models.OneToOneField(KgpEmployees, models.DO_NOTHING, db_column='employee_number')
    employee_name = models.CharField(blank=True, null=True)
    shift = models.BigIntegerField(blank=True, null=True)
    supervisor = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quality_auditors'


class KgpScrapCodes(models.Model):
    scrap_id = models.BigAutoField(primary_key=True)
    process = models.ForeignKey(KgpProductionProcess, models.DO_NOTHING)
    scrap_description = models.TextField(blank=True, null=True)
    scrap_code = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_scrap_codes'

class KgpProcessFailCodes(models.Model):
    fail_id = models.AutoField(primary_key=True)
    process = models.ForeignKey('KgpProductionProcess', models.DO_NOTHING)
    fail_description = models.TextField()

    class Meta:
        managed = False
        db_table = 'kgp_process_fail_codes'


class KgpReworkCodes(models.Model):
    rework_id = models.BigAutoField(primary_key=True)
    process = models.ForeignKey(KgpProductionProcess, models.DO_NOTHING)
    rework_description = models.TextField(blank=True, null=True)
    rework_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_rework_codes'


class KgpTest2Results(models.Model):
    id = models.BigAutoField(primary_key=True)
    entered_date = models.DateTimeField(blank=True, null=True)
    build = models.ForeignKey(KgpProductionOrders, models.DO_NOTHING, to_field='build_id', blank=True, null=True)
    employee_number = models.BigIntegerField(blank=True, null=True)
    workplace = models.TextField(blank=True, null=True)
    tethers_completed = models.BigIntegerField(blank=True, null=True)
    build_attempt = models.BigIntegerField(blank=True, null=True)
    scrap = models.BooleanField(blank=True, null=True)
    updated_date = models.TextField(blank=True, null=True)
    production_cell = models.IntegerField(blank=True, null=True)
    production_hour = models.IntegerField(blank=True, null=True)
    production_shift = models.IntegerField(blank=True, null=True)
    tethers_total = models.BigIntegerField(blank=True, null=True)
    result_status = models.TextField(blank=True, null=True)
    scrap_auditor = models.ForeignKey('QualityAuditors', models.DO_NOTHING, db_column='scrap_auditor', to_field='employee_number', blank=True, null=True)
    scrap_0 = models.ForeignKey(KgpScrapCodes, models.DO_NOTHING, db_column='scrap_id', blank=True, null=True)  # Field renamed because of name conflict.
    fail_quantity = models.IntegerField(blank=True, null=True)
    fail = models.ForeignKey(KgpProcessFailCodes, models.DO_NOTHING, blank=True, null=True)
    rework_auditor = models.ForeignKey('QualityAuditors', models.DO_NOTHING, db_column='rework_auditor', to_field='employee_number', related_name='kgptest2results_rework_auditor_set', blank=True, null=True)
    rework = models.ForeignKey(KgpReworkCodes, models.DO_NOTHING, blank=True, null=True)
    hold_time_total = models.IntegerField(blank=True, null=True)
    active_time_total = models.IntegerField(blank=True, null=True)
    time_total = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_test2_results'

class KpgProcessFails(models.Model):
    id = models.BigAutoField(primary_key=True)
    build = models.ForeignKey(KgpProductionOrders, models.DO_NOTHING, to_field='build_id', blank=True, null=True)
    global_tether = models.IntegerField(blank=True, null=True)
    entered_date = models.DateTimeField()
    employee_number = models.BigIntegerField(blank=True, null=True)
    workplace = models.TextField(blank=True, null=True)
    process = models.ForeignKey(KgpProductionProcess, models.DO_NOTHING)
    fail = models.ForeignKey(KgpProcessFailCodes, models.DO_NOTHING)
    fail_amount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'kpg_process_fails'

class KgpFinaltestResults(models.Model):
    entered_date = models.DateTimeField()
    build = models.ForeignKey('KgpProductionOrders', models.DO_NOTHING, to_field='build_id')
    employee_number = models.BigIntegerField(blank=True, null=True)
    workplace = models.TextField(blank=True, null=True)
    passed_fibers = models.BigIntegerField(blank=True, null=True)
    failed_fibers = models.TextField(blank=True, null=True)
    finished = models.BooleanField(blank=True, null=True)
    scrap = models.BooleanField(blank=True, null=True)
    updated_date = models.TextField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    production_hour = models.SmallIntegerField(blank=True, null=True)
    production_shift = models.SmallIntegerField(blank=True, null=True)
    scrap_auditor = models.ForeignKey('QualityAuditors', models.DO_NOTHING, db_column='scrap_auditor', to_field='employee_number', blank=True, null=True)
    scrap_0 = models.ForeignKey('KgpScrapCodes', models.DO_NOTHING, db_column='scrap_id', blank=True, null=True)  # Field renamed because of name conflict.
    fail = models.ForeignKey('KgpProcessFailCodes', models.DO_NOTHING, blank=True, null=True)
    hold_time_total = models.IntegerField(blank=True, null=True)
    active_time_total = models.IntegerField(blank=True, null=True)
    time_total = models.IntegerField(blank=True, null=True)
    rework_auditor = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_finaltest_results'