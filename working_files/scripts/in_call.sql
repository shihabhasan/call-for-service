/*
For each call, displays the start (dispatched) and end (cleared) times for each unit involved with the call, as well as the shift_unit_id of that unit.

The view is materialized because it takes about 2 seconds to create.  This is inefficient when querying it multiple times.
*/

DROP VIEW IF EXISTS in_call;
CREATE MATERIALIZED VIEW in_call AS

SELECT
  c.call_id AS call_id,
  start_.time_recorded AS start_time,
  end_.time_recorded AS end_time,
  start_.shift_unit_id AS shift_unit_id,
  start_.call_unit_id AS start_call_unit_id,
  end_.call_unit_id AS end_call_unit_id
FROM
  call AS c,
  (SELECT * FROM call_log AS cl1 WHERE cl1.transaction_id = 115) AS start_,
  (SELECT * from call_log AS cl2 WHERE cl2.transaction_id = 145) AS end_
WHERE
  start_.call_id = c.call_id AND
  end_.call_id = c.call_id AND
  start_.shift_unit_id = end_.shift_unit_id
ORDER BY call_id;