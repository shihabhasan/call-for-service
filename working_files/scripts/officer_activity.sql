/*
This view has a row for each instance of officer activity -- being in a call,
being on duty, and/or being out of service.  Note that there could be significant
overlap here.  We'll use this to drive the officer allocation view.
*/

DROP MATERIALIZED VIEW IF EXISTS officer_activity;

CREATE MATERIALIZED VIEW officer_activity AS
  SELECT
    ROW_NUMBER() OVER (ORDER BY start_time ASC) AS officer_activity_id,
    activity.*
  FROM (
  SELECT
    ic.call_unit_id AS call_unit_id,
    ic.start_time AS start_time,
    ic.end_time AS end_time,
    'IN CALL' AS activity,
    ic.call_id AS call_id
  FROM
    in_call ic
  UNION ALL
  SELECT
    oos.call_unit_id AS call_unit_id,
    oos.start_time AS start_time,
    oos.end_time AS end_time,
    'OUT OF SERVICE' AS activity,
    NULL AS call_id
   FROM
     out_of_service oos
   UNION ALL
   SELECT
     sh.call_unit_id AS call_unit_id,
     sh.in_time AS start_time,
     sh.out_time AS out_time,
     'ON DUTY' AS activity,
     NULL AS call_id
   FROM
     shift_unit sh) activity; 