#!/bin/bash

org="_$1"

if [ "$org" == "_" ]; then
  org=""
fi


echo "
--Create table
create table photos${org} (
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
SELECT AddGeometryColumn('photos${org}', 'geom', 4326, 'POINT', 3);

-- Create some indexes used in filters
CREATE INDEX ON photos${org} (guid);
CREATE INDEX ON photos${org} (filename);
CREATE INDEX ON photos${org} (title);
CREATE INDEX ON photos${org} (incidenttype);
CREATE INDEX ON photos${org} (userid);
CREATE INDEX ON photos${org} (email);
CREATE INDEX ON photos${org} (oidc_claim_given_name);
CREATE INDEX ON photos${org} (oidc_claim_family_name);
CREATE INDEX ON photos${org} (oidc_claim_name);
CREATE INDEX ON photos${org} (remote_addr);
CREATE INDEX ON photos${org} (event);
CREATE INDEX ON photos${org} (verified);
CREATE INDEX ON photos${org} (uploadtime);
CREATE INDEX ON photos${org} (phototime);

-- Grant access to table
grant select,insert,delete,update ON photos${org} TO mapserver;
grant select,update ON photos${org}_id_seq TO mapserver;
" | psql mapserver -U postgres

