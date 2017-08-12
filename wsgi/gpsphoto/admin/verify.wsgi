#!/bin/env python
from webob import Request, Response
from webob.multidict import (NestedMultiDict, MultiDict)
import cgi, os, sys
import cgitb; cgitb.enable()

libdir = os.path.dirname(__file__).replace('/admin', '')
sys.path.append(libdir)
sys.path.append(libdir)

from gpsphoto import GpsPhoto, GpsDb, PhotoStore
import config

def application(environ, start_response):
    try:
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
        #let's get the script name for the form action
        scriptname = environ['SCRIPT_NAME']

        fields = ['verified']
        fieldsDef = {
                    'verified': ['Verified', 'checkbox']
                    }

        # guid is mandatory
        guid = form.getvalue("guid", "")

        # org sets the table to write to, otherwise default is used
        org = form.getvalue("org", "")

        verified = form.getvalue("verified", "")
        
        # now we want to send a form for filling in
        # only guid and possibly org are populated
        if guid == "":
            raise Exception("No guid provided")

        gpsDB = GpsDb(org = org)
        record = gpsDB.getGpsPhotoRow(guid, fields)

        nrArgs = len(form.keys())
        # called without submitted form, let's produce one
        if nrArgs == 1 or nrArgs == 2 and org: # 1 or 2 args if 2 org must have value
            # 
            out = '<form action="{}" method="POST"><input type="hidden" name="guid" value="{}"><input type="hidden" name="org" value="{}">\n'.format(scriptname, guid, org)

            if 'verified' not in fields:
                raise Exception("Argument 'verified' not provided")
            for field in fields:
                if fieldsDef[field][1] == 'checkbox':
                    if record[fields.index(field)] == True:
                        out += '<input type="checkbox" name="{}" value="true" checked>{}<br>'.format(field, fieldsDef[field][0])
                    else:
                        out += '<input type="checkbox" name="{}" value="true">{}<br>'.format(field, fieldsDef[field][0])
            out += '<br><br><input type="submit" value="Submit"></form>'
        elif verified == 'true' or verified == 'false':
            # we recieved an update
            rowDict = {'values' : {'verified': verified}}

            gpsDB.updateGpsPhotoRow(guid=guid, rowDict=rowDict)
            out = "{result: 'success'}"
	else:
            raise Exception("Incorrect parameters provided")
        
        status = '200 OK'
        response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(out)))]
        start_response(status, response_headers)
        return(out)

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
    

