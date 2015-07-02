/*
Returns the average number of calls per day by hour of the day and
call source.
*/

DROP VIEW IF EXISTS tableau_source_by_hour;
CREATE VIEW tableau_source_by_hour AS

SELECT hour_received, call_source.descr AS source, COUNT(*)/365::float AS avg_num_calls
FROM call, call_source
WHERE call.call_source_id = call_source.call_source_id
GROUP BY hour_received, source
ORDER BY hour_received, source;
