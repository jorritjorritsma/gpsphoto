#!/bin/env python
from webob import Request, Response
from webob.multidict import (NestedMultiDict, MultiDict)
import cgi, os, sys
import cgitb; cgitb.enable()

from pprint import pprint

libdir = os.path.dirname(__file__).replace('/admin', '')
sys.stderr.write(libdir)

#sys.path.append(os.path.dirname(__file__))
sys.path.append(libdir)
from gpsphoto import GpsPhoto, GpsDb, PhotoStore
import config

def application(environ, start_response):
    try:
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
        #let's get the script name for the form action
        scriptname = environ['SCRIPT_NAME']

        # guid is mandatory
        guid = form.getvalue("guid", "")

        # org sets the table to write to, otherwise default is used
        org = form.getvalue("org", "")

        # Check if we are already very sure about deleting?
        sure = form.getvalue("sure", "")

        # now we want to send a form for filling in
        # only guid and possibly org are populated
        if guid == "":
            raise Exception("No guid provided")


        nrArgs = len(form.keys())
        # called without submitted form, let's produce one
        if nrArgs == 1 or nrArgs == 2 and org: # 1 or 2 args if 2 org must have value
            # 
            out = '<form action="{}" method="POST"><input type="hidden" name="guid" value="{}"><input type="hidden" name="org" value="{}">\n'.format(scriptname, guid, org)
            out += '<input type="checkbox" name="{}" value="true">{}<br>'.format('sure', 'Are you sure?')
            out += '<br><br><input type="submit" value="Submit"></form>'

        elif sure == 'true':
            # we must have recieved a delete request
            gpsDB = GpsDb(org = org)

            record = gpsDB.getGpsPhotoRow(guid, ['filename'])
            fileName = record[0]
            photoStore = PhotoStore()
            photoStore.deleteFile(fileName)
            photoStore.deleteFile(os.path.join('thumbs', fileName))
            gpsDB.deleteGpsPhotoRow(guid)
            out = "{result: 'success'}"
        elif sure != 'true':
            out = "{result: '{} not deleted'}".format(guid)
        else:
            raise Exception("Not sure what is expected, are the arguments correct?")
        
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
    

