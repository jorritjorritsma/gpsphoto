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
            uploadtime TIMESTAMP WITH TIME ZONE,
            phototime TIMESTAMP WITH TIME ZONE);

SELECT AddGeometryColumn('photos', 'geom', 4326, 'POINT', 3);

grant select,insert,delete,update ON photos TO mapserver;
grant select,update ON photos_id_seq TO mapserver;



