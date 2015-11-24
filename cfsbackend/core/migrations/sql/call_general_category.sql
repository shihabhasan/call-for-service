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
),
mentally_ill_ids AS (
  SELECT distinct call_id
  FROM note
  WHERE
    (upper(body) LIKE '%10-73%' AND
      upper(body) ~ '\m73\M') OR
    (upper(body) LIKE '%73%' AND
      upper(body) ~ '\m73\M' AND
      upper(body) !~ 'AGE: 73' AND
      upper(body) !~ '73(\.| YOA|-YEAR| YEARS)' AND
      upper(body) !~ '[-|.|/]73' AND
      upper(body) !~ '\(73\)'
    ) OR
    (upper(body) LIKE '%BAKER ACT%')
),
officer_citizen_conflict_ids AS (
  SELECT distinct call_id
  FROM note
  -- Ignore EMS/FIRE messages because they won't be reporting conflict between PD and citizens.
  WHERE upper(body) NOT LIKE '[EMD]%' AND upper(body) NOT LIKE '[FIRE]%' AND upper(body) NOT LIKE '[EMS]%' AND
  -- Gnarly regex to attempt to locate comments that indicate officer-citizen conflict
  -- We do this by searching for either a specific phrase indicating a complaint about an officer or both 1) a reference to an officer ("officer phrase") and 2) a phrase associated with some kind of conflict ("conflict phrase")
  upper(body) ~
  $$(?x)# <-- (?x) allows comments
  (
    # First check for sequences that indicate an officer phrase
    (OFFICER|\mOFCR\M|\mPD\M|POLICE|(\m[A-D]\d{3}\M(?![)}])))  # that last gargbage is an attempt to match a unit expression in a way that doesn't catch comments by units (ex. "(A132) <comments>" or "{A143} <comments>")
    # Some other unimportant text; note that we exclude periods and commas here so that the officer and conflict phrases occur near each other in the sentence structure
    [^.,]*?
    # Now check for conflict phrases
    (UPSET|UNHAPPY|\mRUDE\M|RUDELY|\mCOMPLAIN(ING)?\M|DISRESPECT|AGGRESSIVE|UNPROFESSIONAL)
  )
  # We could also have the conflict phrase before the officer phrase
  |
  (
    # Conflict phrases again
    (UPSET|UNHAPPY|\mRUDE\M|RUDELY|\mCOMPLAIN(ING)?\M|DISRESPECT|AGGRESSIVE|UNPROFESSIONAL)
    # Other unimportant text again, again excluding clause-breaking punctuation
    [^,.]*?
    # Officer phrase again
    (OFFICER|\mOFCR\M|\mPD\M|POLICE|(\m[A-D]\d{3}\M))
  )
  # We could also have some more specific phrasing indicating a complaint about an officer.  We can't just use "complaint" as a conflict phrase, because
  # this word is used in several different ways in the corpus (synonym for "caller", referring to something like a customer dispute, etc), so we'll only look
  # for the following very specific wording.
  |
  (
    # Complaint with a space
    COMPLAINT\s
    # Many different combinations of prepositions are possible
    (OF|ON)\s(AN )?
    # Officer phrases -- last sequence is again an attempt to capture a unit designation.  Since the context for this sequence is more limited than it was
    # above, we don't need to worry about catching the (A132), {A132} stuff.
    (OFFICER|\mOFCR\M|(\m[A-D]\d{3}\M))
  )$$
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
   END AS gang_related,
  CASE
    WHEN call_id IN (SELECT * FROM spanish_ids) THEN TRUE
    ELSE FALSE
  END AS spanish_related,
  CASE
    WHEN call_id IN (SELECT * FROM mentally_ill_ids) THEN TRUE
    ELSE FALSE
  END AS mental_illness_related,
  CASE
    WHEN call_id IN (SELECT * FROM officer_citizen_conflict_ids) THEN TRUE
    ELSE FALSE
  END AS officer_citizen_conflict
FROM call;