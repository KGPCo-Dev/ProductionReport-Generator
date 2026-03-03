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

FINAL_TEST_REPORT_QUERY = """
SELECT
  (results.entered_date - INTERVAL '7 hours')::DATE AS "Fecha de Produccion",
  results.build_id AS "Orden",
  results.employee_number AS "Empleado",
  results.workplace AS "Mesa",
  results.production_shift AS "Turno",
  results.entered_date::date AS "Fecha de Registro",
  results.production_hour AS "Hora",
  TO_CHAR(results.entered_date, 'HH24:MI') AS "Tiempo de Registro",
  orders.fiber_count AS "Fibras totales",
  results.passed_fibers AS "Fibras aprobadas",
  CASE
    WHEN results.failed_fibers = '' THEN  '0'
  END AS "Fibras fallidas",
  CASE
    WHEN results.finished IS true THEN 'Terminado'
    ELSE 'No terminado'
  END AS "Estatus"
FROM public.kgp_finaltest_results results
JOIN public.kgp_production_orders orders
  ON results.build_id = orders.build_id
WHERE results.entered_date >= (%s::DATE + INTERVAL '7 hours')
    AND results.entered_date < (%s::DATE + INTERVAL '1 day' + INTERVAL '7 hours')
    {shift_clause}
ORDER BY results.entered_date
"""

ORDER_RESULTS_QUERY = """
SELECT
  results.process_id,
  results.build_id AS "Orden",
  process.process_name AS "Proceso",
  results.process_start_time AS "Inicio del Proceso",
  results.process_finish_time AS "Fin del Proceso",
  results.employee_number AS "Empleado",
  results.workplace AS "Estacion",
  results.entered_date AS "Fecha",
  results.global_tether AS "Numero de Tether",
  results.tap_number AS "Locacion"
FROM public.kpg_production_process_results AS results
INNER JOIN public.kgp_production_process AS process ON results.process_id = process.process_id
INNER JOIN public.kgp_production_orders AS orders ON results.build_id = orders.build_id
WHERE results.build_id = %s
ORDER BY results.entered_date DESC
"""

ORDER_DETAILS_QUERY = """
SELECT
  build_id,
  tethers,
  taps,
  cable_type,
  cable_length,
  order_type,
  installation_type,
  fiber_count,
  planned_fibers,
  spare_fibers
FROM public.kgp_production_orders
WHERE build_id = %s
"""

ORDER_STATUS_QUERY = """
SELECT
    id,
    build_id as "Orden",
    entered_date::DATE AS "Fecha",
    TO_CHAR(entered_date::TIME, 'HH24:MI') AS "Hora",
    employee_number AS "Empleado",
    workplace AS "Estacion",
    production_cell AS "Celda",
    production_shift AS "Turno",
    tethers_completed || ' de ' || tethers_total AS "Tethers",
    build_attempt AS "Intentos",
    result_status AS "Estatus"
FROM public.kgp_test2_results
WHERE build_id = %s
    AND result_status IS NOT NULL
    AND workplace IS NOT NULL
    AND workplace <> ''
ORDER BY entered_date ASC
"""


SCRAP_REPORT_QUERY = """
SELECT
    results.entered_date::DATE AS "Fecha de Registro",
    TO_CHAR(results.entered_date, 'HH24:MI') AS "Hora de Registro",
    CASE EXTRACT(DOW FROM (results.entered_date - INTERVAL '7 hours'))
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END AS "Día",
    (results.entered_date - INTERVAL '7 hours')::DATE AS "Fecha del Scrap",
    results.build_id AS "Orden",
    orders.cable_type AS "Tipo de Cable",
    results.employee_number AS "Empleado",
    results.workplace AS "Estacion",
    results.production_cell AS "Celda",
    results.production_hour AS "Hora",
    results.production_shift AS "Turno"
FROM public.kgp_test2_results results
JOIN public.kgp_production_orders orders ON results.build_id = orders.build_id
WHERE results.entered_date >= (%s::DATE + INTERVAL '7 hours')
    AND results.entered_date < (%s::DATE + INTERVAL '1 day' + INTERVAL '7 hours')
    AND results.result_status = 'Scrap'
    {shift_clause}
ORDER BY results.entered_date
"""

PRODUCTION_REPORT_QUERY = """
SELECT
    (results.entered_date - INTERVAL '7 hours')::DATE AS "Fecha de Produccion",
    results.entered_date::DATE AS "Fecha de Registro",
    TO_CHAR(results.entered_date, 'HH24:MI') AS "Hora de Registro",
    CASE EXTRACT(DOW FROM (results.entered_date - INTERVAL '7 hours'))
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END AS "Dia",
    results.build_id AS "Orden",
    orders.cable_type AS "Tipo de Cable",
    results.production_hour AS "Hora",
    results.employee_number AS "Empleado",
    results.workplace AS "Estacion",
    results.production_cell AS "Celda",
    results.production_shift AS "Turno"
FROM public.kgp_test2_results results
JOIN public.kgp_production_orders orders ON results.build_id = orders.build_id
WHERE results.entered_date >= (%s::DATE + INTERVAL '7 hours')
    AND results.entered_date < (%s::DATE + INTERVAL '1 day' + INTERVAL '7 hours')
    AND results.workplace IS NOT NULL
    AND results.workplace <> ''
    AND results.result_status IS DISTINCT  FROM 'Rework'
    AND results.result_status IS DISTINCT  FROM 'Scrap'
    {shift_clause}
ORDER BY results.entered_date
"""

REPORT_CONFIG = { 
    'scrap_report': { 
        'query': SCRAP_REPORT_QUERY,
        'filename': 'Reporte de Scrap',
        'sheet_name': 'Scrap',
        'chart_config': { 
            'date_col': 'Fecha del Scrap',
            'hour_col': 'Hora',
            'label': 'Ordenes Scrap',
            'base_color': '#da1d1df1',
            'lighter_color': 'rgba(223, 59, 59, 0.99)',
            'darker_color': 'rgba(253, 13, 13, 0.3)'
         }
    },
    'final_test_report': { 
        'query': FINAL_TEST_REPORT_QUERY,
        'filename': 'Reporte Final Test',
        'sheet_name': 'Final Test',
        'chart_config': { 
            'date_col': 'Fecha de Produccion',
            'hour_col': 'Hora',
            'label': 'Fibras',
            'base_color': '#29b457cb',
            'lighter_color': 'rgba(41, 187, 41, 0.8)',
            'darker_color': 'rgba(13, 253, 53, 0.3)'
        }
    },
    'production_report': { 
        'query': PRODUCTION_REPORT_QUERY,
        'filename': 'Reporte de Produccion',
        'sheet_name': 'Produccion',
        'chart_config': { 
            'date_col': 'Fecha de Produccion',
            'hour_col': 'Hora',
            'label': 'Tethers Producidos',
            'base_color': '#0d6efd',
            'lighter_color': 'rgba(13, 110, 253, 0.8)',
            'darker_color': 'rgba(13, 110, 253, 0.3)'
         }
    },
    'order_status_results': { 
        'query': ORDER_STATUS_QUERY,
        'filename': 'Resultados de Orden',
        'sheet_name': 'Order_Results',
        'chart_config': { 
            'date_col': 'Fecha de Registro',
            'label': 'Piezas Diaria'
         }
    },
    'order_process_results': { 
        'query': ORDER_RESULTS_QUERY,
        'filename': 'Resultados de Orden',
        'sheet_name': 'Order_Results',
        'chart_config': { 
            'date_col': 'Fecha de Registro',
            'label': 'Resultados'
         }
    },
    'order_fail_results': { 
        'query': ORDER_FAIL_RESULTS_QUERY,
        'filename': 'Resultados de Orden',
        'sheet_name': 'Order_Results',
        'chart_config': { 
            'date_col': 'Fecha de Registro',
            'label': 'Resultados'
         }
    },
 }