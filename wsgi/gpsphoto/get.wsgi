#!/bin/env python
from webob import Request, Response
import os
import sys
import uuid
import json
from datetime import datetime, timedelta
from dateutil import tz
import textwrap
import geojson
import simplekml
from pytz import timezone

from gpsphoto import GpsDb

import cgitb # traceback
cgitb.enable(format='text')

def application(environ, start_response):
    '''
    The following parameters are accepted (with example values)
    timezone=Europe/Amsterdam
    begindate=2016-09-26
    enddate=2016-09-26
    org='pemantau'
    user=jsj@xs4all.nl
    incidenttype=nice
    bbox=left,bottom,right,top (decimal degrees)
    numberofdays=6
    f=<json|pjson|kml|kmz>
    '''

    req = Request(environ)
    res = Response()
    data = {}
    query = {}
    try:
        # f : json, pjson, kml, kmz
        if  'f' in req.params:
            f = req.GET['f'].lower()
        else:
            f = 'json'
        # tzdata compatible time zone
        if  'timezone' in req.params:
            timeZone = timezone(req.GET['timezone'])
        else:
            timeZone = timezone('UTC') # if we cannot get the timezone let's assume UTC
        data['timezone'] = timeZone.zone
        # e.g. 2016-09-26
        if 'begindate' in req.params and req.params['begindate'] != "":
            beginDate = req.params['begindate']
            data['begindate'] = beginDate
        else:
            beginDate = None
        if 'enddate' in req.params and req.params['enddate'] != "":
            endDate = req.params['enddate']
            data['enddate'] = endDate
        else:
            endDate = None
        # org determines which table the data is stored in and possibly what domain values are available.
        if 'org' in req.params and req.params['org'] != "":
            org = req.params['org']
        else:
            org = None
        # email address / user name?
        if 'user' in req.params and req.params['user'] != "":
            user = req.params['user']
            data['user'] = user
        else:
            user = None
        if 'event' in req.params and req.params['event'] != "":
            event = req.params['event']
            data['event'] = event
        else:
            event = None
        # is the entry verified?
        if 'verified' in req.params and req.params['verified'] != "":
            verified = req.params['verified']
            data['verified'] = verified
        else:
            verified = None
        # incidenttype (domain value?)
        if 'type' in req.params and req.params['type'] != "":
            incidenttype = req.params['type']
            data['incidenttype'] = incidenttype
        else:
            incidenttype = None
        # bounding box to return points for
        # ST_MakeEnvelope(left, bottom, right, top)
        if 'bbox' in req.params:
            bbox = req.params['bbox']
            data['bbox'] = True
            data['bboxleft'] =   float(bbox.split(',')[0])
            data['bboxbottom'] = float(bbox.split(',')[1])
            data['bboxright'] =   float(bbox.split(',')[2])
            data['bboxtop'] =    float(bbox.split(',')[3])
        else:
            bbox = ""
        # Number of days ago.... what does that actually mean....?
        # We take the view of the user
        if 'numberofdays' in req.params and req.params['numberofdays'] != "":
            numberofdays = req.params['numberofdays']
            # get current local time of requester
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
        query = {'begindate': 	"phototime AT TIME ZONE %(timezone)s > %(begindate)s",
              'enddate':        "phototime AT TIME ZONE %(timezone)s < %(enddate)s",
              'user':           "userid ILIKE %(user)s",
              'incidenttype':   "incidenttype ILIKE %(incidenttype)s",
              'event':   	    "event ILIKE %(event)s",
              'verified':       "verified = %(verified)s",
              'bbox':           "geom @ ST_MakeEnvelope(%(bboxleft)s,%(bboxbottom)s,%(bboxright)s,%(bboxtop)s)"
             }
        gpsDB = GpsDb(org = org)
        columns = ['guid', 'title', 'incidenttype', 'description', 'url', 'thumburl', 'verified', 'positioningmethod', 'event', "phototime at time zone '%s' as phototime" % timeZone.zone]
        results = gpsDB.getPhotoPoints(columns=columns, query=query, data=data, limit=100)
        if f == 'json' or f == 'pjson':
            points = []
            for entry in results:
                guid = entry[1] # geometry = 0!
                photoTime = entry[10].strftime('%-d %b %Y %-H:%M')
                title = '<h1>{}</h1>'.format(entry[2], entry[3], entry[9])
                image = '<p><a href="%s"><img src="%s" /></a></p>Photo taken at %s (%s)<br>' % (entry[5], entry[6], photoTime, timeZone.zone)
                if entry[3] is not None or entry[3] != '':
                    incidenttype = 'Type: {}<br>'.format(entry[3])
                else:
                    incidenttype = ''
                if entry[9] is not None or entry[9] != '':
                    event = 'Event: {}<br>'.format(entry[9])
                else:
                    event = ''
                description = "<br>".join(textwrap.wrap(entry[4], 40))
                popup = title + image + description
                myFeature = geojson.Feature(geometry=entry[0],
                                             id=entry[1],
                                             properties={"popup": popup,
                                                         "title": title,
                                                         "incidenttype": entry[3],
                                                         "description": description,
                                                         "thumbnail": entry[6],
                                                         "image": entry[5],
                                                         "verified": entry[7],
                                                         "positioningmethod": entry[8],
                                                         "event": entry[9],
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
                res.body = "mapitems=" + geojson.dumps(featurecollection)
                res.headerlist = [('Content-Type', 'application/javascript')]
            else: # normal geojson
                res.body = geojson.dumps(featurecollection)
                res.headerlist = [('Content-Type', 'application/json')]
        elif f == 'kml' or f == 'kmz':
            kml = simplekml.Kml()
            for entry in results:
                pnt = kml.newpoint(name="%s (%s)" % (entry[2], entry[3]), description='<![CDATA[<p><a href="%s"><img src="%s" /></a></p>]]>' % (entry[4], entry[5]), coords=[(entry[0]['coordinates'][0], entry[0]['coordinates'][1], entry[0]['coordinates'][2])])

            res.body = kml.kml().encode('utf-8')
            res.headerlist = [('Content-Type', 'application/vnd.google-earth.kml+xml')]
        else:
            raise() # we should not get here, so raise an exception
        return res(environ, start_response)
    except Exception, e:
        exc_obj = sys.exc_info()[1]
        exc_tb = sys.exc_info()[2]
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("%s\n" % str(e))
        sys.stderr.write("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))
        res.status = 400
        res.headerlist = [('Content-type', 'text/html')]
        res.body = str(e)
        return res(environ, start_response)

