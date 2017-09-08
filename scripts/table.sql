--Create table
create table photos (
            id BIGSERIAL,
            guid VARCHAR(50),
            filename VARCHAR(60),
            orgfilename VARCHAR(100),
            title VARCHAR(80),
            description VARCHAR(500),
            bearing NUMERIC(5,2),
            incidenttype VARCHAR(30),
            email VARCHAR(100),
            event VARCHAR(100),
            verified BOOLEAN DEFAULT FALSE,
            positioningmethod VARCHAR(20),
            url VARCHAR(500),
            thumburl VARCHAR(500),
            withexifurl VARCHAR(500),
            userid VARCHAR(100),
            remote_addr VARCHAR(50),
            oidc_claim_email VARCHAR(100),
            oidc_claim_given_name VARCHAR(50),
            oidc_claim_family_name VARCHAR(50),
            oidc_claim_iss VARCHAR(100),
            oidc_claim_name VARCHAR(100),
            oidc_claim_picture VARCHAR(250),
            oidc_claim_profile VARCHAR(250),
            uploadtime TIMESTAMP WITH TIME ZONE,
            phototime TIMESTAMP WITH TIME ZONE);

-- Create a point geometry column with WGS84 as CRS
SELECT AddGeometryColumn('photos', 'geom', 4326, 'POINT', 3);

-- Create some indexes used in filters
CREATE INDEX ON photos (guid);
CREATE INDEX ON photos (filename);
CREATE INDEX ON photos (title);
CREATE INDEX ON photos (incidenttype);
CREATE INDEX ON photos (userid);
CREATE INDEX ON photos (email);
CREATE INDEX ON photos (oidc_claim_given_name);
CREATE INDEX ON photos (oidc_claim_family_name);
CREATE INDEX ON photos (oidc_claim_name);
CREATE INDEX ON photos (remote_addr);
CREATE INDEX ON photos (event);
CREATE INDEX ON photos (verified);
CREATE INDEX ON photos (uploadtime);
CREATE INDEX ON photos (phototime);

-- Grant access to table
grant select,insert,delete,update ON photos TO mapserver;
grant select,update ON photos_id_seq TO mapserver;
