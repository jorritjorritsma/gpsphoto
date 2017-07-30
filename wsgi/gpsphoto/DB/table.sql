--Create table
create table photos (
            id BIGSERIAL,
            guid VARCHAR(50),
            filename VARCHAR(100),
            title VARCHAR(80),
            description VARCHAR(500),
            url VARCHAR(500),
            thumburl VARCHAR(500),
            bearing NUMERIC(5,2),
            type VARCHAR(30),
            userid VARCHAR(100),
            event VARCHAR(100),
            verified BOOLEAN,
            positioningmethod VARCHAR(20),
            uploadtime TIMESTAMP WITH TIME ZONE,
            phototime TIMESTAMP WITH TIME ZONE);

-- Create a point geometry column with WGS84 as CRS
SELECT AddGeometryColumn('photos', 'geom', 4326, 'POINT', 3);

-- Create some indexes used in filters
CREATE INDEX ON photos (guid)
CREATE INDEX ON photos (filename)
CREATE INDEX ON photos (title)
CREATE INDEX ON photos (type)
CREATE INDEX ON photos (userid)
CREATE INDEX ON photos (event)
CREATE INDEX ON photos (verified)
CREATE INDEX ON photos (uploadtime)
CREATE INDEX ON photos (phototime)

-- Grant access to table
grant select,insert,delete,update ON photos TO mapserver;
grant select,update ON photos_id_seq TO mapserver;
