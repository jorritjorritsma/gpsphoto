#!/bin/env python
from webob import Request, Response
import os
import sys
libdir = os.path.dirname(__file__).replace('/admin', '')
sys.path.append(libdir)
from gpsphoto import GpsPhoto, GpsDb, PhotoStore
import config

def application(environ, start_response):
    try:
        req = Request(environ)
        res = Response()
        #let's get the script name for the form action
        scriptname = environ['SCRIPT_NAME']
        # what fields do we want to get back
        fields = ['title', 'description', 'incidenttype', 'event', 'verified']
        # poor man's templating for form elements
        fieldsDef = {
                    'title': ['Title', 'text'],
                    'description': ['Description', 'textarea'],
                    'incidenttype': ['Incident type', 'text'],
                    'event': ['Event', 'text'],
                    'lon': ['Longitude (-180 - 180)', 'text'], 
                    'lat': ['Latitude (-90 - 90)', 'text'], 
                    'verified': ['Verified', 'checkbox']
                    }
        # guid is mandatory
        try:
            guid = req.params['guid']
        except:
            guid = ""
        # org sets the table to write to, otherwise default is used
        try:
            org = req.params['org']
        except:
            org = ""
        # now we want to send a form for filling in
        # only guid and possibly org are populated
        if guid == "":
            raise Exception("No guid provided")
        gpsDB = GpsDb(org = org)
        record = gpsDB.getGpsPhotoRow(guid, fields)
        nrArgs = len(req.params)
        # called without submitted form, let's produce one
        if nrArgs == 1 or nrArgs == 2 and org: # 1 or 2 args if 2 org must have value
            # 
            out = '<form action="{}" method="POST"><input type="hidden" name="guid" value="{}"><input type="hidden" name="org" value="{}">\n'.format(scriptname, guid, org)
            for field in fields:
                if fieldsDef[field][1] == 'text':
                    out += '{}<br><input type="text" name="{}" value="{}"><br>'.format(fieldsDef[field][0], field, record[fields.index(field)])
                if fieldsDef[field][1] == 'textarea':
                    out += '{}<br><textarea rows="4" cols="50" name="{}">{}</textarea><br>'.format(fieldsDef[field][0],field, record[fields.index(field)])
                if fieldsDef[field][1] == 'checkbox':
                    if record[fields.index(field)] == True:
                        out += '<input type="checkbox" name="{}" value="true" checked>{}<br>'.format(field, fieldsDef[field][0])
                    else:
                        out += '<input type="checkbox" name="{}" value="true">{}<br>'.format(field, fieldsDef[field][0])
            out += 'Longitude (-180.0 - 180.0)<br><input type="text" name="lon" value=""><br>Latitude (-90.0 - 90.0)<br><input type="text" name="lat" value=""><br><br><input type="submit" value="Submit"></form>'
        else:
            # we recieved an update
            try:
                title = req.params['title']
            except:
                title = ""
            try:
                description = req.params['description']
            except:
                description = ""
            try:
                incidenttype = req.params['type']
            except:
                incidenttype = ""
            try:
                event = req.params['event']
            except:
                event = ""
            try:
                lon = req.params['lon']
            except:
                lon = ""
            try:
                lat = req.params['lat']
            except:
                lat = ""
            try:
                verified = req.params['verified']
            except:
                verified = "false"
            if lon != "" and lat != "":
                positioningmethod = 'manual'
                coordinates = {
                                'lat': lat,
                                'lon': lon,
                                'z': -99999,
                                'bearing': None,
                                'mapdatum': 'WGS-84'
                        }
                rowDict = {'coordinates': coordinates, 'values' : {'guid': guid, 'title': title, 'description' : description, 'incidenttype' : incidenttype, 'event': event, 'positioningmethod': positioningmethod, 'verified': verified}}
            else:
                rowDict = {'values' : {'guid': guid, 'title': title, 'description' : description, 'incidenttype' : incidenttype, 'event': event, 'verified': verified}}

            gpsDB.updateGpsPhotoRow(guid=guid, rowDict=rowDict)
            out = "{result: 'success'}"
        res.body = out
        return res(environ, start_response)
    except Exception, e:
        exc_obj = sys.exc_info()[1]
        exc_tb = sys.exc_info()[2]
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("%s\n" % str(e))
        sys.stderr.write("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))
        status = '400 Bad Request'
        response_headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len(str(e))))]
        start_response(status, response_headers)
        res.status = 400
        res.body = str(e)
        return res(environ, start_response)
    

