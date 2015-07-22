/*
For each hour in 2014, displays the number of officers clocked in,
the number of officers out of service, and the number of officers on a call.

Helper views are used to increase performance (without this, with 1 hour granularity,
   view takes ~1200 secs to creat; with this, with 1 hour granularity,
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
*/

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
    COUNT(*) AS num
FROM
    shift,
    time_sample AS ts
WHERE 
    (time_out - time_in) < interval '1 day'
    AND ts.time_ BETWEEN time_in AND time_out
GROUP BY
    ts.time_;

CREATE UNIQUE INDEX on_duty_count_time
  ON on_duty_count(time_);

-- Out of service
DROP MATERIALIZED VIEW IF EXISTS oos_count CASCADE;
CREATE MATERIALIZED VIEW oos_count AS

SELECT
    ts.time_ AS time_,
    COUNT(*) AS num
FROM
    out_of_service,
    time_sample AS ts
WHERE 
    duration < (interval '1 day')
    AND out_of_service.call_unit_id IN (SELECT DISTINCT call_unit_id FROM shift)
    AND ts.time_ BETWEEN start_time AND end_time
GROUP BY
    ts.time_;
    
CREATE UNIQUE INDEX oos_count_time
  ON oos_count(time_);
  
-- On call
DROP MATERIALIZED VIEW IF EXISTS in_call_count CASCADE;
CREATE MATERIALIZED VIEW in_call_count AS

SELECT
    ts.time_ AS time_,
    COUNT(*) AS num
FROM
    in_call,
    time_sample AS ts
WHERE
    in_call.start_call_unit_id IN (SELECT DISTINCT call_unit_id FROM shift)
    AND in_call.end_call_unit_id IN (SELECT DISTINCT call_unit_id FROM shift)
    AND ts.time_ BETWEEN start_time AND end_time
GROUP BY
    ts.time_;
    
CREATE UNIQUE INDEX in_call_count_time
  ON in_call_count(time_);


/* Main view */                

DROP MATERIALIZED VIEW IF EXISTS officer_allocation;
CREATE MATERIALIZED VIEW officer_allocation AS

SELECT
  d.time_ AS time_sample,
  d.num AS num_on_duty,
  o.num AS num_oos,
  c.num AS num_on_call
FROM
  on_duty_count AS d,
  oos_count AS o,
  in_call_count AS c
WHERE
  d.time_ = o.time_
  AND d.time_ = c.time_;