UPDATE call_unit cu
SET beat_id = NULL,
    district_id = NULL;

UPDATE call_unit cu
SET beat_id = (
        SELECT beat_id
        FROM beat b
        WHERE b.descr = substring(cu.descr FROM 2 FOR 3)
    ),
    district_id = (
        SELECT district_id
        FROM district d
        WHERE d.descr = 'D' || substring(cu.descr FROM 2 FOR 1)
    )
WHERE cu.descr ~ '[A-D][1-5][0-9][0-9]'
  AND NOT cu.descr ~ '[A-D][1-5]00';
  