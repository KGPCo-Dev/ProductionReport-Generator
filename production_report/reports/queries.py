SCRAP_REPORT_QUERY = """
SELECT
    results.entered_date AS "Fecha de Registro",
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
    results.entered_date AS "Fecha de Registro",
    CASE EXTRACT(DOW FROM (results.entered_date - INTERVAL '7 hours'))
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END AS "Dia",
    (results.entered_date - INTERVAL '7 hours')::DATE AS "Fecha de Produccion",
    results.build_id AS "Orden",
    orders.cable_type AS "Tipo de Cable",
    results.employee_number AS "Empleado",
    results.workplace AS "Estacion",
    results.production_cell AS "Celda",
    results.production_shift AS "Turno"
FROM public.kgp_test2_results results
JOIN public.kgp_production_orders orders ON results.build_id = orders.build_id
WHERE results.entered_date >= (%s::DATE + INTERVAL '7 hours')
    AND results.entered_date < (%s::DATE + INTERVAL '1 day' + INTERVAL '7 hours')
    AND results.workplace IS NOT NULL
    AND results.result_status != 'Rework'
    {shift_clause}
ORDER BY results.entered_date;
"""

REPORT_CONFIG = { 
    'scrap_report': { 
        'query': SCRAP_REPORT_QUERY,
        'filename': 'Reporte de Scrap',
        'sheet_name': 'Scrap'
     },
     'production_report': { 
        'query': PRODUCTION_REPORT_QUERY,
        'filename': 'Reporte de Produccion',
        'sheet_name': 'Produccion'
      }
 }