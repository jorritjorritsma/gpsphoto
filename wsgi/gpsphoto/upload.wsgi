#!/bin/env python
from webob import Request, Response
from webob.multidict import (NestedMultiDict, MultiDict)
import cgi, os, sys
import cgitb; cgitb.enable()

from pprint import pprint

sys.path.append(os.path.dirname(__file__))
from gpsphoto import GpsPhoto, GpsDb, PhotoStore
import config

def application(environ, start_response):
    try:
        #form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True) 

        req = Request(environ)
        res = Response()

        sys.stderr.write("{}\n".format(req.params))

        if 'file' in req.params:
            fileitem = req.POST["file"]
        else:
            raise Exception("No file given")
        # voluntary email address - will never be exposed.
        try:
            email = req.POST["email"]
        except:
            email = ""
        # let's get all the OID auth parameters - none of these are exposed
        # user id from authentication provider
        userid = req.remote_user # None if not provided
        # let's also store remote address
        remote_addr = req.environ['REMOTE_ADDR']
        # registered email at authenticator
        try:
            oidc_claim_email = req.environ['OIDC_CLAIM_email']
        except:
            oidc_claim_email = ''
        # First Name
        try:
            oidc_claim_given_name = req.environ['OIDC_CLAIM_given_name']
        except:
            oidc_claim_given_name = ''
        # Family name
        try:
            oidc_claim_family_name = req.environ['OIDC_CLAIM_family_name']
        except:
            oidc_claim_family_name = ''
        # authentication provider
        try:
            oidc_claim_iss = req.environ['OIDC_CLAIM_iss']
        except:
            oidc_claim_iss = ''
        # Full name
        try:
            oidc_claim_name = req.environ['OIDC_CLAIM_name']
        except:
            oidc_claim_name = ''
        # Link to profile pic
        try:
            oidc_claim_picture = req.environ['OIDC_CLAIM_picture']
        except:
            oidc_claim_picture = ''
        # user profile
        try:
            oidc_claim_profile = req.environ['OIDC_CLAIM_profile']
        except:
            oidc_claim_profile = ''

        # org sets the table to write to, otherwise default is used
        try:
            org = req.POST["org"]
        except:
            org = None
        try:
            title = req.POST["title"]
        except:
            title = ""
        try:
            description = req.POST["description"]
        except:
            description = ""
        
        try:
            incidenttype = req.POST["type"]
        except:
            incidenttype = ""
        try:
            event = req.POST["event"]
        except:
            event = ""
        try:
            f = req.POST["f"]
        except:
            f = ""

        f = fileitem.file
        orgFileName = fileitem.filename

        gpsPhoto = GpsPhoto(image = f)
        if not gpsPhoto.processPhoto():
            raise Exception("Photo has no reliable coordinate information")

        fileName = '{}.{}'.format(gpsPhoto.guid, gpsPhoto.imageFormat)
        
        # defined as variable to allow this script to be used as well for photos without gps data
        positioningmethod = "GPS" 
        
        filename = '{}.{}'.format(gpsPhoto.guid, gpsPhoto.imageFormat)
        
        # Store photo
        photoStore = PhotoStore(org=org)
        # Store public photo - no exif included
        url = photoStore.storeImage(image = gpsPhoto.resizedImage,
            fileName = '{}.{}'.format(gpsPhoto.guid, gpsPhoto.imageFormat),
            imgFormat = gpsPhoto.imageFormat,
            makePublic=True)
        
        # Let's see if we want to store photo with exif for evidence purposes
        # these will not be made public, probably we need en admin cgi to serve them up
        if org is None or org == "":
            keepExif = config.KEEP_EXIF['default']
        else:
            keepExif = config.KEEP_EXIF[org]
        if keepExif: # Check if we want to save the exif for this org
            withexifurl = photoStore.storeImage(image = gpsPhoto.resizedImage,
                fileName = 'withexif/{}.{}'.format(gpsPhoto.guid, gpsPhoto.imageFormat),
                imgFormat = gpsPhoto.imageFormat,
                exif = gpsPhoto.exifbytes,
                keepExif=keepExif,
                makePublic=False)
        else:
            withexifurl = "" # need something to go in DB
        # Store Thumbnail
        thumburl = photoStore.storeImage(image = gpsPhoto.thumbnail,
            fileName = 'thumbs/{}.{}'.format(gpsPhoto.guid, gpsPhoto.imageFormat),
            imgFormat = gpsPhoto.imageFormat,
            makePublic=True)

        #url = os.path.join(config.S3URL, filename)
        #thumburl = os.path.join(config.S3URL, 'thumbs', filename)
        #withexifurl = os.path.join(config.S3URL, 'withexif', filename)

        # Store record in DB
        gpsDB = GpsDb(org = org)
        rowDict = {'coordinates': gpsPhoto.coordinates, 
                    'values' : {
                        'filename': fileName,
                        'orgfilename': orgFileName,
                        'guid': gpsPhoto.guid,
                        'title': title,
                        'description': description,
                        'incidenttype': incidenttype,
                        'event': event,
                        'positioningmethod': positioningmethod,
                        'url': url,
                        'thumburl': thumburl,
                        'withexifurl': withexifurl,
                        'userid': userid,
                        'email': email,
                        'oidc_claim_email': oidc_claim_email,
                        'oidc_claim_given_name': oidc_claim_given_name,
                        'oidc_claim_family_name': oidc_claim_family_name,
                        'oidc_claim_iss': oidc_claim_iss,
                        'oidc_claim_name': oidc_claim_name,
                        'oidc_claim_picture': oidc_claim_picture,
                        'oidc_claim_profile': oidc_claim_profile,
                        'uploadtime': gpsPhoto.uploadtimestampz,
                        'phototime': gpsPhoto.phototimestampz}}
        gpsDB.insertGpsPhotoRow(rowDict=rowDict)
        res.body = '{{"guid": "{}"}}'.format(gpsPhoto.guid)
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


