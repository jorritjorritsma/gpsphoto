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
import datetime
import uuid
import os, sys


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

    def processPhoto(self):
        if self.image.format != 'JPEG' and gpsPhoto.image.format != 'PNG':
            return(None)
        else:
            self.imageFormat = self.image.format
        self.getExif()
        self.correctImageOrientation()
        self.getCoordinates()
        self.getPhotoTimeStampZ()
        self.getUploadTimeStampZ()
        self.getResizedImage()
        self.get_guid()
    
    def getImageFromUrl(self, url):
        '''Download image from provided URL'''
        try:
            fd = urllib.urlopen(url)
            imageFile = io.BytesIO(fd.read())
            self.image = Image.open(imageFile)
            return(True)
        except Exception, e:
            print "failed getImageFromUrl"
            print str(e)
            return(None)

    def getImageFromPath(self, path):
        '''Get image from file path'''
        try:
            self.image = Image.open(path)
            return(True)
        except Exception, e:
            print "failed getImageFromPath"
            print str(e)
            return(None)

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

            gps_altitude = self._get_if_exist(gps_info, 'GPSAltitude')
            #gps_altitude_ref = self._get_if_exist(gps_info, 'GPSAltitudeRef')
            try:
                z = [float(x)/float(y) for x, y in gps_altitude]
            except:
                z = None
            
            gps_mapdatum = self._get_if_exist(gps_info, "GPSMapDatum")

            gps_imgdirection = self._get_if_exist(gps_info, "GPSImgDirection")
            try:
                bearing = [float(x)/float(y) for x, y in gps_imgdirection]
            except:
                bearing = None

            self.coordinates = {'mapdatum': gps_mapdatum, 'lon': lon, 'lat': lat, 'bearing': bearing, 'z': z}
            return(True)
        except Exception, e:
            print 'We bailed out of getCoordinates'
            print str(e)
            self.coordinates = {}
            return(None)
        
    def getDate(self):
        try:
            gps_info = self.exif['GPSInfo']
            rawdate = self._get_if_exist(gps_info, "GPSDateStamp")
            date = rawdate.split(":")
            self.date = map(int, date)
            return(True)
        except Exception, e:
            print 'failed getDate'
            print str(e)
            self.date = []
            return(None)
    
    def getTime(self):
        try:
            gps_info = self.exif['GPSInfo']
            rawtime = self._get_if_exist(gps_info, "GPSTimeStamp")
            self.time = [rawtime[0][0], rawtime[1][0], rawtime[2][0]]
            return(True)
        except Exception, e:
            print 'failed getTime'
            print str(e)
            self.time = []
            return(None)

    def getUploadTimeStampZ(self):
        try:
            self.uploadtimestampz = '{:%Y-%m-%d %H:%M:%S} UTC'.format(datetime.datetime.now())
            return (True)
        except Exception, e:
            print 'failed getUploadTimeStampZ'
            print str(e)
            self.uploadtimestampz = None
            return(None)

    def getPhotoTimeStampZ(self):
        try:
            self.getDate()
            self.getTime()
            self.phototimestampz = '%4d-%02d-%02d %02d:%02d:%02d UTC' % (self.date[0], self.date[1], self.date[2], self.time[0], self.time[1], self.time[2])
            return (True)
        except Exception, e:
            print 'failed getPhotoTimeStampZ'
            print str(e)
            self.phototimestampz = None
            return(None)
    
    def getEpoch(self):
        try:
            self.getDate(self.exif)
            self.getTime(self.exif)
            date_time = '%4d:%02d:%02d:%02d:%02d:%02d' % (self.date[0], self.date[1], self.date[2], self.time[0], self.time[1], self.time[2])
            pattern = '%Y:%m:%d:%H:%M:%S'
            self.epoch = int(time.mktime(time.strptime(date_time, pattern)))
            return(True)
        except Exception, e:
            print 'failed getEpoch'
            print str(e)
            self.epoch = None
            return(None)
        
    def getResizedImage(self, width=1280, height=1024, thumbwidth=200, thumbheight=133):
        try:
            oldsize = self.image.size
            ratio = min(float(width)/oldsize[0], float(height)/oldsize[1])
            size = int(oldsize[0] * ratio), int(oldsize[1] * ratio)
            self.resizedImage = self.image.resize((size), Image.ANTIALIAS)

            ratio = min(float(thumbwidth)/oldsize[0], float(thumbheight)/oldsize[1])
            size = int(oldsize[0] * ratio), int(oldsize[1] * ratio)
            self.thumbnail = self.image.resize((size), Image.ANTIALIAS)

        except Exception, e:
            print 'failed getResizedImage'
            print str(e)
            return(None)
 
############################################################################### 
class GpsDb:
    def __init__(self):
        sys.path.append(os.path.dirname(__file__))
        import config
        self.config = config

        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (self.config.DB_HOST, self.config.DB_NAME, self.config.DB_USER, self.config.DB_PASSWD)
        self.conn = psycopg2.connect(conn_string)
        self.cur = self.conn.cursor()
        self.gpsPhotoTable = self.config.DB_PHOTOTABLE
    
    def insertGpsPhotoRow(self, rowDict={}, table=''):
        # { 'coordinates' : {   'lat' : <latitude>,
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
        #               'type': <cartographic type>,
        #               'userid': <email address / user identifyer>,
        #               'uploadtime': <yyyy-mm-dd hh:mm:ss UTC>,
        #               'phototime': <yyyy-mm-dd hh:mm:ss UTC>}
        # }
        if table == '':
            table = self.gpsPhotoTable
            
        values = rowDict['values']
                    
        lat = rowDict['coordinates']['lat']
        lon = rowDict['coordinates']['lon']
        bearing = rowDict['coordinates']['bearing']
        if 'z' not in rowDict['coordinates'] or not rowDict['coordinates']['z']:
            z = -999
        else:
            z = rowDict['coordinates']['z']
            
        mapdatum = rowDict['coordinates']['mapdatum']
        if mapdatum == 'WGS-84':
            rsid = 4326
        else:
            rsid = 4326 # don't know how to handle this yet....

        sql = "INSERT INTO " + table + " (guid, filename, title, description, url, thumburl, bearing, type, userid, uploadtime, phototime, geom) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), %s))"
        
        data = (values['guid'], values['filename'], values['title'], values['description'], values['url'], values['thumburl'], bearing, values['type'], values['userid'], values['uploadtime'], values['phototime'], lon, lat, z, rsid)
        
        self.cur.execute(sql, data)
        self.cur.execute('SELECT LASTVAL()')
        lastid = self.cur.fetchone()[0]
        self.conn.commit()
        return(lastid)
    
    def getPhotoPointByOwner(self, rowid=None, columns=[], user=None):
        sql = "select " + ','.join(columns) + " from "    + rowDict['table'] + " where userid = %s"
        self.cur.execute(sql, user)
        result = self.cur.fetchall()
        return(result)

    def getPhotoPointsAsGeojson(self, columns=[], query=None, data=None):
        queryArray = []
        for item in query.keys():
            if item in data.keys():
                queryArray.append(query[item])
        whereClause = ' AND '.join(queryArray)

        # No query entries, no WHERE clause
        if len(queryArray) == 0:
            sql = "select ST_AsGeoJSON(geom)," + ','.join(columns) + " from " + self.config.DB_PHOTOTABLE
        else:
            sql = "select ST_AsGeoJSON(geom)," + ','.join(columns) + " from " + self.config.DB_PHOTOTABLE + ' WHERE ' + whereClause

        self.cur.execute(sql, data)
        result = self.cur.fetchall()
        return(result)
    
    def getPhotoPointsAsKml(self, columns=[], whereClause=None, data=None):
        sql = "select ST_AsKML(geom)," + ','.join(columns) + " from " + self.config.DB_PHOTOTABLE + whereClause
        self.cur.execute(sql, data)
        result = self.cur.fetchall()
        return(result)
    
    def getAllPhotoPointsAsKml(self, columns=[]):
        sql = "select ST_AsKML(geom)," + ','.join(columns) + " from " + self.config.DB_PHOTOTABLE
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return(result)

    def disconnect(self, conn, cur):
        self.cur.close()
        self.conn.close()
    
###############################################################################
class PhotoStore:
    def __init__(self):
        sys.path.append(os.path.dirname(__file__))
        import config
        self.config = config
        
        self.connS3 = boto.connect_s3(self.config.ID,self.config.KEY)
    
        try:
            self.bucket = self.connS3.get_bucket(self.config.BUCKET)
        except:
            self.bucket = self.connS3.create_bucket(self.config.BUCKET)
        
    def deleteFile(self, fileName):
        k = Key(self.bucket)
        k.key = fileName
        self.bucket.delete_key(k)
    
    def storeImage(self, image=None, fileName=None, imgFormat=None, exif=None):
        # image is a PIL Image object, fileName the full name including path on how it should be stored
        import StringIO
        if image is not None and fileName is not None and imgFormat is not None and exif is not None:
            k = Key(self.bucket)
            k.key = fileName
            try:
                output = StringIO.StringIO()
                image.save(output, format=imgFormat, exif=exif)
                #image.save(output, format=imgFormat)
                fileContents = output.getvalue()
                output.close()
                k.set_contents_from_string(fileContents)
                k.make_public()
            except Exception, e:
                print "failed storeImage"
                print str(e)
                return(False)
        else:
            return(False)
