/*
This view has a row for each instance of officer activity -- being in a call,
being on duty, and/or being out of service.  Note that there could be significant
overlap here.  We'll use this to drive the officer allocation view.
*/

DROP MATERIALIZED VIEW IF EXISTS officer_activity CASCADE;

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
  WHERE
    ic.start_time IS NOT NULL AND
    ic.end_time IS NOT NULL AND
    ic.end_time - ic.start_time < interval '1 day'
  UNION ALL
  SELECT
    oos.call_unit_id AS call_unit_id,
    oos.start_time AS start_time,
    oos.end_time AS end_time,
    'OUT OF SERVICE' AS activity,
    NULL AS call_id
   FROM
     out_of_service oos
   WHERE
     oos.start_time IS NOT NULL AND
     oos.end_time IS NOT NULL AND
     oos.end_time - oos.start_time < interval '1 day'
   UNION ALL
   SELECT
     sh.call_unit_id AS call_unit_id,
     sh.in_time AS start_time,
     sh.out_time AS out_time,
     'ON DUTY' AS activity,
     NULL AS call_id
   FROM
     shift_unit sh
   WHERE
     sh.in_time IS NOT NULL AND
     sh.out_time IS NOT NULL AND
     sh.out_time - sh.in_time < interval '1 day') activity; 
     
/*
This view has a row for each instance of officer activity at each 10 minute interval.  It can be used to aggregate activity up based on discrete time intervals instead of a continuous start_time to end_time.
*/

-- temp view needed here for speed
DROP MATERIALIZED VIEW IF EXISTS time_sample CASCADE;
CREATE MATERIALIZED VIEW time_sample AS
SELECT * FROM
generate_series('2014-01-01 00:00'::timestamp,
                '2014-12-31 23:59'::timestamp,
                '10 minutes') AS series(time_);

CREATE UNIQUE INDEX time_sample_time
  ON time_sample(time_); 

DROP MATERIALIZED VIEW IF EXISTS discrete_officer_activity CASCADE;

CREATE MATERIALIZED VIEW discrete_officer_activity AS
  SELECT
    ROW_NUMBER() OVER (ORDER BY start_time ASC) AS discrete_officer_activity_id,
    ts.time_,
    oa.call_unit_id,
    oa.activity,
    oa.call_id
  FROM
    officer_activity oa,
    time_sample ts
  WHERE
    ts.time_ BETWEEN oa.start_time AND oa.end_time;
    
CREATE INDEX discrete_officer_activity_time
  ON discrete_officer_activity(time_);
  
CREATE INDEX discrete_officer_activity_time_hour
  ON discrete_officer_activity (EXTRACT(HOUR FROM time_));