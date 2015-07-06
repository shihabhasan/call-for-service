/* For each beat, the proportion of calls that end with no report
being filed. */

DROP VIEW IF EXISTS tableau_no_report_proportion;
CREATE VIEW tableau_no_report_proportion AS
SELECT
  c1.beat,
  COUNT(*) / (
      SELECT COUNT(*) FROM call AS c2 WHERE c2.beat = c1.beat
  )::float AS no_report_proportion
FROM call AS c1
WHERE close_code_id = 2 AND c1.beat IS NOT NULL
GROUP BY beat
ORDER BY no_report_proportion DESC;
