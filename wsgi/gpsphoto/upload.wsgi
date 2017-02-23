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
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True) 
        fileitem = form["file"]
        title = form.getvalue("title", 0)
        description = form.getvalue("description", 0)
        user = form.getvalue("user", 0)
        type = form.getvalue("type", 0)
        f = fileitem.file
        fileName = fileitem.filename

        gpsPhoto = GpsPhoto(image = f)
        gpsPhoto.processPhoto()
        
        url = '%s.%s' % (os.path.join(config.S3URL,gpsPhoto.guid), gpsPhoto.imageFormat)
        thumburl = '%s.%s' % (os.path.join(config.S3URL,'thumbs', gpsPhoto.guid), gpsPhoto.imageFormat)

        rowDict = {'coordinates': gpsPhoto.coordinates, 'values' : {'filename': fileName, 'guid': gpsPhoto.guid, 'title': title, 'description' : description, 'userid' : user, 'type' : type, 'url': url, 'thumburl': thumburl, 'uploadtime' : gpsPhoto.uploadtimestampz, 'phototime' : gpsPhoto.phototimestampz}}

        gpsDB = GpsDb()
      
        gpsDB.insertGpsPhotoRow(rowDict=rowDict)
        
        photoStore = PhotoStore()

        photoStore.storeImage(image = gpsPhoto.resizedImage, fileName = '%s.%s' % (gpsPhoto.guid, gpsPhoto.imageFormat), imgFormat = gpsPhoto.imageFormat, exif = gpsPhoto.exifbytes)
        thumbPath = '%s.%s' % (os.path.join('thumbs', gpsPhoto.guid), gpsPhoto.imageFormat)
        photoStore.storeImage(image = gpsPhoto.thumbnail, fileName = thumbPath, imgFormat = gpsPhoto.imageFormat, exif = gpsPhoto.exifbytes)
        status = '200 OK'
        response_headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len('')))]
        start_response(status, response_headers)
        return []
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
