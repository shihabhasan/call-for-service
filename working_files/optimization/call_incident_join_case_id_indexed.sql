CREATE INDEX IF NOT EXISTS call_case_id ON call (case_id);

EXPLAIN ANALYZE SELECT * FROM call, incident WHERE call.case_id = incident.case_id;
