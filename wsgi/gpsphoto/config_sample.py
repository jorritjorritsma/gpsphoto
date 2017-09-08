ID = ''                             # S3 ID
KEY = ''                            # S3 key
# S3 bucket (needs to be lowercase)
BUCKET = {'default': 'gpsphoto', 'org1': 'gpsphoto_org1', 'org2': 'gpsphoto_org2'}
S3URL = 'https://s3-eu-west-1.amazonaws.com'
DB_HOST = 'localhost'               # can also be fqdn
DB_NAME = ''                        # DB Name (postgresql)
DB_USER = ''                        # DB User name
DB_PASSWD = ''                      # DB Password
DB_PHOTOTABLE = ''                  # table name
DB_RECORDLIMIT = 2000               # nr of records to return 'ALL' returns all records
KEEP_EXIF = {'default':False,
            'org1':True,
            'org2':True}            # keep exif header in saved photos
IMG_WIDTH = 1280                    # max width of stored image
IMG_HEIGHT = 1024                   # max height of stored image
THUMB_WIDTH = 200                   # max widht of stored thumbnail
THUMB_HEIGHT = 133                  # max height of stored thumbnail
