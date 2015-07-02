/* For each beat, displays the ratio of proactive officer activity
to non-proactive officer activity (i.e., number of calls where call_source =
'Self-Initiated' divided by number of calls where call_source != 'Self-
Initiated'*/

DROP VIEW IF EXISTS tableau_proactive;
CREATE OR REPLACE VIEW tableau_proactive AS

SELECT c.beat, a.proactive / b.nonproactive::float AS proactive_ratio
FROM
  (SELECT DISTINCT beat FROM call) AS c,
  (SELECT beat, COUNT(*) AS proactive FROM call WHERE call_source_id = 8 GROUP BY beat) AS a,
  (SELECT beat, COUNT(*) AS nonproactive FROM call WHERE call_source_id != 8 GROUP BY beat) AS b
WHERE c.beat=a.beat AND c.beat=b.beat
ORDER BY proactive_ratio;
