#!/bin/env python
from webob import Request, Response
import os
import sys
libdir = os.path.dirname(__file__).replace('/admin', '')
sys.path.append(libdir)
sys.path.append(libdir)
from gpsphoto import GpsPhoto, GpsDb, PhotoStore
import config

def application(environ, start_response):
    try:
        req = Request(environ)
        res = Response()
        #let's get the script name for the form action
        scriptname = environ['SCRIPT_NAME']
        # what field we want to get back from db
        fields = ['verified']
        # poor man's templating for web form
        fieldsDef = {
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
        try: # work around stupid checkbox implementation
            submitted = req.params['submitted']
        except:
            submitted = ""
        # hidden value in form to check if it was actually submitted
        try:
            verified = req.params['verified']
        except:
            if submitted:
                verified = 'false'
            else:
                verified = ""

        # now we want to send a form for filling in
        # only guid and possibly org are populated
        if guid == "":
            raise Exception("No guid provided")
        gpsDB = GpsDb(org = org)
        record = gpsDB.getGpsPhotoRow(guid, fields)
        if len(record) != 1:
            out='{{"result": "{} does not exist"}}'.format(guid)
        else:
            nrArgs = len(req.params)
            # called without submitted form, let's produce one
            if nrArgs == 1 or nrArgs == 2 and org: # 1 or 2 args if 2 org must have value
                out = '<form action="{}" method="POST"><input type="hidden" name="guid" value="{}"><input type="hidden" name="org" value="{}"><input type="hidden" name="submitted" value="true">\n'.format(scriptname, guid, org)
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
                raise Exception("Incorrect parameters provided {} verified".format(verified))
        res.body = out
        return res(environ, start_response)
    except Exception, e:
        exc_obj = sys.exc_info()[1]
        exc_tb = sys.exc_info()[2]
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sys.stderr.write("%s\n" % str(e))
        sys.stderr.write("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))
        res.status = 400
        res.body = str(e)
        return res(environ, start_response)
