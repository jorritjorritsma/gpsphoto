#!/bin/env python
from webob import Request, Response
import psycopg2
import urllib
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
import time
import boto
from boto.s3.key import Key
from boto.s3.connection import Location
import datetime
import uuid
import os, sys
import ast # to digest the geom object from postgis geojson

###############################################################################
class GpsPhoto:
    def __init__(self, imageUrl=None, imagePath=None, image=None):
        sys.path.append(os.path.dirname(__file__))
        import config
        self.config = config

        if imageUrl is not None:
            self.getImageFromUrl(imageUrl)
        if imagePath is not None:
            self.getImageFromPath(imagePath)
        if image is not None:
            self.image = Image.open(image)
        if not hasattr(self, 'image'):
            raise Exception("No image provided to gpsphoto")

    def processPhoto(self):
        if self.image.format != 'JPEG' and gpsPhoto.image.format != 'PNG':
            raise Exception("File provided was no JPG or PNG file")
        else:
            self.imageFormat = self.image.format
        if self.getExif():
            self.getCoordinates()
            self.correctImageOrientation()
        self.getPhotoTimeStampZ()
        self.getUploadTimeStampZ()
        self.getResizedImage()
        self.get_guid()
        return(True)
    
    def getImageFromUrl(self, url):
        '''Download image from provided URL'''
        try:
            fd = urllib.urlopen(url)
            imageFile = io.BytesIO(fd.read())
            self.image = Image.open(imageFile)
        except Exception, e:
            print "failed getImageFromUrl"
            print str(e)

    def getImageFromPath(self, path):
        '''Get image from file path'''
        try:
            self.image = Image.open(path)
        except Exception, e:
            print "failed getImageFromPath"
            print str(e)

    def _get_if_exist(self, data, key):
        if key in data:
            return data[key]
        return None
    
    def get_guid(self):
        self.guid = uuid.uuid1().get_hex()

    def getExif(self):
        try:
            exif_data = {}
            self.exifbytes = self.image.info['exif']
            exif = self.image._getexif()
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]
                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
            self.exif = exif_data
            return(True)
        except Exception, e:
            print "failed getExif"
            print str(e)
            return(None)
    
    def correctImageOrientation(self):
        try:
            for orientation in self.exif.keys():
                if orientation == 'Orientation':
                    break
            if self.exif[orientation] == 3: 
                rotatedImage = self.image.rotate(180, expand=True)
                self.image = rotatedImage
            if self.exif[orientation] == 6: 
                rotatedImage = self.image.rotate(270, expand=True)
                self.image = rotatedImage
            if self.exif[orientation] == 8:
                rotatedImage = self.image.rotate(90, expand=True)
                self.image = rotatedImage
            return(True)
        except Exception, e:
            print "failed correctImageOrientation"
            print str(e)
            return(None)
    
    
    def _convert_to_dec_degrees(self, value):
        """Helper function to convert the GPS coordinates stored in the EXIF to decimal degress"""
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)
    
    def getCoordinates(self):
        try:
            gps_info = self.exif['GPSInfo']
        except:
            return(False) # let the upload script decide how to handle
        try:
            gps_latitude = self._get_if_exist(gps_info, "GPSLatitude")
            gps_latitude_ref = self._get_if_exist(gps_info, 'GPSLatitudeRef')
            gps_longitude = self._get_if_exist(gps_info, 'GPSLongitude')
            gps_longitude_ref = self._get_if_exist(gps_info, 'GPSLongitudeRef')

            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = self._convert_to_dec_degrees(gps_latitude)
                if gps_latitude_ref != "N":                     
                    lat = 0 - lat

                lon = self._convert_to_dec_degrees(gps_longitude)
                if gps_longitude_ref != "E":
                    lon = 0 - lon
                # check if coordinates are sane and if not....
		if lat > 90 or lat < -90 or lon > 180 or lon < -180:
                    raise Exception("No usable coordinates stored in photo")

            gps_altitude = self._get_if_exist(gps_info, 'GPSAltitude')
            try:
                z = [float(x)/float(y) for x, y in gps_altitude]
            except:
                z = None
            
            gps_mapdatum = self._get_if_exist(gps_info, "GPSMapDatum")
            if gps_mapdatum:
                gps_mapdatum = gps_mapdatum.rstrip()

            gps_imgdirection = self._get_if_exist(gps_info, "GPSImgDirection")
            try:
                bearing = [float(x)/float(y) for x, y in gps_imgdirection]
            except:
                bearing = None

            self.coordinates = {'mapdatum': gps_mapdatum, 'lon': lon, 'lat': lat, 'bearing': bearing, 'z': z}
            return(True)
        except Exception, e:
            exc_obj = sys.exc_info()[1]
            exc_tb = sys.exc_info()[2]
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(str(e))
            print("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))
            print('Failed on getCoordinates')
            if hasattr(self, 'coordinates'):
                del self.coordinates
            return(None)
    
    #def setCoordinates(self):

    def getDateTime(self):
        """
        Get timestamp from photo's exif header
        GPS time and date are tried first, if that fails the dateTimeOriginal
        """
        # let's first try to get gpsdate and gpstime DateTimeOriginal
        try:
            gps_info = self.exif['GPSInfo']
            rawtime = self._get_if_exist(gps_info, "GPSTimeStamp")
            rawdate = self._get_if_exist(gps_info, "GPSDateStamp")
            date = rawdate.split(":")
            date = map(int, date)
            self.photoTimeStamp = time.strptime("{:04d}:{:02d}:{:02d} {:02d}:{:02d}:{:02d}".format(date[0], date[1], date[2], rawtime[0][0], rawtime[1][0], rawtime[2][0]), '%Y:%m:%d %H:%M:%S')
        except:
            print("Failed getting GPSTimeStamp and GPSDateStamp, trying camera's time")
        # if that fails, fail over to DateTimeOriginal which is the time of the camera / photo
        # this is however less reliable time
        if not hasattr(self, 'photoTimeStamp') or self.photoTimeStamp is None:
            try:
                dateTimeOriginal = self.exif["DateTimeOriginal"]
                # 2017:07:06 11:45:51
                self.photoTimeStamp = time.strptime(dateTimeOriginal, '%Y:%m:%d %H:%M:%S')
            except:
                raise Exception("Could not take time from photo")
        
    def getUploadTimeStampZ(self):
        self.uploadtimestampz = '{:%Y-%m-%d %H:%M:%S} UTC'.format(datetime.datetime.utcnow())

    def getPhotoTimeStampZ(self):
        """ 
        Format time stamp for time zone aware postgres time
        Delete it if the content does not make sense
        """
        self.getDateTime()
        self.phototimestampz = time.strftime("%Y-%m-%d %H:%M:%S UTC", self.photoTimeStamp)
        # if the time is not properly set, there is probably no connection with GPS
        if self.phototimestampz.startswith('0000'):
            del self.phototimestampz
    
    def getResizedImage(self, imgWidth=None, imgHeight=None, thumbWidth=None, thumbHeight=None):
        """ 
        Resize image to max width or height to exceed neither while maintaining aspect ratio
        self.resizedImage and self.thumbnail contain the resized image
        """
        if imgWidth is None:
            imgWidth = self.config.IMG_WIDTH
        if imgHeight is None:
            imgHeight = self.config.IMG_HEIGHT
        if thumbWidth is None:
            thumbWidth = self.config.THUMB_WIDTH
        if thumbHeight is None:
            thumbHeight = self.config.THUMB_HEIGHT

        try:
            oldSize = self.image.size
            ratio = min(float(imgWidth)/oldSize[0], float(imgHeight)/oldSize[1])
            size = int(oldSize[0] * ratio), int(oldSize[1] * ratio)
            self.resizedImage = self.image.resize((size), Image.ANTIALIAS)

            ratio = min(float(thumbWidth)/oldSize[0], float(thumbHeight)/oldSize[1])
            size = int(oldSize[0] * ratio), int(oldSize[1] * ratio)
            self.thumbnail = self.image.resize((size), Image.ANTIALIAS)

        except Exception, e:
            print 'failed getResizedImage'
            print str(e)
            return(None)
 
############################################################################### 
class GpsDb:
    def __init__(self, org=None):
        sys.path.append(os.path.dirname(__file__))
        import config
        self.config = config

        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (self.config.DB_HOST, self.config.DB_NAME, self.config.DB_USER, self.config.DB_PASSWD)
        self.conn = psycopg2.connect(conn_string)
        self.cur = self.conn.cursor()
        if org is None or org == '':
            self.gpsPhotoTable = self.config.DB_PHOTOTABLE
        else:
            self.gpsPhotoTable = '{}_{}'.format(self.config.DB_PHOTOTABLE, org)
    
    def insertGpsPhotoRow(self, rowDict={}):
        # rowdict = {
        # 'coordinates' : {     'lat' : <latitude>,
        #                       'lon' : <longitude>,
        #                       'z' : <z>,
        #                       'bearing' : <compass bearing>,
        #                       'crs' : <map datum>},
        # 'values' : {  'guid': <guid>
        #               'filename': <photo name>,
        #               'title': <title>,
        #               'description': <description>,
        #               'url': <photo url>,
        #               'thumburl: <url of thumbnail>,
        #               'incidenttype': <cartographic type>,
        #               'userid': <email address / user identifier>,
        #               'event': <event name>,
        #               'positioningmethod': <'GPS'|'manual'>
        #               'uploadtime': <yyyy-mm-dd hh:mm:ss UTC>,
        #               'phototime': <yyyy-mm-dd hh:mm:ss UTC>}
        # }
        try:
            (sql, data) = self._updateOrModifySql(rowDict, 'insert')

            self.cur.execute(sql, data)
            self.cur.execute('SELECT LASTVAL()')
            lastid = self.cur.fetchone()[0]
            self.conn.commit()
            return(lastid)
        except Exception, e:
            print(str(e))
            raise Exception('Failed to insert a record')
    
    def updateGpsPhotoRow(self, guid=None, rowDict={}):
        # rowdict = {
        # 'coordinates' : {     'lat' : <latitude>,
        #                       'lon' : <longitude>,
        #                       'z' : <z>,
        #                       'bearing' : <compass bearing>,
        #                       'crs' : <map datum>},
        # 'values' : {  'title': <title>,
        #               'description': <description>,
        #               'incidenttype': <cartographic type>,
        #               'event': <name of event>,
        #               'verified': <Boolean>,
        #               'positioningmethod': <'GPS'|'manual'>
        #            }
        # }
        if guid is None:
            raise Exception("Trying to update a record without specifying a guid")
        try:
            rowDict['guid'] = guid
            (sql, data) = self._updateOrModifySql(rowDict, 'update')
            self.cur.execute(sql, data, )
            self.conn.commit()
            return(True)
        except Exception, e:
            print(str(e))
            raise Exception("Failed to update record")

    def _updateOrModifySql(self, rowDict, type):
        # rowdict = {
        # 'guid' :      guid,
        # 'coordinates' : {     'lat' : <latitude>,
        #                       'lon' : <longitude>,
        #                       'z' : <z>,
        #                       'bearing' : <compass bearing>,
        #                       'crs' : <map datum>},
        # 'values' : {  'filename': <photo name>,
        #               'title': <title>,
        #               'description': <description>,
        #               'url': <photo url>,
        #               'thumburl: <url of thumbnail>,
        #               'incidenttype': <cartographic type>,
        #               'userid': <email address / user identifier>,
        #               'event': <event name>,
        #               'positioningmethod': <'GPS'|'manual'>
        #               'uploadtime': <yyyy-mm-dd hh:mm:ss UTC>,
        #               'phototime': <yyyy-mm-dd hh:mm:ss UTC>}
        # },
        # type = 'insert'|'update'
        
        fields = {}
        # all normal attributes get the same sql statent format
        for item in rowDict['values']:
            fields[item] = '%s' # fields for psychopg2 sql statement
        
        # if this is an update, coordinates don't have to be provided.
        # if they are however, they need to be complete
        if 'coordinates' in rowDict:
            # let's process the coordinates
            lat = rowDict['coordinates']['lat']
            lon = rowDict['coordinates']['lon']

            bearing = rowDict['coordinates']['bearing']
            if 'z' not in rowDict['coordinates'] or not rowDict['coordinates']['z']:
                z = -99999
            else:
                z = rowDict['coordinates']['z']
            
            mapdatum = rowDict['coordinates']['mapdatum']
            if mapdatum == 'WGS-84':
                rsid = 4326
            else:
                rsid = 4326 # don't know how to handle this yet, we should never end up here anyway
                # bedause it's just not correct I'll keep this here and maybe one day...
           
            # geom is special
            rowDict['values']['geom'] = [lon, lat, z, rsid]
            fields['geom'] = 'ST_SetSRID(ST_MakePoint(%s, %s, %s), %s)'
        
            # bearing was considered part of the geometry, hence added here as normal attribute
            rowDict['values']['bearing'] = rowDict['coordinates']['bearing']
            fields['bearing'] = '%s'

        columns = [] # columns to build sql statement
        values = [] # fields to build sql statement
        data = [] # data (tuple) to use with sql execute
        for item in fields:
            columns.append(item)
            values.append(fields[item])
            if item == 'geom':
                data += rowDict['values']['geom']
            else:
                data.append(rowDict['values'][item])
            
        if type == 'insert':
            sql = "INSERT INTO %s (%s) VALUES (%s)" % (self.gpsPhotoTable, ','.join(columns), ','.join(values))
        elif type == 'update':
            # We'll be overwriting the guid with itself, but that should be ok
            sql = "UPDATE {} SET ({}) = ({}) WHERE guid = %s".format(self.gpsPhotoTable, ','.join(columns), ','.join(values))
            data.append(rowDict['guid'])
        else:
            return(None)
        
        # let's for now see what sql we are getting
        return(sql, tuple(data))

    def getPhotoPoints(self, columns=[], orderColumn='phototime', order='DESC', query=None, data=None, limit=None):
        '''
        columns[]:   array of column names to get back from query
        orderColumn: column to order results by
        order:       order direction (default: DESC)
        query:       dict of query stubs to be AND-ed together to one query
        data:        dict with values to fill the parameters in query dict stubs.
                     The keys of data entries must match the parameters in the stubs.
        limit:       Limit the amount of results returned by a number ('ALL' gets all records)
        '''

        if limit is None:
            limit = self.config.DB_LIMITRECORDS
      
        queryArray = []
        if query:
            for item in query.keys():
                if item in data.keys():
                    queryArray.append(query[item])
        whereClause = ' AND '.join(queryArray)

        # No query entries, no WHERE clause
        if len(queryArray) == 0:
            sql = "SELECT ST_AsGeoJSON(geom), {} FROM {} ORDER BY {} {} LIMIT {}".format(','.join(columns), self.gpsPhotoTable, orderColumn, order, limit)
        else:
            sql = "SELECT ST_AsGeoJSON(geom), {} FROM {} WHERE {} ORDER BY {} {} LIMIT {}".format(','.join(columns), self.gpsPhotoTable, whereClause, orderColumn, order, limit)

        self.cur.execute(sql, data)
        result = self.cur.fetchall()
        pythonicResult = []
        for i in range(len(result)):
            # for some reason the object given back by ST_AsGeoJSON is not interpreted as python object
            # the ast.literal_eval makes it a python dict, which we can easily use again.
            try:
                pythonicResult.append([ast.literal_eval(result[i][0])] + list(result[i][1:]))
            except Exception, e:
                exc_obj = sys.exc_info()[1]
                exc_tb = sys.exc_info()[2]
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(str(e))
                print(result[i][0])
                print(result[i][1:])
                print("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))
                raise Exception("Failed to do getPhotoPoints")
        return(pythonicResult)
    
    def getGpsPhotoRow(self, guid, fields):
        try:
            sql = "select {} from {} where guid = %s".format(",".join(fields), self.gpsPhotoTable)
            self.cur.execute(sql, [guid])
            result = self.cur.fetchone()
            return(result)
        except Exception, e:
            print(str(e))
            raise Exception("Failed to do getGpsPhotoRow")

    def verifyPhoto(self, guid, status):
        try:
            sql = "update {} SET verified = %s where guid = %s".format(self.gpsPhotoTable)
            self.cur.execute(sql, [status, guid])
            self.conn.commit()
        except Exception, e:
            print(str(e))
            raise Exception("Could not verify / unverify record")

    def deleteGpsPhotoRow(self, guid):
        try:
            sql = "delete from {} where guid = %s".format(self.gpsPhotoTable)
            self.cur.execute(sql, [guid])
            self.conn.commit()
        except Exception, e:
            print(str(e))
            raise Exception("Could not delete record")
    
    def disconnect(self, conn, cur):
        self.cur.close()
        self.conn.close()
        
        
    
###############################################################################
class PhotoStore:
    def __init__(self, org = None):
        sys.path.append(os.path.dirname(__file__))
        import config
        self.config = config

        if org is None or org == '':
            self.bucketName = self.config.BUCKET['default']
        else:
            self.bucketName = self.config.BUCKET[org]
        
        self.connS3 = boto.connect_s3(self.config.ID,self.config.KEY)
    
        try:
            self.bucket = self.connS3.get_bucket(self.bucketName)
        except:
            try:
                #location = 'location=Location.{}'.format(self.config.S3LOCATION)
                self.bucket = self.connS3.create_bucket(self.bucketName, location=Location.EU)
            except Exception, e:
                exc_obj = sys.exc_info()[1]
                exc_tb = sys.exc_info()[2]
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print str(e)
                print("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))
                raise Exception("Could not open or create S3 bucket")

        
    def deleteFile(self, fileName):
        try:
            k = Key(self.bucket)
            k.key = fileName
            self.bucket.delete_key(k)
        except Exception, e:
            exc_obj = sys.exc_info()[1]
            exc_tb = sys.exc_info()[2]
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print str(e)
            print("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))
            raise Exception("failed to delete file from S3")
    
    def storeImage(self, image=None, fileName=None, imgFormat=None, exif=None, keepExif=False, makePublic=False):
        # image is a PIL Image object, fileName the full name including path on how it should be stored
        import StringIO
        if image is not None and fileName is not None and imgFormat is not None:
            k = Key(self.bucket)
            k.key = fileName
            try:
                output = StringIO.StringIO()
                if keepExif: # True
                    image.save(output, format=imgFormat, exif=exif, quality="keep")
                else: # False
                    image.save(output, format=imgFormat, quality="keep")
                fileContents = output.getvalue()
                output.close()
                k.set_contents_from_string(fileContents)
                if makePublic: # True
                    k.make_public()
            except Exception, e:
                exc_obj = sys.exc_info()[1]
                exc_tb = sys.exc_info()[2]
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print str(e)
                print("%s line %s\n" % (str(fname), str(exc_tb.tb_lineno)))
                raise Exception("failed storeImage")
            return "{}/{}/{}".format(self.config.S3URL, self.bucketName, fileName)
        else:
            raise Exception("No suitable image provided")






