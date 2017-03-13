#!/bin/env python
from webob import Request, Response
from webob.multidict import (NestedMultiDict, MultiDict)
import cgi, os, sys, uuid
from cgi import parse_qs
from datetime import datetime, timedelta
from dateutil import tz
import textwrap
import geojson
import simplekml
from pytz import timezone
import json

from gpsphoto import GpsDb

import cgitb # traceback
cgitb.enable(format='text')

def application(environ, start_response):
    '''
    The following parameters are accepted (with example values)
    timezone=Europe/Amsterdam
    begindate=2016-09-26
    enddate=2016-09-26
    user=jsj@xs4all.nl
    type=nice
    bbox=left,bottom,right,top (decimal degrees)
    numberofdays=6
    f=<json|pjson|kml|kmz>
    '''
    
    data = {}
    query = {}
    try:
        parameters = parse_qs(environ.get('QUERY_STRING', ''))

        # f : json, pjson, kml, kmz
        if  'f' in parameters:
            f = parameters['f'][0].lower()
        else:
            f = 'json'

        # tzdata compatible time zone
        if  'timezone' in parameters:
            timeZone = timezone(parameters['timezone'][0])
        else:
            timeZone = timezone('UTC') # if we cannot get the timezone let's assume UTC
            sys.stderr.write('hallo')
        data['timezone'] = timeZone.zone

        # e.g. 2016-09-26
        if 'begindate' in parameters:
            beginDate = parameters['begindate'][0]
            data['begindate'] = beginDate
        else:
            beginDate = None
        
        if 'enddate' in parameters:
            endDate = parameters['enddate'][0]
            data['enddate'] = endDate
        else:
            endDate = None
        
        # email address / user name?
        if 'user' in parameters:
            user = parameters['user'][0]
            data['user'] = user
        else:
            user = None
        
	# event type (domain value?)
        if 'type' in parameters:
            type = parameters['type'][0]
            data['type'] = type
        else:
            type = None
	
	# bounding box to return points for
        # ST_MakeEnvelope(left, bottom, right, top)
        if 'bbox' in parameters:
            bbox = parameters['bbox'][0]
            data['bbox'] = True
            data['bboxleft'] =   float(bbox.split(',')[0])
            data['bboxbottom'] = float(bbox.split(',')[1])
            data['bboxright'] =   float(bbox.split(',')[2])
            data['bboxtop'] =    float(bbox.split(',')[3])
        else:
            bbox = None

        # Number of days ago.... what does that actually mean....?
        # We take the view of the user
        if 'numberofdays' in parameters:
            numberofdays = parameters['numberofdays'][0]

            #sys.stderr.write('hallo')

            # get current local time of requestor
            if endDate is None:
                endDateTime= datetime.now(timeZone)
                endDate =  endDateTime.strftime("%Y-%m-%d")  # 2016-09-26 18:02:08
            else:
                endDateTime = datetime.strptime(endDate, "%Y-%m-%d")

            # x days ago in whatever timezone
            if beginDate is None:
                beginDateTime = endDateTime - timedelta(days=int(numberofdays))
                beginDate = beginDateTime.strftime("%Y-%m-%d")

            data['enddate'] = endDate
            data['begindate'] = beginDate

        query = {'begindate': "phototime AT TIME ZONE %(timezone)s > %(begindate)s",
              'enddate':   "phototime AT TIME ZONE %(timezone)s < %(enddate)s",
              'user':      "userid ILIKE %(user)s",
              'type':      "type ILIKE %(type)s",
              'bbox':      "ST_MakeEnvelope(%(bboxleft)f,%(bboxbottom)f,%(bboxright)f,%(bboxtop)f)"
             }
        
        gpsDB = GpsDb()

        columns = ['title', 'type', 'description', 'url', 'thumburl', "phototime at time zone '%s' as phototime" % timeZone.zone]
        
        results = gpsDB.getPhotoPoints(columns=columns, query=query, data=data, limit=100)

        if f == 'json' or f == 'pjson':
            points = []
            for entry in results:
                photoTime = entry[6].strftime('%-d %b %Y %-H:%M')
                title = '<h1>%s (%s)</h1>' % (entry[1], entry[2])
                image = '<p><a href="%s"><img src="%s" /></a></p>Photo taken at %s (%s)<br>' % (entry[4], entry[5], photoTime, timeZone.zone)
                description = "<br>".join(textwrap.wrap(entry[3], 40))
                popup = title + image + description
                myFeature = geojson.Feature(geometry=entry[0],
                                             properties={"popup": popup,
                                                         "title": title,
                                                         "eventtype": entry[2],
                                                         "description": description,
                                                         "thumbnail": entry[5],
                                                         "image": entry[4],
                                                         "time": photoTime,
                                                         "timezone": timeZone.zone
                                             })
                points.append(myFeature)
            crs = {
                   "type": "name",
                   "properties": {
                       "name": "EPSG:4326"
                   }
            }

            featurecollection = geojson.FeatureCollection(points, crs=crs)
            
            if f == 'pjson':
                output = "mapitems=" + geojson.dumps(featurecollection)
                response_headers = [('Content-Type', 'application/javascript'), ('Content-Length', str(len(output)))]
            else: # normal geojson
                output = geojson.dumps(featurecollection)
                response_headers = [('Content-Type', 'application/json'), ('Content-Length', str(len(output)))]
        elif f == 'kml' or f == 'kmz':
            kml = simplekml.Kml()
            
            for entry in results:
                pnt = kml.newpoint(name="%s (%s)" % (entry[1], entry[2]), description='<![CDATA[<p><a href="%s"><img src="%s" /></a></p>]]>' % (entry[3], entry[4]), coords=[(entry[0]['coordinates'][0], entry[0]['coordinates'][1], entry[0]['coordinates'][2])])

            output = kml.kml().encode('utf-8')
            response_headers = [('Content-Type', 'application/vnd.google-earth.kml+xml'), ('Content-Length', str(len(output)))]

        else:
            raise() # we should not get here, so raise an exception
        
        status = '200 OK'
        start_response(status, response_headers)
        return [output]
    except Exception, e:
        exc_obj = sys.exc_info()[1]
        exc_tb = sys.exc_info()[2]
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("%s\n" % str(e))
        sys.stderr.write("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))

        status = '400 Bad Request'
        response_headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len(str(e))))]
        start_response(status, response_headers)
        return (str(e))
