-- srid: 2264 (NC State Planar) to 4326 (WGS 84)

DROP TABLE IF EXISTS call_latlong;

CREATE TABLE call_latlong AS (
    SELECT call_id, st_x(point) AS longitude, st_y(point) AS latitude, point
    FROM (
        SELECT call_id, 
        st_Transform(ST_SetSRID(ST_MakePoint(geox, geoy), 2264), 4326)::geometry(Point, 4326) AS point
        FROM call
    ) AS a
);

DROP TABLE IF EXISTS incident_latlong;

CREATE TABLE incident_latlong AS (
    SELECT incident_id, st_x(point) AS longitude, st_y(point) AS latitude, point
    FROM (
        SELECT incident_id, 
        -- We have to divide incident x and y by 100 to get the proper numbers
        st_Transform(ST_SetSRID(ST_MakePoint(geox/100, geoy/100), 2264), 4326)::geometry(Point, 4326) AS point
        FROM incident
    ) AS a
);