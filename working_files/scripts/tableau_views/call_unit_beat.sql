/* Maps each call_unit to its assigned beat based on the last 3 digits
of its unit designation.  Only valid for units starting with the letters
A-D. */

DROP VIEW IF EXISTS call_unit_beat;
CREATE VIEW call_unit_beat AS
SELECT
  call_unit_id,
  descr,
  CASE
    WHEN descr ~ '[A-D]\d{3}' THEN SUBSTRING(descr FROM 2 FOR 3)
    ELSE NULL
  END AS beat
FROM call_unit;
