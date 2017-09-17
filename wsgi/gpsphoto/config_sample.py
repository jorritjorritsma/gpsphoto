ID = ''                             # S3 ID
KEY = ''                            # S3 key
# Bucket names should not contain upper-case letters
# Bucket names should not contain underscores (_)
# Bucket names should not end with a dash
# Bucket names should be between 3 and 63 characters long
# Bucket names cannot contain dashes next to periods (e.g., "my-.bucket.com" and "my.-bucket" are invalid)
# Bucket names cannot contain periods - Due to our S3 client utilizing SSL/HTTPS, Amazon documentation
# indicates that a bucket name cannot contain a period, otherwise you will not be able to upload files
# from our S3 browser in the dashboard
BUCKET = {'default': '<bucket name',
        'some_org': <some org bucket name>}
S3URL = 'https://s3-eu-west-1.amazonaws.com/%s/' % BUCKET
S3LOCATION = ''                     # AWS region http://docs.aws.amazon.com/general/latest/gr/rande.html
DB_HOST = 'localhost'               # can also be fqdn
DB_NAME = ''                        # DB Name (postgresql)
DB_USER = ''                        # DB User name
DB_PASSWD = ''                      # DB Password
DB_PHOTOTABLE = ''                  # table name
DB_RECORDLIMIT = 2000               # nr of records to return 'ALL' returns all records
KEEP_EXIF = {'default':True|False,
            'some_org':True|False}  # keep exif header in saved photos
IMG_WIDTH = 1280                    # max width of stored image
IMG_HEIGHT = 1024                   # max height of stored image
THUMB_WIDTH = 200                   # max widht of stored thumbnail
THUMB_HEIGHT = 133                  # max height of stored thumbnail
