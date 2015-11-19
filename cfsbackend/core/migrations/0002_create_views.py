# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            """
CREATE MATERIALIZED VIEW in_call AS
  WITH start_ids AS (
    SELECT transaction.transaction_id
    FROM transaction
    WHERE transaction.descr = 'Dispatched'::text
  ), end_ids AS (
    SELECT transaction.transaction_id
    FROM transaction
    WHERE transaction.descr = ANY (ARRAY['Cleared'::text, 'Canceled'::text])
  )
  SELECT row_number() OVER (ORDER BY c.call_id) AS in_call_id,
    c.call_id,
    start_.time_recorded AS start_time,
    end_.time_recorded AS end_time,
    start_.shift_id,
    start_.call_unit_id
  FROM call c,
    (SELECT cl1.call_log_id,
            cl1.transaction_id,
            cl1.shift_id,
            cl1.time_recorded,
            cl1.call_id,
            cl1.call_unit_id,
            cl1.close_code_id
           FROM call_log cl1
          WHERE (cl1.transaction_id IN ( SELECT start_ids.transaction_id
                   FROM start_ids))) start_,
    (SELECT cl2.call_log_id,
            cl2.transaction_id,
            cl2.shift_id,
            cl2.time_recorded,
            cl2.call_id,
            cl2.call_unit_id,
            cl2.close_code_id
           FROM call_log cl2
          WHERE (cl2.transaction_id IN ( SELECT end_ids.transaction_id
                   FROM end_ids))) end_
  WHERE start_.call_id = c.call_id AND end_.call_id = c.call_id AND start_.call_unit_id = end_.call_unit_id AND start_.time_recorded = (( SELECT max(cl_closest_start.time_recorded) AS max
           FROM call_log cl_closest_start
          WHERE cl_closest_start.call_id = end_.call_id AND cl_closest_start.call_unit_id = end_.call_unit_id AND (cl_closest_start.transaction_id IN ( SELECT start_ids.transaction_id
                   FROM start_ids)) AND cl_closest_start.time_recorded < end_.time_recorded)) AND end_.time_recorded = (( SELECT min(cl_closest_end.time_recorded) AS min
           FROM call_log cl_closest_end
          WHERE cl_closest_end.call_id = start_.call_id AND cl_closest_end.call_unit_id = start_.call_unit_id AND (cl_closest_end.transaction_id IN ( SELECT end_ids.transaction_id
                   FROM end_ids)) AND cl_closest_end.time_recorded > start_.time_recorded))
  ORDER BY c.call_id;
            """
        ),
        migrations.RunSQL(
            """
CREATE MATERIALIZED VIEW officer_activity AS
WITH sergeants AS (
         SELECT call_unit.call_unit_id
           FROM call_unit
          WHERE call_unit.descr = ANY (ARRAY['A100'::text, 'A200'::text, 'A300'::text, 'A400'::text, 'A500'::text, 'B100'::text, 'B200'::text, 'B300'::text,
 'B400'::text, 'B500'::text, 'C100'::text, 'C200'::text, 'C300'::text, 'C400'::text, 'C500'::text, 'D100'::text, 'D200'::text, 'D300'::text, 'D400'::text, '
D500'::text])
        ), valid_call_units AS (
         SELECT DISTINCT shift_unit.call_unit_id
           FROM shift_unit
        )
 SELECT row_number() OVER (ORDER BY activity.start_time) AS officer_activity_id,
    activity.call_unit_id,
    activity.start_time,
    activity.end_time,
    activity.officer_activity_type_id,
    activity.call_id
   FROM ( SELECT ic.call_unit_id,
            ic.start_time,
            ic.end_time,
            ( SELECT officer_activity_type.officer_activity_type_id
                   FROM officer_activity_type
                  WHERE officer_activity_type.descr = 'IN CALL - DIRECTED PATROL'::text) AS officer_activity_type_id,
            ic.call_id
           FROM in_call ic
             JOIN call c ON ic.call_id = c.call_id
          WHERE ic.start_time IS NOT NULL AND ic.end_time IS NOT NULL AND (ic.end_time - ic.start_time) < '1 day'::interval AND NOT (ic.call_unit_id IN ( SELECT sergeants.call_unit_id
                   FROM sergeants)) AND (ic.call_unit_id IN ( SELECT valid_call_units.call_unit_id
                   FROM valid_call_units)) AND (c.nature_id IN ( SELECT nature.nature_id
                   FROM nature
                  WHERE nature.descr = ANY (ARRAY['DIRECTED PATROL'::text, 'FOOT  PATROL'::text])))
        UNION ALL
         SELECT ic.call_unit_id,
            ic.start_time,
            ic.end_time,
            ( SELECT officer_activity_type.officer_activity_type_id
                   FROM officer_activity_type
                  WHERE officer_activity_type.descr = 'IN CALL - SELF INITIATED'::text) AS officer_activity_type_id,
            ic.call_id
           FROM in_call ic
             JOIN call c ON ic.call_id = c.call_id
          WHERE ic.start_time IS NOT NULL AND ic.end_time IS NOT NULL AND (ic.end_time - ic.start_time) < '1 day'::interval AND NOT (ic.call_unit_id IN ( SELECT sergeants.call_unit_id
                   FROM sergeants)) AND (ic.call_unit_id IN ( SELECT valid_call_units.call_unit_id
                   FROM valid_call_units)) AND NOT (c.nature_id IN ( SELECT nature.nature_id
                   FROM nature
                  WHERE nature.descr = ANY (ARRAY['DIRECTED PATROL'::text, 'FOOT  PATROL'::text]))) AND c.call_source_id = (( SELECT call_source.call_source_id
                   FROM call_source
                  WHERE call_source.descr = 'Self Initiated'::text))
        UNION ALL
         SELECT ic.call_unit_id,
            ic.start_time,
            ic.end_time,
            ( SELECT officer_activity_type.officer_activity_type_id
                   FROM officer_activity_type
                  WHERE officer_activity_type.descr = 'IN CALL - CITIZEN INITIATED'::text) AS officer_activity_type_id,
            ic.call_id
           FROM in_call ic
             JOIN call c ON ic.call_id = c.call_id
          WHERE ic.start_time IS NOT NULL AND ic.end_time IS NOT NULL AND (ic.end_time - ic.start_time) < '1 day'::interval AND NOT (ic.call_unit_id IN ( SELECT sergeants.call_unit_id
                   FROM sergeants)) AND (ic.call_unit_id IN ( SELECT valid_call_units.call_unit_id
                   FROM valid_call_units)) AND NOT (c.nature_id IN ( SELECT nature.nature_id
                   FROM nature
                  WHERE nature.descr = ANY (ARRAY['DIRECTED PATROL'::text, 'FOOT  PATROL'::text]))) AND c.call_source_id <> (( SELECT call_source.call_source_id
                   FROM call_source
                  WHERE call_source.descr = 'Self Initiated'::text))
        UNION ALL
         SELECT oos.call_unit_id,
            oos.start_time,
            oos.end_time,
            ( SELECT officer_activity_type.officer_activity_type_id
                   FROM officer_activity_type
                  WHERE officer_activity_type.descr = 'OUT OF SERVICE'::text) AS officer_activity_type_id,
            NULL::bigint AS call_id
           FROM out_of_service oos
          WHERE oos.start_time IS NOT NULL AND oos.end_time IS NOT NULL AND (oos.end_time - oos.start_time) < '1 day'::interval AND (oos.call_unit_id IN ( SELECT valid_call_units.call_unit_id
                   FROM valid_call_units)) AND NOT (oos.call_unit_id IN ( SELECT sergeants.call_unit_id
                   FROM sergeants))
        UNION ALL
         SELECT DISTINCT ON (sh.shift_id) sh.call_unit_id,
            sh.in_time AS start_time,
            sh.out_time,
            ( SELECT officer_activity_type.officer_activity_type_id
                   FROM officer_activity_type
                  WHERE officer_activity_type.descr = 'ON DUTY'::text) AS officer_activity_type_id,
            NULL::bigint AS call_id
           FROM shift_unit sh
          WHERE sh.in_time IS NOT NULL AND sh.out_time IS NOT NULL AND (sh.out_time - sh.in_time) < '1 day'::interval AND NOT (sh.call_unit_id IN ( SELECT sergeants.call_unit_id
                   FROM sergeants))
  ORDER BY 2) activity;
            """
        ),
        migrations.RunSQL(
            """
CREATE MATERIALIZED VIEW time_sample AS
 SELECT series.time_
   FROM generate_series('2014-01-01 00:00:00'::timestamp without time zone, '2014-12-31 23:59:00'::timestamp without time zone, '00:10:00'::interval) series(time_);
            """
        ),
        migrations.RunSQL(
            """
CREATE MATERIALIZED VIEW discrete_officer_activity AS
 SELECT row_number() OVER (ORDER BY oa.start_time) AS discrete_officer_activity_id,
    ts.time_,
    oa.call_unit_id,
    oa.officer_activity_type_id,
    oa.call_id
   FROM officer_activity oa,
    time_sample ts
  WHERE ts.time_ >= oa.start_time AND ts.time_ <= oa.end_time;
            """
        ),
        migrations.RunSQL(
            """
CREATE MATERIALIZED VIEW call_general_category AS
 WITH gun_ids AS (
         SELECT DISTINCT note.call_id
           FROM note
          WHERE (upper(note.body) ~~ '%GUN%'::text AND upper(note.body) ~ '\m(SHOT|HAND)?GUNS?\M(?! IS INVOLVED)'::text OR upper(note.body) ~~ '%SHOTS HAVE BEEN FIRED%'::text OR upper(note.body)~~ '%RIFLE%'::text AND upper(note.body) ~ 'RIFLE(?!D)S?'::text OR upper(note.body) ~~ '%GUN%'::text AND upper(note.body) ~ 'A GUN IS INVOLVED: .*(\.?22|9\s?MM|\.?45|\.?40)'::text OR upper(note.body) ~~ '%REVOLVER%'::text OR upper(note.body) ~~ '%PISTOL%'::text) AND NOT (upper(note.body) ~ 'NO (SHOT|HAND)?GUNS?'::text OR upper(note.body) ~ 'TOY (GUN|RIFLE|SHOTGUN|PISTOL|HANDGUN)'::text)
        ), gang_ids AS (
         SELECT DISTINCT note.call_id
           FROM note
          WHERE upper(note.body) ~~ '%GANG%'::text AND upper(note.body) ~ '\mGANG'::text OR upper(note.body) ~~ '%CRIP%'::text AND upper(note.body) ~ '\mCRIP\M'::text OR upper(note.body) ~~ '%BLOODS%'::text OR upper(note.body) ~~ '%MS13%'::text
        ), spanish_ids AS (
         SELECT DISTINCT note.call_id
           FROM note
          WHERE upper(note.body) ~~ '%SPANISH%'::text OR upper(note.body) ~~ '%SPAINISH%'::text
        ), mentally_ill_ids AS (
         SELECT DISTINCT note.call_id
           FROM note
          WHERE upper(note.body) ~~ '%10-73%'::text AND upper(note.body) ~ '\m73\M'::text OR upper(note.body) ~~ '%73%'::text AND upper(note.body) ~ '\m73\M'::text AND upper(note.body) !~ 'AGE: 73'::text AND upper(note.body) !~ '73(\.| YOA|-YEAR| YEARS)'::text AND upper(note.body) !~ '[-|.|/]73'::text AND upper(note.body) !~ '\(73\)'::text OR upper(note.body) ~~ '%BAKER ACT%'::text
        ), homeless_ids AS (
         SELECT DISTINCT note.call_id
           FROM note
          WHERE upper(note.body) ~~ '%HOMELESS%'::text OR upper(note.body) ~~ '%VAGRANT%'::text OR upper(note.body) ~~ '%DRIFTER%'::text OR upper(note.body) ~~ '%TRANSIENT%'::text AND upper(note.body) !~~ '%ISCHEMIC%'::text OR upper(note.body) ~~ '%URBAN MINISTRIES%'::text OR upper(note.body) ~~ '%BEGGING%'::text OR upper(note.body) ~~ '%BEGG[AE]R%'::text OR upper(note.body) ~~ '%PANHANDL%'::text
        ), officer_citizen_conflict_ids AS (
         SELECT DISTINCT note.call_id
           FROM note
          WHERE upper(note.body) !~~ '[EMD]%'::text AND upper(note.body) !~~ '[FIRE]%'::text AND upper(note.body) !~~ '[EMS]%'::text AND upper(note.body) ~ '(?x)# <-- (?x) allows comments
  (
    # First check for sequences that indicate an officer phrase
    (OFFICER|\mOFCR\M|\mPD\M|POLICE|(\m[A-D]\d{3}\M(?![)}])))  # that last gargbage is an attempt to match a unit expression in a way that doesn''t catch comments by units (ex. "(A132) <comments>" or "{A143} <comments>")
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
  # We could also have some more specific phrasing indicating a complaint about an officer.  We can''t just use "complaint" as a conflict phrase, because
  # this word is used in several different ways in the corpus (synonym for "caller", referring to something like a customer dispute, etc), so we''ll only look
  # for the following very specific wording.
  |
  (
    # Complaint with a space
    COMPLAINT\s
    # Many different combinations of prepositions are possible
    (OF|ON)\s(AN )?
    # Officer phrases -- last sequence is again an attempt to capture a unit designation.  Since the context for this sequence is more limited than it was
    # above, we don''t need to worry about catching the (A132), {A132} stuff.
    (OFFICER|\mOFCR\M|(\m[A-D]\d{3}\M))
  )'::text
        )
 SELECT call.call_id,
        CASE
            WHEN (call.call_id IN ( SELECT gun_ids.call_id
               FROM gun_ids)) THEN true
            ELSE false
        END AS gun_related,
        CASE
            WHEN (call.call_id IN ( SELECT gang_ids.call_id
               FROM gang_ids)) THEN true
            ELSE false
        END AS gang_related,
        CASE
            WHEN (call.call_id IN ( SELECT spanish_ids.call_id
               FROM spanish_ids)) THEN true
            ELSE false
        END AS spanish_related,
        CASE
            WHEN (call.call_id IN ( SELECT mentally_ill_ids.call_id
               FROM mentally_ill_ids)) THEN true
            ELSE false
        END AS mental_illness_related,
        CASE
            WHEN (call.call_id IN ( SELECT homeless_ids.call_id
               FROM homeless_ids)) THEN true
            ELSE false
        END AS homeless_related,
        CASE
            WHEN (call.call_id IN ( SELECT officer_citizen_conflict_ids.call_id
               FROM officer_citizen_conflict_ids)) THEN true
            ELSE false
        END AS officer_citizen_conflict
   FROM call;
            """
        ),
    ]
