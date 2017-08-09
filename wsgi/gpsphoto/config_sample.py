ID = ''                     # S3 ID
KEY = ''                    # S3 key
BUCKET = ''                 # S3 bucket (needs to be lowercase)
S3URL = 'https://s3-eu-west-1.amazonaws.com/%s/' % BUCKET
DB_HOST = 'localhost'       # can also be fqdn
DB_NAME = ''                # DB Name (postgresql)
DB_USER = ''                # DB User name
DB_PASSWD = ''              # DB Password
DB_PHOTOTABLE = ''          # table name
DB_RECORDLIMIT = 2000       # nr of records to return 'ALL' returns all records
KEEP_EXIF = True|False      # keep exif header in saved photos
PGP_PRIVACY = True|False    # keep original exif header as well as submitter in
                            # gpg'd message
PGP_PUBLIC_KEY = ""         # Location where public PGP key can be downloaded
IMG_WIDTH = 1280            # max width of stored image
IMG_HEIGHT = 1024           # max height of stored image
THUMB_WIDTH = 200           # max widht of stored thumbnail
THUMB_HEIGHT = 133          # max height of stored thumbnail
