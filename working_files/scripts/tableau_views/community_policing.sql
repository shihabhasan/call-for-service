/* For each beat, displays the number of calls identified as community policing, the number not related to community policing, the ratio of community:unrelated, and the proportion of community policing activities to total calls.
*/

DROP VIEW IF EXISTS tableau_community_policing;
CREATE OR REPLACE VIEW tableau_community_policing AS

SELECT c.beat, a.cp AS community_policing, b.non_cp AS non_community_policing, a.cp/(SELECT COUNT(*) FROM call)::float AS community_policing_proportion, a.cp / b.non_cp::float AS community_policing_ratio
FROM
  (SELECT DISTINCT beat FROM call) AS c,
  (SELECT beat, COUNT(*) AS cp FROM call WHERE nature_id IN (95, 102) GROUP BY beat) AS a,
  (SELECT beat, COUNT(*) AS non_cp FROM call WHERE nature_id NOT IN (95, 102) GROUP BY beat) AS b
WHERE c.beat=a.beat AND c.beat=b.beat
ORDER BY c.beat;
