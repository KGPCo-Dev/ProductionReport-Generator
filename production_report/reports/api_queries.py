TEST2_RESULTS_QUERY = """
SELECT
  build_id,
  employee_number,
  production_shift,
  production_cell,
  SUBSTRING (workplace FROM 2 FOR 2) AS line,
  (entered_date - INTERVAL '7 hours')::DATE AS date
FROM public.kgp_test2_results
WHERE result_status IS DISTINCT FROM 'Rework'
  AND workplace IS NOT NULL
"""
PRODUCTION_RESULTS_QUERY = """
SELECT
  results.entered_date::DATE,
  results.employee_number,
  results.build_id,
  results.workplace,
  SUBSTRING(results.workplace FROM 1 FOR 1) AS cell,
  SUBSTRING (results.workplace FROM 2 FOR 2) AS line,
  results.global_tether,
  results.hold_time_total,
  results.active_time_total,
  results.time_total,
  process.process_name,
  results.process_start_time,
  results.process_finish_time,
  results.shift
FROM public.kpg_production_process_results results
JOIN public.kgp_production_process process ON results.process_id = process.process_id
"""

SCRAP_RESULTS_QUERY = """
SELECT
  results.build_id,
  process.process_name,
  scrap.scrap_code,
  scrap.scrap_description_spanish,
  results.employee_number,
  results.scrap_auditor,
  results.tap_number,
  results.global_tether,
  results.shift,
  results.workplace,
  (results.entered_date - INTERVAL '7 hours')::DATE AS date
FROM public.kgp_production_scrap results
JOIN public.kgp_production_process process ON results.process_id = process.process_id
JOIN public.kgp_scrap_codes scrap ON results.scrap_id = scrap.scrap_id
"""

FAILS_RESULTS_QUERY = """
SELECT
  results.build_id,
  (results.entered_date - INTERVAL '7hours')::DATE AS date,
  results.global_tether,
  SUBSTRING(results.workplace FROM 1 FOR 1) AS cell,
  SUBSTRING(results.workplace FROM 2 FOR 2) AS line,
  results.employee_number,
  process.process_name,
  fails.fail_description,
  results.fail_amount,
  results.shift
FROM public.kpg_process_fails results
JOIN public.kgp_process_fail_codes fails ON results.fail_id = fails.fail_id
JOIN public.kgp_production_process process ON results.process_id = process.process_id
"""
PRODUCTION_PROCESS_QUERY = """
SELECT *
FROM public.kgp_production_process
"""

SCRAP_CODES_QUERY = """
SELECT *
FROM public.kgp_scrap_codes
"""

QUALITY_AUDITORS_QUERY = """
SELECT
  employee_number AS "auditor_number",
  employee_name,
  shift,
  supervisor
FROM public.quality_auditors
"""

PRODUCTION_ORDERS_QUERY = """
SELECT
  build_id,
  fiber_count,
  tethers,
  taps,
  cable_type,
  cable_length,
  order_type,
  installation_type
FROM public.kgp_production_orders
"""

REPORT_CONFIG = { 
    'molded_tethers_results': { 
        'query': TEST2_RESULTS_QUERY
    },
    'yield_system_results': { 
        'query': PRODUCTION_RESULTS_QUERY
    },
    'scrap_results': { 
        'query': SCRAP_RESULTS_QUERY
     },
    'fails_results': { 
        'query': FAILS_RESULTS_QUERY
     },
    'production_process': { 
        'query': PRODUCTION_PROCESS_QUERY
     },
    'scrap_codes': { 
        'query': SCRAP_CODES_QUERY
     },
    'quality_auditors': { 
        'query': QUALITY_AUDITORS_QUERY
     },
    'production_orders': { 
        'query': PRODUCTION_ORDERS_QUERY
     },
 }
