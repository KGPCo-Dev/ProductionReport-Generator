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

class AccountEmailaddress(models.Model):
    email = models.CharField(unique=True, max_length=254)
    verified = models.BooleanField()
    primary = models.BooleanField()
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailaddress'
        unique_together = (('user', 'email'), ('user', 'primary'),)


class AccountEmailconfirmation(models.Model):
    created = models.DateTimeField()
    sent = models.DateTimeField(blank=True, null=True)
    key = models.CharField(unique=True, max_length=64)
    email_address = models.ForeignKey(AccountEmailaddress, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailconfirmation'


class AgentDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField()
    sharepoint_id = models.CharField(unique=True, max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'agent_document'


class AgentDocumentchunk(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField()
    embedding = models.TextField()  # This field type is a guess.
    document = models.ForeignKey(AgentDocument, models.DO_NOTHING)
    page_number = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'agent_documentchunk'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class KgpCompletedOrders(models.Model):
    id = models.BigAutoField(primary_key=True)
    build_id = models.TextField()
    tethers_total = models.BigIntegerField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    production_shift = models.IntegerField(blank=True, null=True)
    cable_type = models.TextField(blank=True, null=True)
    result_status = models.TextField(blank=True, null=True)
    started_date = models.DateTimeField(blank=True, null=True)
    workplace = models.TextField(blank=True, null=True)
    line = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_completed_orders'
        db_table_comment = 'This table will get the orders that has been completed in final test'


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


class KgpFinaltestMetricsDaily(models.Model):
    id = models.BigAutoField(primary_key=True)
    workplace = models.TextField()
    fibers_per_hour = models.TextField()
    failed_fibers_count = models.BigIntegerField()
    scrap_count = models.BigIntegerField()
    shift = models.SmallIntegerField()
    updated_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'kgp_finaltest_metrics_daily'
        unique_together = (('workplace', 'shift'),)


class KgpFinaltestResults(models.Model):
    entered_date = models.DateTimeField()
    build_id = models.ForeignKey('KgpProductionOrders', models.DO_NOTHING, to_field='build_id')
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
    fail_id = models.ForeignKey('KgpProcessFailCodes', models.DO_NOTHING, blank=True, null=True)
    hold_time_total = models.IntegerField(blank=True, null=True)
    active_time_total = models.IntegerField(blank=True, null=True)
    time_total = models.IntegerField(blank=True, null=True)
    rework_auditor = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_finaltest_results'


class KgpOrdersStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_code = models.TextField(unique=True, blank=True, null=True)
    status_description = models.TextField(blank=True, null=True)
    internal_descrption = models.TextField(blank=True, null=True, db_comment='This section is to explain what every code is')

    class Meta:
        managed = False
        db_table = 'kgp_orders_status'


class KgpOvertimeReasons(models.Model):
    overtime_id = models.BigAutoField(primary_key=True)
    overtime_desciption = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_overtime_reasons'


class KgpProcessFailCodes(models.Model):
    fail_id = models.AutoField(primary_key=True)
    process_id = models.ForeignKey('KgpProductionProcess', models.DO_NOTHING)
    fail_description = models.TextField()

    class Meta:
        managed = False
        db_table = 'kgp_process_fail_codes'


class KgpProductionOrderSetup(models.Model):
    id = models.BigAutoField(primary_key=True)  # The composite primary key (id, build_id) found, that is not supported. The first column is selected.
    updated_date = models.DateTimeField()
    build_id = models.TextField(unique=True)
    location_setup = models.TextField(blank=True, null=True)
    tethers_registered = models.IntegerField(blank=True, null=True)
    locations_registered = models.IntegerField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    attempt_number = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_production_order_setup'
        unique_together = (('id', 'build_id'),)


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
    process_description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_production_process'


class KgpProductionRework(models.Model):
    id = models.BigAutoField(primary_key=True)
    entered_date = models.DateTimeField()
    build_id = models.TextField(blank=True, null=True)
    workplace = models.SmallIntegerField(blank=True, null=True)
    rework_auditor = models.IntegerField(blank=True, null=True)
    shift = models.SmallIntegerField(blank=True, null=True)
    employee_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_production_rework'


class KgpProductionScrap(models.Model):
    id = models.BigAutoField(primary_key=True)
    entered_date = models.DateTimeField()
    build_id = models.TextField(blank=True, null=True)
    workplace = models.SmallIntegerField(blank=True, null=True)
    process_id = models.SmallIntegerField(blank=True, null=True)
    employee_number = models.IntegerField(blank=True, null=True)
    scrap_auditor = models.IntegerField(blank=True, null=True)
    tap_number = models.SmallIntegerField(blank=True, null=True)
    global_tether = models.SmallIntegerField(blank=True, null=True)
    scrap_id = models.SmallIntegerField(blank=True, null=True)
    shift = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_production_scrap'


class KgpProductionWorkstations(models.Model):
    id = models.BigAutoField(primary_key=True)
    cell = models.SmallIntegerField(blank=True, null=True)
    line = models.SmallIntegerField(blank=True, null=True)
    station = models.SmallIntegerField(blank=True, null=True)
    workplace = models.SmallIntegerField(unique=True, blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    working_build_id = models.TextField(blank=True, null=True)
    working_build_location = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_production_workstations'


class KgpReworkCodes(models.Model):
    rework_id = models.BigAutoField(primary_key=True)
    process_id = models.ForeignKey(KgpProductionProcess, models.DO_NOTHING)
    rework_description = models.TextField(blank=True, null=True)
    rework_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_rework_codes'


class KgpScrapCodes(models.Model):
    scrap_id = models.BigAutoField(primary_key=True)
    process_id = models.ForeignKey(KgpProductionProcess, models.DO_NOTHING)
    scrap_description = models.TextField(blank=True, null=True)
    scrap_code = models.TextField(unique=True, blank=True, null=True)
    scrap_description_spanish = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_scrap_codes'


class KgpSubensambleResults(models.Model):
    id = models.BigAutoField(primary_key=True)
    entered_date = models.DateTimeField()
    build_id = models.TextField(blank=True, null=True)
    tether_description = models.TextField(blank=True, null=True)
    tether_quantity = models.BigIntegerField(blank=True, null=True)
    finished = models.BooleanField(blank=True, null=True)
    employee_number = models.BigIntegerField(blank=True, null=True)
    updated_date = models.TextField(blank=True, null=True)
    tap_number = models.IntegerField(blank=True, null=True)
    local_tether = models.IntegerField(blank=True, null=True)
    global_tether = models.IntegerField(blank=True, null=True)
    overtime_reason = models.ForeignKey(KgpOvertimeReasons, models.DO_NOTHING, db_column='overtime_reason', blank=True, null=True)
    fail_id = models.IntegerField(blank=True, null=True)
    rework = models.BooleanField(blank=True, null=True)
    rework_auditor = models.ForeignKey('QualityAuditors', models.DO_NOTHING, db_column='rework_auditor', to_field='employee_number', blank=True, null=True)
    rework_0 = models.ForeignKey(KgpReworkCodes, models.DO_NOTHING, db_column='rework_id', blank=True, null=True)  # Field renamed because of name conflict.
    scrap = models.BooleanField(blank=True, null=True)
    scrap_auditor = models.ForeignKey('QualityAuditors', models.DO_NOTHING, db_column='scrap_auditor', to_field='employee_number', related_name='kgpsubensambleresults_scrap_auditor_set', blank=True, null=True)
    scrap_0 = models.ForeignKey(KgpScrapCodes, models.DO_NOTHING, db_column='scrap_id', blank=True, null=True)  # Field renamed because of name conflict.
    hold_time_total = models.IntegerField(blank=True, null=True)
    active_time_total = models.IntegerField(blank=True, null=True)
    time_total = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_subensamble_results'
        db_table_comment = 'This table will get the subensamble orders that are in WIP'


class KgpTest2MetricsDaily(models.Model):
    id = models.BigAutoField(primary_key=True)
    cell = models.IntegerField()
    tethers_per_hour = models.TextField()
    scrap_count = models.IntegerField()
    orders_scrapped = models.TextField()
    openned_count = models.IntegerField()
    orders_openned = models.TextField()
    completed_count = models.IntegerField()
    orders_completed = models.TextField()
    shift = models.IntegerField()
    updated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kgp_test2_metrics_daily'
        unique_together = (('cell', 'shift'),)


class KgpTest2Results(models.Model):
    id = models.BigAutoField(primary_key=True)
    entered_date = models.DateTimeField(blank=True, null=True)
    build_id = models.ForeignKey(KgpProductionOrders, models.DO_NOTHING, to_field='build_id', blank=True, null=True)
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
    fail_id = models.ForeignKey(KgpProcessFailCodes, models.DO_NOTHING, blank=True, null=True)
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
    build_id = models.ForeignKey(KgpProductionOrders, models.DO_NOTHING, to_field='build_id', blank=True, null=True)
    global_tether = models.IntegerField(blank=True, null=True)
    entered_date = models.DateTimeField()
    employee_number = models.BigIntegerField(blank=True, null=True)
    workplace = models.TextField(blank=True, null=True)
    process_id = models.ForeignKey(KgpProductionProcess, models.DO_NOTHING)
    fail_id = models.ForeignKey(KgpProcessFailCodes, models.DO_NOTHING)
    fail_amount = models.IntegerField()
    shift = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kpg_process_fails'


class KpgProductionProcessResults(models.Model):
    id = models.BigAutoField(primary_key=True)
    build_id = models.ForeignKey(KgpProductionOrders, models.DO_NOTHING, to_field='build_id', blank=True, null=True)
    entered_date = models.DateTimeField()
    employee_number = models.BigIntegerField(blank=True, null=True)
    workplace = models.TextField(blank=True, null=True)
    tap_number = models.IntegerField(blank=True, null=True)
    local_tether = models.IntegerField(blank=True, null=True)
    global_tether = models.IntegerField(blank=True, null=True)
    hold_time_total = models.IntegerField(blank=True, null=True)
    active_time_total = models.IntegerField(blank=True, null=True)
    time_total = models.IntegerField(blank=True, null=True)
    result_status = models.ForeignKey(KgpOrdersStatus, models.DO_NOTHING, db_column='result_status', to_field='status_code', blank=True, null=True)
    tether_id = models.IntegerField(editable=False, blank=True, null=True)
    process_id = models.ForeignKey(KgpProductionProcess, models.DO_NOTHING, blank=True, null=True)
    process_start_time = models.TextField(blank=True, null=True)
    process_finish_time = models.TextField(blank=True, null=True)
    attempt_number = models.SmallIntegerField(blank=True, null=True)
    shift = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kpg_production_process_results'


class QualityAuditors(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee_number = models.OneToOneField(KgpEmployees, models.DO_NOTHING, db_column='employee_number')
    employee_name = models.CharField(blank=True, null=True)
    shift = models.BigIntegerField(blank=True, null=True)
    supervisor = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quality_auditors'


class SocialaccountSocialaccount(models.Model):
    provider = models.CharField(max_length=200)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    extra_data = models.JSONField()
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)


class SocialaccountSocialapp(models.Model):
    provider = models.CharField(max_length=30)
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=191)
    secret = models.CharField(max_length=191)
    key = models.CharField(max_length=191)
    provider_id = models.CharField(max_length=200)
    settings = models.JSONField()

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp'


class SocialaccountSocialappSites(models.Model):
    id = models.BigAutoField(primary_key=True)
    socialapp = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)
    site = models.ForeignKey(DjangoSite, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp_sites'
        unique_together = (('socialapp', 'site'),)


class SocialaccountSocialtoken(models.Model):
    token = models.TextField()
    token_secret = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    account = models.ForeignKey(SocialaccountSocialaccount, models.DO_NOTHING)
    app = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialtoken'
        unique_together = (('app', 'account'),)


class TetherTypes(models.Model):
    id = models.BigAutoField(primary_key=True)
    tether_id = models.TextField(blank=True, null=True)
    tether_description = models.TextField(blank=True, null=True)
    connector_type = models.TextField(blank=True, null=True)
    order_type = models.TextField(blank=True, null=True)
    installation_type = models.TextField(blank=True, null=True)
    situation_id = models.TextField(blank=True, null=True)
    tether_length = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tether_types'
