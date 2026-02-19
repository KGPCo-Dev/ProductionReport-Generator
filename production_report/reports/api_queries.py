ORDER_FAIL_RESULTS_QUERY = """
SELECT
  results.build_id,
  results.global_tether,
  results.process_id,
  fails.fail_description,
  results.fail_amount
FROM public.kpg_process_fails results
JOIN public.kgp_process_fail_codes fails
  ON results.fail_id = fails.fail_id
WHERE results.build_id = %s
ORDER by results.fail_amount DESC
"""

REPORT_CONFIG = { 
    'scrap_report': { 
        'query': SCRAP_REPORT_QUERY
    },
 }