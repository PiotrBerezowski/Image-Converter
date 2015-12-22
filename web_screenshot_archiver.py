from os.path import exists
from boto import connect_s3
import yaml
import os
import PIL
from PIL import Image

conf_file = '/config/conf.yml' if exists('/config/conf.yml') else 'conf.yml'
config = yaml.load(open(conf_file))

aws_conf = config['aws']
s3_conn = connect_s3(aws_conf['access-key'], aws_conf['secret-key'], is_secure=False)
bucket = s3_conn.get_bucket(aws_conf['bucket'])


def upload_image_to_s3(filename, prefix=''):
    full_prefix = aws_conf.get('key-prefix', '') + ("/" + prefix if prefix else '')
    key_path = "/".join([full_prefix, filename.rsplit('/')[-1]])
    k = bucket.new_key(key_path)
    k.set_contents_from_filename(filename, encrypt_key=aws_conf.get('use-server-side-encryption', False))
    k.set_acl('public-read')
    url = k.generate_url(expires_in=0, query_auth=False)
    s3_conn.close()
    key = "/".join(('s3:/', bucket.name, k.name))
    return key, url


def list_of_images():
    LOCAL_PATH = 'C:/Users/PiotrB/Downloads/images/'
    for file in bucket.list(aws_conf['key-prefix']):
        keyString = str(file.key)
        path = LOCAL_PATH + keyString
        thumbnail_path = path[:-4] + '_thumbnail' + '.png'
        if not os.path.exists(path):
            file.get_contents_to_filename(path)
            resize_image(path, thumbnail_path)
            """os.remove(path)"""
            if 'competitor' in thumbnail_path:
                upload_image_to_s3(thumbnail_path, 'thumbnail/competitor')
            elif 'hompage' in thumbnail_path:
                upload_image_to_s3(thumbnail_path, 'thumbnail/homepage')


def resize_image(path, thumbnail_path):
    basewidth = 300
    img = Image.open(path)
    widthpercent = (basewidth / float(img.size[0]))
    height_size = int((float(img.size[1]) * float(widthpercent)))
    img = img.resize((basewidth, height_size), PIL.Image.ANTIALIAS)
    img.save(thumbnail_path)

list_of_images()