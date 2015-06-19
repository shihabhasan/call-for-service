-- srid: 2264 (NC State Planar) to 4326 (WGS 84)

DROP TABLE IF EXISTS call_latlong;

CREATE TABLE call_latlong AS (
SELECT call_id, geox AS longitude, geoy AS latitude, ST_SetSRID(ST_MakePoint(geox, geoy), 2264) AS point
FROM call
);

UPDATE call_latlong SET
  point = ST_Transform(point, 4326);

UPDATE call_latlong SET
  longitude = ST_X(point),
  latitude = ST_Y(point);

DROP TABLE IF EXISTS incident_latlong;

CREATE TABLE incident_latlong AS (
SELECT incident_id, geox AS longitude, geoy AS latitude, ST_SetSRID(ST_MakePoint(geox, geoy), 2264) AS point
FROM incident
);

UPDATE incident_latlong SET
  point = ST_Transform(point, 4326);

UPDATE incident_latlong SET
  longitude = ST_X(point),
  latitude = ST_Y(point);