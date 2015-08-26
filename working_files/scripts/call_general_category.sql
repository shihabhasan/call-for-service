CREATE MATERIALIZED VIEW call_general_category AS
WITH gun_ids AS (SELECT distinct call_id FROM note WHERE
(
(upper(body) LIKE '%GUN%' AND upper(body) ~ '\m(SHOT|HAND)?GUNS?\M(?! IS INVOLVED)') OR
(upper(body) LIKE '%SHOTS HAVE BEEN FIRED%') OR
(upper(body) LIKE '%RIFLE%' AND upper(body) ~ 'RIFLE(?!D)S?') OR
(upper(body) LIKE '%GUN%' AND upper(body) ~ 'A GUN IS INVOLVED: .*(\.?22|9\s?MM|\.?45|\.?40)') OR
(upper(body) LIKE '%REVOLVER%') OR
(upper(body) LIKE '%PISTOL%')
)
AND NOT
(
(upper(body) ~ 'NO (SHOT|HAND)?GUNS?') OR
(upper(body) ~ 'TOY (GUN|RIFLE|SHOTGUN|PISTOL|HANDGUN)')
))
SELECT
  call_id,
  CASE
    WHEN call_id IN (SELECT * FROM gun_ids) THEN TRUE
    ELSE FALSE
  END AS gun_related
FROM call;