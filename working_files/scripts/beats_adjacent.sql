1 CREATE OR REPLACE FUNCTION public.beats_adjacent(integer, integer)
  2  RETURNS boolean
  3  LANGUAGE sql
  4 AS $function$
  5     SELECT ST_Touches(a.geom, b.geom)
  6     FROM beat AS a, beat AS b
  7     WHERE a.lawbeat = $1
  8       AND b.lawbeat = $2;
  9 $function$

