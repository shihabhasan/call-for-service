/*
For each hour in 2014, displays the number of officers clocked in,
the number of officers out of service, and the number of officers on a call.

Helper views are used to increase performance (without this, with 1 hour granularity,
   view takes ~1200 secs to create; with this, with 1 hour granularity,
   only a few secs)
   
For some reason, using 5 minute intervals for the time sample causes the query
execution time to explode from 3 secs to ~800secs if the time range is extended
to the end of July.  It's something about the number of records used to create the views.
We can, however, query the whole year fairly quickly (~3 secs) with 10 minute intervals.

In addition, these indices should be present:
create index shift_time_in on shift(time_in);
create index shift_time_out on shift(time_out);
create index oos_start_time on out_of_service(start_time);
create index oos_end_time on out_of_service(end_time);
create index in_call_start_time on in_call(start_time);
create index in_call_end_time on in_call(end_time);
create index call_log_transaction_id ON call_log(transaction_id);
create index call_log_call_id ON call_log(call_id);
*/


DROP VIEW IF EXISTS sergeants CASCADE;
CREATE VIEW sergeants AS
SELECT call_unit_id FROM call_unit WHERE descr IN (
'A100', 'A200', 'A300', 'A400', 'A500',
'B100', 'B200', 'B300', 'B400', 'B500',
'C100', 'C200', 'C300', 'C400', 'C500',
'D100', 'D200', 'D300', 'D400', 'D500');

-- Time sample
DROP MATERIALIZED VIEW IF EXISTS time_sample CASCADE;
CREATE MATERIALIZED VIEW time_sample AS
SELECT * FROM
generate_series('2014-01-01 00:00'::timestamp,
                '2014-12-31 23:59'::timestamp,
                '10 minutes') AS series(time_);

CREATE UNIQUE INDEX time_sample_time
  ON time_sample(time_); 

-- On duty
DROP MATERIALIZED VIEW IF EXISTS on_duty_count CASCADE;
CREATE MATERIALIZED VIEW on_duty_count AS

SELECT
    ts.time_ AS time_,
    CASE
      WHEN d.num IS NULL THEN 0
      ELSE d.num
    END AS num
FROM
    time_sample AS ts
    LEFT JOIN (
      SELECT time_, COUNT(*) AS num FROM (
        -- This gets the number of officers; we need to do an additional
        -- aggregation to get the number of units, since there can be
        -- multiple officers per unit.
        SELECT time_sample.time_ AS time_, COUNT(*)
        FROM time_sample, shift
        WHERE (time_out-time_in) < (interval '1 day')
          AND time_sample.time_ BETWEEN time_in AND time_out
          AND call_unit_id NOT IN (SELECT * FROM sergeants)
        GROUP BY time_sample.time_, shift.call_unit_id
      ) AS a
      GROUP BY time_
    ) AS d ON (ts.time_ = d.time_);

CREATE UNIQUE INDEX on_duty_count_time
  ON on_duty_count(time_);

-- Out of service
DROP MATERIALIZED VIEW IF EXISTS oos_count CASCADE;
CREATE MATERIALIZED VIEW oos_count AS

SELECT
    ts.time_ AS time_,
    CASE
      WHEN d.num IS NULL THEN 0
      ELSE d.num
    END AS num
FROM
    time_sample AS ts
    LEFT JOIN (
      SELECT time_sample.time_ AS time_, COUNT(*) AS num
      FROM time_sample, out_of_service
      WHERE duration < (interval '1 day')
        AND out_of_service.call_unit_id IN (SELECT DISTINCT call_unit_id FROM shift)
        AND time_sample.time_ BETWEEN start_time AND end_time
        AND out_of_service.call_unit_id NOT IN (SELECT * FROM sergeants)
      GROUP BY time_sample.time_
    ) AS d ON (ts.time_ = d.time_);
    
CREATE UNIQUE INDEX oos_count_time
  ON oos_count(time_);
  
-- On call
DROP MATERIALIZED VIEW IF EXISTS in_call_count CASCADE;
CREATE MATERIALIZED VIEW in_call_count AS

SELECT ts.time_,
    call.call_source_id,
    call.nature_id,
    count(*) AS num
FROM in_call,
    call,
    time_sample ts
WHERE (in_call.start_call_unit_id IN ( SELECT DISTINCT shift.call_unit_id
         FROM shift) AND in_call.start_call_unit_id NOT IN (SELECT * FROM sergeants)) AND (in_call.end_call_unit_id IN ( SELECT DISTINCT shift.call_unit_id
         FROM shift) AND in_call.end_call_unit_id NOT IN (SELECT * FROM sergeants)) AND ts.time_ >= in_call.start_time AND ts.time_ <= in_call.end_time AND in_call.call_id = call.call_id
GROUP BY ts.time_, call.call_source_id, call.nature_id;

-- On Directed Patrol

DROP MATERIALIZED VIEW IF EXISTS dp_count CASCADE;
CREATE MATERIALIZED VIEW dp_count AS

WITH dp_ids AS (
  SELECT nature_id
  FROM nature
  WHERE descr IN ('FOOT PATROL', 'DIRECTED PATROL')
)
SELECT 
  ts.time_,
  CASE
    WHEN d.num IS NULL THEN 0
    ELSE d.num
  END AS num
FROM
  time_sample AS ts
  LEFT JOIN (
    SELECT time_, SUM(num) AS num FROM in_call_count
    WHERE in_call_count.nature_id IN (SELECT nature_id FROM dp_ids)
    GROUP BY time_
  ) AS d ON (ts.time_ = d.time_);

CREATE UNIQUE INDEX dp_count_time
  ON dp_count (time_);

-- On Self-initiated Call

DROP MATERIALIZED VIEW IF EXISTS self_init_count CASCADE;
CREATE MATERIALIZED VIEW self_init_count AS

WITH dp_ids AS (
  SELECT nature_id
  FROM nature
  WHERE descr IN ('FOOT PATROL', 'DIRECTED PATROL')
),
self_init_id AS (
  SELECT call_source_id
  FROM call_source
  WHERE descr = 'Self Initiated'
)
SELECT 
  ts.time_,
  CASE
    WHEN d.num IS NULL THEN 0
    ELSE d.num
  END AS num
FROM
  time_sample AS ts
  LEFT JOIN (
    SELECT time_, SUM(num) AS num
    FROM in_call_count
    WHERE in_call_count.call_source_id = (SELECT call_source_id FROM self_init_id)
      AND in_call_count.nature_id NOT IN (SELECT nature_id FROM dp_ids)
    GROUP BY time_
  ) AS d ON (ts.time_ = d.time_);

CREATE UNIQUE INDEX self_init_count_time
  ON self_init_count (time_);

-- On Other-initiated Call

DROP MATERIALIZED VIEW IF EXISTS other_init_count CASCADE;
CREATE MATERIALIZED VIEW other_init_count AS

WITH dp_ids AS (
  SELECT nature_id
  FROM nature
  WHERE descr IN ('FOOT PATROL', 'DIRECTED PATROL')
),
self_init_id AS (
  SELECT call_source_id
  FROM call_source
  WHERE descr = 'Self Initiated'
)
SELECT 
  ts.time_,
  CASE
    WHEN d.num IS NULL THEN 0
    ELSE d.num
  END AS num
FROM
  time_sample AS ts
  LEFT JOIN (
    SELECT time_, SUM(num) AS num
    FROM in_call_count
    WHERE in_call_count.call_source_id <> (SELECT call_source_id FROM self_init_id)
      AND in_call_count.nature_id NOT IN (SELECT nature_id FROM dp_ids)
      GROUP BY time_
  ) AS d ON (ts.time_ = d.time_);

CREATE UNIQUE INDEX other_init_count_time
  ON other_init_count(time_);

/* Main view */                

DROP MATERIALIZED VIEW IF EXISTS officer_allocation;
CREATE MATERIALIZED VIEW officer_allocation AS

SELECT d.time_ AS time_sample,
    d.num AS num_on_duty,
    o.num AS num_oos,
    dp_count.num AS num_on_dp,
    self_init_count.num AS num_self_init,
    other_init_count.num AS num_other_init
FROM on_duty_count d,
    oos_count o,
    dp_count,
    self_init_count,
    other_init_count
WHERE d.time_ = o.time_ AND d.time_ = dp_count.time_ AND
      d.time_ = self_init_count.time_ AND d.time_ = other_init_count.time_;
