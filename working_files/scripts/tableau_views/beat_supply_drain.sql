DROP VIEW IF EXISTS tableau_beat_supply_drain;

/*
For each beat, shows the number of calls where that beat drained
a unit from another beat and the number of calls where that beat
supplied a unit to another beat.
*/

CREATE VIEW tableau_beat_supply_drain AS
WITH sucking_stats AS
(SELECT
  p.beat AS unavailable_beat,
  d.beat AS dispatched_beat,
  --p.call_unit_id AS unavailable_id,
  --d.call_unit_id AS dispatched_id,
  count(*) AS count
FROM
  call as c,
  call_unit_beat AS p,
  call_unit_beat AS d
WHERE
  c.primary_unit_id = p.call_unit_id
  AND c.first_dispatched_id = d.call_unit_id
  AND c.primary_unit_id != c.first_dispatched_id
  AND p.beat IS NOT NULL
  AND d.beat IS NOT NULL
GROUP BY
  p.beat,
  d.beat
ORDER BY count(*) DESC)
SELECT
  beat,
  (SELECT SUM(count) AS sum FROM sucking_stats WHERE unavailable_beat = b.beat GROUP BY beat) AS drain,
  (SELECT SUM(count) AS sum FROM sucking_stats WHERE dispatched_beat = b.beat GROUP BY beat) AS supply
FROM
  (SELECT distinct beat FROM call) AS b
WHERE
  beat IS NOT NULL;
