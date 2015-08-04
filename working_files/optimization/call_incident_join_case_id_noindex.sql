DROP INDEX IF EXISTS call_case_id;

EXPLAIN ANALYZE SELECT * FROM call, incident WHERE call.case_id = incident.case_id;
