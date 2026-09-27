CREATE TABLE aqi_data1 (
    date TEXT,
    pm25 TEXT,
    pm10 TEXT,
    no TEXT,
    no2 TEXT,
    so2 TEXT,
    co TEXT,
    ozone TEXT,
    xylene TEXT,
    temp TEXT,
    humidity TEXT,
    wind_speed TEXT,
    wind_direction TEXT,
    rainfall TEXT,
    total_rf TEXT,
    solar_radiation TEXT,
    pressure TEXT,
    vws TEXT
);

select * from aqi_data1;

UPDATE aqi_data1
SET
pm25 = NULLIF(NULLIF(pm25, '##'), ''),
pm10 = NULLIF(NULLIF(pm10, '##'), ''),
no = NULLIF(NULLIF(no, '##'), ''),
no2 = NULLIF(NULLIF(no2, '##'), ''),
so2 = NULLIF(NULLIF(so2, '##'), ''),
co = NULLIF(NULLIF(co, '##'), ''),
ozone = NULLIF(NULLIF(ozone, '##'), ''),
xylene = NULLIF(NULLIF(xylene, '##'), ''),
temp = NULLIF(NULLIF(temp, '##'), ''),
humidity = NULLIF(NULLIF(humidity, '##'), ''),
wind_speed = NULLIF(NULLIF(wind_speed, '##'), ''),
wind_direction = NULLIF(NULLIF(wind_direction, '##'), ''),
rainfall = NULLIF(NULLIF(rainfall, '##'), ''),
total_rf = NULLIF(NULLIF(total_rf, '##'), ''),
solar_radiation = NULLIF(NULLIF(solar_radiation, '##'), ''),
pressure = NULLIF(NULLIF(pressure, '##'), ''),
vws = NULLIF(NULLIF(vws, '##'), '');

ALTER TABLE aqi_data1 
MODIFY pm25 FLOAT,
MODIFY pm10 FLOAT,
MODIFY no FLOAT,
MODIFY no2 FLOAT,
MODIFY so2 FLOAT,
MODIFY co FLOAT,
MODIFY ozone FLOAT,
MODIFY xylene FLOAT,
MODIFY temp FLOAT,
MODIFY humidity FLOAT,
MODIFY wind_speed FLOAT,
MODIFY wind_direction FLOAT,
MODIFY rainfall FLOAT,
MODIFY total_rf FLOAT,
MODIFY solar_radiation FLOAT,
MODIFY pressure FLOAT,
MODIFY vws FLOAT;


ALTER TABLE aqi_data1 MODIFY date DATE;

select * from aqi_data1;

SELECT COUNT(*) FROM aqi_data1;

SELECT * FROM aqi_data1 LIMIT 10;

SELECT 
    SUM(date IS NULL) AS date_null,
    SUM(pm25 IS NULL) AS pm25_null,
    SUM(pm10 IS NULL) AS pm10_null,
    SUM(no IS NULL) AS no_null,
    SUM(no2 IS NULL) AS no2_null,
    SUM(so2 IS NULL) AS so2_null,
    SUM(co IS NULL) AS co_null,
    SUM(ozone IS NULL) AS ozone_null,
    SUM(xylene IS NULL) AS xylene_null,
    SUM(temp IS NULL) AS temp_null,
    SUM(humidity IS NULL) AS humidity_null,
    SUM(wind_speed IS NULL) AS wind_speed_null,
    SUM(wind_direction IS NULL) AS wind_direction_null,
    SUM(rainfall IS NULL) AS rainfall_null,
    SUM(total_rf IS NULL) AS total_rf_null,
    SUM(solar_radiation IS NULL) AS solar_radiation_null,
    SUM(pressure IS NULL) AS pressure_null,
    SUM(vws IS NULL) AS vws_null
FROM aqi_data1;

UPDATE aqi_data1 
SET pm25 = (
    SELECT avg_val FROM (SELECT AVG(pm25) AS avg_val FROM aqi_data1) t
)
WHERE pm25 IS NULL;

UPDATE aqi_data1 
SET pm10 = (
    SELECT avg_val FROM (SELECT AVG(pm10) AS avg_val FROM aqi_data1) t
)
WHERE pm10 IS NULL;

UPDATE aqi_data1 
SET no = (
    SELECT avg_val FROM (SELECT AVG(no) AS avg_val FROM aqi_data1) t
)
WHERE no IS NULL;

UPDATE aqi_data1 
SET no2 = (
    SELECT avg_val FROM (SELECT AVG(no2) AS avg_val FROM aqi_data1) t
)
WHERE no2 IS NULL;

UPDATE aqi_data1 
SET so2 = (
    SELECT avg_val FROM (SELECT AVG(so2) AS avg_val FROM aqi_data1) t
)
WHERE so2 IS NULL;

UPDATE aqi_data1 
SET co = (
    SELECT avg_val FROM (SELECT AVG(co) AS avg_val FROM aqi_data1) t
)
WHERE co IS NULL;

UPDATE aqi_data1 
SET ozone = (
    SELECT avg_val FROM (SELECT AVG(ozone) AS avg_val FROM aqi_data1) t
)
WHERE ozone IS NULL;

UPDATE aqi_data1 
SET xylene = (
    SELECT avg_val FROM (SELECT AVG(xylene) AS avg_val FROM aqi_data1) t
)
WHERE xylene IS NULL;

UPDATE aqi_data1 
SET temp = (
    SELECT avg_val FROM (SELECT AVG(temp) AS avg_val FROM aqi_data1) t
)
WHERE temp IS NULL;

UPDATE aqi_data1 
SET humidity = (
    SELECT avg_val FROM (SELECT AVG(humidity) AS avg_val FROM aqi_data1) t
)
WHERE humidity IS NULL;

UPDATE aqi_data1 
SET wind_speed = (
    SELECT avg_val FROM (SELECT AVG(wind_speed) AS avg_val FROM aqi_data1) t
)
WHERE wind_speed IS NULL;

UPDATE aqi_data1 
SET wind_direction = (
    SELECT avg_val FROM (SELECT AVG(wind_direction) AS avg_val FROM aqi_data1) t
)
WHERE wind_direction IS NULL;

UPDATE aqi_data1 
SET rainfall = (
    SELECT avg_val FROM (SELECT AVG(rainfall) AS avg_val FROM aqi_data1) t
)
WHERE rainfall IS NULL;

UPDATE aqi_data1 
SET total_rf = (
    SELECT avg_val FROM (SELECT AVG(total_rf) AS avg_val FROM aqi_data1) t
)
WHERE total_rf IS NULL;

UPDATE aqi_data1 
SET solar_radiation = (
    SELECT avg_val FROM (SELECT AVG(solar_radiation) AS avg_val FROM aqi_data1) t
)
WHERE solar_radiation IS NULL;

UPDATE aqi_data1 
SET pressure = (
    SELECT avg_val FROM (SELECT AVG(pressure) AS avg_val FROM aqi_data1) t
)
WHERE pressure IS NULL;

UPDATE aqi_data1 
SET vws = (
    SELECT avg_val FROM (SELECT AVG(vws) AS avg_val FROM aqi_data1) t
)
WHERE vws IS NULL;


select * from aqi_data1;

SELECT 
MIN(pm25), MAX(pm25),
MIN(pm10), MAX(pm10),
MIN(temp), MAX(temp),
MIN(humidity), MAX(humidity),
MIN(wind_speed), MAX(wind_speed),
MIN(pressure), MAX(pressure)
FROM aqi_data1;

SELECT 
MIN(pm25), MAX(pm25),
MIN(pm10), MAX(pm10),
MIN(no), MAX(no),
MIN(no2), MAX(no2),
MIN(so2), MAX(so2),
MIN(co), MAX(co),
MIN(ozone), MAX(ozone),
MIN(xylene), MAX(xylene),
MIN(temp), MAX(temp),
MIN(humidity), MAX(humidity),
MIN(wind_speed), MAX(wind_speed),
MIN(wind_direction), MAX(wind_direction),
MIN(rainfall), MAX(rainfall),
MIN(total_rf), MAX(total_rf),
MIN(solar_radiation), MAX(solar_radiation),
MIN(pressure), MAX(pressure),
MIN(vws), MAX(vws)
FROM aqi_data1;


UPDATE aqi_data1 SET pm25 = ABS(pm25) WHERE pm25 < 0;
UPDATE aqi_data1 SET pm10 = ABS(pm10) WHERE pm10 < 0;
UPDATE aqi_data1 SET no = ABS(no) WHERE no < 0;
UPDATE aqi_data1 SET no2 = ABS(no2) WHERE no2 < 0;
UPDATE aqi_data1 SET so2 = ABS(so2) WHERE so2 < 0;
UPDATE aqi_data1 SET co = ABS(co) WHERE co < 0;
UPDATE aqi_data1 SET ozone = ABS(ozone) WHERE ozone < 0;
UPDATE aqi_data1 SET xylene = ABS(xylene) WHERE xylene < 0;

UPDATE aqi_data1 SET humidity = 100 WHERE humidity > 100;
UPDATE aqi_data1 SET humidity = 0 WHERE humidity < 0;

UPDATE aqi_data1 SET temp = 60 WHERE temp > 60;

UPDATE aqi_data1 
SET pressure = NULL 
WHERE pressure < 800 OR pressure > 1100;

SELECT MIN(pressure), MAX(pressure) FROM aqi_data1;

ALTER TABLE aqi_data1 DROP COLUMN pressure;


SELECT * FROM aqi_data1
WHERE 
pm25 IS NULL OR pm10 IS NULL OR temp IS NULL;

UPDATE aqi_data1
SET
pm25 = ROUND(pm25, 2),
pm10 = ROUND(pm10, 2),
no = ROUND(no, 2),
no2 = ROUND(no2, 2),
so2 = ROUND(so2, 2),
co = ROUND(co, 2),
ozone = ROUND(ozone, 2),
xylene = ROUND(xylene, 2),
temp = ROUND(temp, 2),
humidity = ROUND(humidity, 2),
wind_speed = ROUND(wind_speed, 2),
wind_direction = ROUND(wind_direction, 2),
rainfall = ROUND(rainfall, 2),
total_rf = ROUND(total_rf, 2),
solar_radiation = ROUND(solar_radiation, 2),
vws = ROUND(vws, 2);

select * from aqi_data1;

ALTER TABLE aqi_data1 
MODIFY pm25 DECIMAL(10,2),
MODIFY pm10 DECIMAL(10,2),
MODIFY no DECIMAL(10,2),
MODIFY no2 DECIMAL(10,2),
MODIFY so2 DECIMAL(10,2),
MODIFY co DECIMAL(10,2),
MODIFY ozone DECIMAL(10,2),
MODIFY xylene DECIMAL(10,2),
MODIFY temp DECIMAL(10,2),
MODIFY humidity DECIMAL(10,2),
MODIFY wind_speed DECIMAL(10,2),
MODIFY wind_direction DECIMAL(10,2),
MODIFY rainfall DECIMAL(10,2),
MODIFY total_rf DECIMAL(10,2),
MODIFY solar_radiation DECIMAL(10,2),
MODIFY vws DECIMAL(10,2);


select * from aqi_data1;

SELECT COUNT(*) FROM aqi_data1;

SELECT * FROM aqi_data1;


