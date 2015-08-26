DROP MATERIALIZED VIEW IF EXISTS call_general_category;

CREATE MATERIALIZED VIEW call_general_category AS
WITH gun_ids AS (
  SELECT distinct call_id
  FROM note
  WHERE (
    (upper(body) LIKE '%GUN%' AND upper(body) ~ '\m(SHOT|HAND)?GUNS?\M(?! IS INVOLVED)') OR
    (upper(body) LIKE '%SHOTS HAVE BEEN FIRED%') OR
    (upper(body) LIKE '%RIFLE%' AND upper(body) ~ 'RIFLE(?!D)S?') OR
    (upper(body) LIKE '%GUN%' AND upper(body) ~ 'A GUN IS INVOLVED: .*(\.?22|9\s?MM|\.?45|\.?40)') OR
    (upper(body) LIKE '%REVOLVER%') OR
    (upper(body) LIKE '%PISTOL%')
  )
    AND NOT (
    (upper(body) ~ 'NO (SHOT|HAND)?GUNS?') OR
    (upper(body) ~ 'TOY (GUN|RIFLE|SHOTGUN|PISTOL|HANDGUN)')
  )
),
gang_ids AS (
  SELECT distinct call_id
  FROM note
  WHERE (
    (upper(body) LIKE '%GANG%' AND upper(body) ~ '\mGANG') OR
    (upper(body) LIKE '%CRIP%' AND upper(body) ~ '\mCRIP\M') OR
    (upper(body) LIKE '%BLOODS%') OR
    (upper(body) LIKE '%MS13%')
  )
),
spanish_ids AS (
  SELECT distinct call_id
  FROM note
  WHERE (
    (upper(body) LIKE '%SPANISH%') OR
    (upper(body) LIKE '%SPAINISH%')
  )
)
SELECT
  call_id,
  CASE
    WHEN call_id IN (SELECT * FROM gun_ids) THEN TRUE
    ELSE FALSE
  END AS gun_related,
  CASE
    WHEN call_id IN (SELECT * FROM gang_ids) THEN TRUE
    ELSE FALSE
   END AS gang_related
FROM call;