import boto3
from botocore.exceptions import ClientError
import datetime
import logging
import os
import time
import sys

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

if 'S3_BUCKET' in os.environ:
    s3bucket = os.getenv('S3_BUCKET')
else:
    log.error('Bucket Not Defined')
    log.error('Export Variable "S3_BUCKET"')
    exit()

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        log.error(e)
        return False
    return True

def main():
  s3 = boto3.client('s3')

  while True:
      time.sleep(5)

      log.info('writing to file')
      timefile = open('time.txt', 'w')
      currenttime = str(datetime.datetime.now())
      timefile.write(currenttime)
      timefile.close()

      log.info('upload file to s3')
      with open('time.txt', "rb") as f:
        s3.upload_fileobj(f, s3bucket, currenttime)

  log.info('finished writing to file')

if __name__ == "__main__":
    main()