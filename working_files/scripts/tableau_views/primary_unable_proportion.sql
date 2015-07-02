/* For each beat, displays the proportion of calls in that beat
where the first unit dispatched != the primary unit (i.e., the one that
is geographically responsible for that call)*/

DROP VIEW IF EXISTS tableau_primary_unable_proportion;
CREATE VIEW tableau_primary_unable_proportion AS
SELECT c.beat, a.primary_unable/b.total::float as proportion_primary_unable
FROM
  (SELECT DISTINCT beat FROM call) AS c,
  (SELECT beat, COUNT(*) AS primary_unable FROM call WHERE primary_unit_id != first_dispatched_id GROUP BY beat) AS a,
  (SELECT beat, COUNT(*) AS total FROM call GROUP BY beat) AS b
WHERE c.beat = b.beat AND c.beat = a.beat;
