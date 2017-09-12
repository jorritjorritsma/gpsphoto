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
        # Check if we are already very sure about deleting?
        try:
            sure = req.POST['sure']
        except:
            sure = ""
        # now we want to send a form for filling in
        # only guid and possibly org are populated
        if guid == "":
            raise Exception("No guid provided")
        nrArgs = len(req.params)
        # called without submitted form, let's produce one
        if guid and sure == "":
            out = '<form action="{}" method="POST"><input type="hidden" name="guid" value="{}"><input type="hidden" name="org" value="{}">\n'.format(scriptname, guid, org)
            out += '<input type="checkbox" name="{}" value="true">{}<br>'.format('sure', 'Are you sure?')
            out += '<br><br><input type="submit" value="Submit"></form>'
        elif sure == 'true':
            # we must have recieved a delete request
            gpsDB = GpsDb(org = org)
            record = gpsDB.getGpsPhotoRow(guid, ['filename'])
            if len(record) != 1:
                out="{{result: '{} does not exist'}}".format(guid)
            else:
                fileName = record[0]
                photoStore = PhotoStore()
                photoStore.deleteFile(fileName)
                photoStore.deleteFile(os.path.join('thumbs', fileName))
                photoStore.deleteFile(os.path.join('withexif', fileName))
                gpsDB.deleteGpsPhotoRow(guid)
                out = '{{"result": "success"}}'
        elif sure != 'true':
            out = '{{"result": "{} not deleted"}}'.format(guid)
        else:
            raise Exception("Not sure what is expected, are the arguments correct?")
        res.body = out
        return res(environ, start_response)

    except Exception, e:
        exc_obj = sys.exc_info()[1]
        exc_tb = sys.exc_info()[2]
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("%s\n" % str(e))
        sys.stderr.write("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))
        res.status =  400
        res.body = str(e)
        return res(environ, start_response)
    

