/*
For each call, displays the start (dispatched) and end (cleared) times for each unit involved with the call, as well as the shift_unit_id of that unit.

The view is materialized because it takes about 2 seconds to create.  This is inefficient when querying it multiple times.
*/

 -- ensure these indexes exist or else it will be super slow
 --CREATE INDEX call_log_transaction_id ON call_log (transaction_id);
 --CREATE INDEX call_log_call_id ON call_log (call_id);
 --CREATE INDEX call_log_call_unit_id ON call_log(call_unit_id);
DROP MATERIALIZED VIEW IF EXISTS in_call CASCADE;
CREATE MATERIALIZED VIEW in_call AS
 SELECT c.call_id,
    start_.time_recorded AS start_time,
    end_.time_recorded AS end_time,
    start_.shift_unit_id,
    start_.call_unit_id AS start_call_unit_id,
    end_.call_unit_id AS end_call_unit_id
   FROM call c,
    ( SELECT cl1.call_log_id,
            cl1.transaction_id,
            cl1.shift_unit_id,
            cl1.time_recorded,
            cl1.call_id,
            cl1.call_unit_id,
            cl1.close_code_id
           FROM call_log cl1
          WHERE cl1.transaction_id = 115) start_,
    ( SELECT cl2.call_log_id,
            cl2.transaction_id,
            cl2.shift_unit_id,
            cl2.time_recorded,
            cl2.call_id,
            cl2.call_unit_id,
            cl2.close_code_id
           FROM call_log cl2
          WHERE cl2.transaction_id IN (384, 145)) end_
  WHERE start_.call_id = c.call_id
    AND end_.call_id = c.call_id
    AND start_.shift_unit_id = end_.shift_unit_id
    
    -- ensure our start is the closest dispatch to the clear/cancel
    AND start_.time_recorded = (
      SELECT MAX(time_recorded)
      FROM call_log cl_closest_start
      WHERE cl_closest_start.call_id = end_.call_id
        AND cl_closest_start.call_unit_id = end_.call_unit_id
        AND cl_closest_start.transaction_id = 115
        AND cl_closest_start.time_recorded < end_.time_recorded
    /*
      -- this is slow
      SELECT DISTINCT ON (call_id) time_recorded
      FROM call_log cl_closest_start
      WHERE cl_closest_start.call_id = end_.call_id
        AND cl_closest_start.transaction_id = 115
        AND cl_closest_start.time_recorded < end_.time_recorded
      ORDER BY call_id, time_recorded DESC
    */
    )
    
    -- ensure our end is the closest clear/cancel to the dispatch
    AND end_.time_recorded =  (
      SELECT MIN(time_recorded)
      FROM call_log cl_closest_end
      WHERE cl_closest_end.call_id = start_.call_id
        AND cl_closest_end.call_unit_id = start_.call_unit_id
        AND cl_closest_end.transaction_id IN (145, 384)
        AND cl_closest_end.time_recorded > start_.time_recorded
    /*
    -- this is slow
    SELECT DISTINCT ON (call_id) time_recorded
      FROM call_log cl_closest_start
      WHERE cl_closest_start.call_id = end_.call_id
        AND cl_closest_start.transaction_id = 115
        AND cl_closest_start.time_recorded < end_.time_recorded
      ORDER BY call_id, time_recorded
    */
    )
    
    /* I don't think we actually need to check for this; looks like
       dispatches are always followed by a cancel or clear before another
       dispatch
    -- Make sure the next dispatch/clear/cancel record before this one
    -- wasn't a dispatch record
    AND NOT 115 IN (
      SELECT cl_test.transaction_id
      FROM call_log cl_test
      WHERE cl1.transaction_id IN (115, 145, 384)
        AND cl_test.time_recorded < cl1.time_recorded
        AND cl_test.time_recorded = (
          SELECT MAX(cl_test_inner.time_recorded)
          FROM call_log cl_test_inner
          WHERE cl_test_inner.call_id = start_.call_id
            AND cl_test_inner.time_recorded < start_.time_recorded
        )
    )
    */
  ORDER BY c.call_id;