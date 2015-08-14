ALTER TABLE call DROP COLUMN IF EXISTS incident_id CASCADE;

ALTER TABLE call ADD COLUMN incident_id bigint;

UPDATE call SET incident_id = (SELECT incident_id FROM incident WHERE incident.case_id = call.case_id);

ALTER TABLE call ADD CONSTRAINT incident_call_fk FOREIGN KEY (incident_id) REFERENCES incident(incident_id);

CREATE INDEX call_incident_id_ndx ON call (incident_id);
