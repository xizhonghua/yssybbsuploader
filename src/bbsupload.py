#!/usr/bin/env python

################################################
# Author: Zhonghua Xi (xxfflower@YSSY)
# Email: xizhonghua (AT) gmail.com
################################################

import imghdr
import math
import json
import os
import re
import sys
import time
import hashlib
from PIL import Image
from multiprocessing.pool import ThreadPool
from requests import Request, Session


def is_ascii(s):
  return all(ord(c) < 128 for c in s)


def unwrap_self_upload_file(arg, **kwarg):
  uploader = arg[0]
  filename = arg[1]
  return uploader.upload_file(filename)


class Uploader():

  def __init__(self, config):
    self.config = config
    self.headers = {
        'Origin': 'https://bbs.sjtu.edu.cn',
        'Referer': 'https://bbs.sjtu.edu.cn/file/bbs/index/index.htm',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
    }
    self.session = Session()

  # resize an image
  def resize_img(self, filename, factor=1.0):
    img = Image.open(filename)
    scale = 1800.0 / max(img.size) * factor
    new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
    new_img = img.resize(new_size, Image.LANCZOS)
    path, basename = os.path.split(filename)
    hashed_filename = hashlib.md5(basename).hexdigest()
    new_filename = path + '/' + hashed_filename + '_resized_by_uploader.jpg'
    new_img.save(new_filename, "JPEG", quality=80, optimize=True)
    return new_filename

  # fit an image to given file size
  def fit_img(self, filename, max_size=1000 * 1000):
    factor = 1.0
    tmp_filename = None
    file_size = 0
    while True:
      tmp_filename = self.resize_img(filename, factor)
      file_size = os.path.getsize(tmp_filename)
      if file_size > max_size:
        factor *= 0.75
      else:
        break
    return tmp_filename, file_size

  # test whether a file is an image
  def is_image(self, filename):
    if imghdr.what(filename) == None:
      return False
    return True

  # upload a file to server, return its uploaded url
  def upload_file(self, filename):

    org_filename = filename

    # file size in kb
    file_size = int(os.path.getsize(filename) / 1024.00)

    sys.stdout.write(
        'uploading ' +
        filename + ' [' + str(file_size) + 'kb]' +
        ' to ' +
        self.config['board'] +
        '\n')

    tmp_filename = None
    resized = False

    # A large file or has Unicode characters in the filename
    if file_size > 1000 or not is_ascii(filename):
      if self.is_image(filename):
        tmp_filename, size = self.fit_img(filename)
        sys.stdout.write(
            'resized to ' + tmp_filename + ', new image filesize = ' +
            str(
                size /
                1024) +
            'kb\n')

        filename = tmp_filename
        resized = True
      else:
        # other types
        sys.stdout.write('Cannot handle non-image large file...')
        return ''

    files = {
        'up': open(filename, 'rb')
    }

    resp = self.session.post('https://bbs.sjtu.edu.cn/bbsdoupload',
                             headers=self.headers,
                             files=files,
                             data=self.payload)

    m = re.search(r"<font color=green>([^<]+)", resp.text)

    if m is None:
      sys.stdout.write('failed to upload ' + org_filename + '\n')
      return ''

    url = m.groups()[0]

    sys.stdout.write(
        'uploaded ' +
        org_filename.decode('utf-8') +
        (' (resized)' if resized else '') +
        ' to ' +
        url +
        '\n')

    return url

  def login(self):
    resp = self.session.post('https://bbs.sjtu.edu.cn/bbslogin',
                             data={
                                 'id': self.config['id'],
                                 'pw': self.config['pw']
                             },
                             headers=self.headers)

    if 'utmpuserid' in self.session.cookies.get_dict():
      print 'Logged in with id:', self.config['id']
      return True
    else:
      print 'Failed to login with id:', self.config['id']
      return False

  def post(self):

    self.payload = {
        'board': self.config['board'],
        'title': self.config['title'].decode('utf-8').encode('gb2312'),
        'signature': 1,
        'autocr': 'on',
        'text': 'content',
        'level': 0,
        'live': 180,
    }

    print 'board   =', self.config['board']
    print 'title   =', self.config['title']
    print 'content =', self.config['content']

    full_content = self.config['content'].decode('utf-8')

    files = self.config['files']

    start = time.time()

    threads = 4
    if self.config['single_thread']:
      threads = 1

    pool = ThreadPool(threads)
    results = pool.map(
        unwrap_self_upload_file, zip(
            [self] * len(files), files))

    end = time.time()

    print 'all files uploaded in', end - start, 's'

    full_content = '\n'.join(results) + '\n'

    if self.config['ad'] == True:
      full_content += 'Post by bbsupload.py ver: ' + config['version'] + "\n"

    self.payload['text'] = full_content.encode('gb2312')

    if self.config['up_only'] == True:
      return

    resp = self.session.post(
        'https://bbs.sjtu.edu.cn/bbssnd',
        headers=self.headers,
        data=self.payload)

    print 'Posting...'
    if resp.status_code == 200:
      print 'Posted!'
    else:
      print '!Error! Failed to post'

# load account info into config


def load_account(filename, config):
  with open(filename) as data_file:
    account = json.load(data_file)
  config['id'] = account['id']
  config['pw'] = account['pw']


def print_usage(argv, config):
  print 'YSSY BBS file uploader ver: ' + config['version']
  print 'Usage:', argv[0], '[options] file1 file2 file3...'
  print 'Options:'
  print '  -a, --account  ', 'account filename. default is "account.json"'
  print '  -b, --board:   ', 'board to upload/post. default is "PPPerson"'
  print '  -t, --title:   ', 'post title. default is "noname"'
  print '  -c, --content: ', 'content of the post. default is empty'
  print '  -n, --no-ad:   ', 'post without ad'
  print '  -s:            ', 'use single thread. default uses 4 threads'
  print '  -u, --up-only  ', 'upload only, do not post'
  print '  -h, --help:    ', 'print usage'


def parse_args(argv):
  config = {
      'id': None,
      'pw': None,
      'board': 'PPPerson',
      'title': 'noname',
      'content': '',
      'files': [],
      'ad': True,
      'account': 'account.json',
      'version': '0.2',
      'up_only': False,
      'single_thread': False
  }

  index = 1
  while index < len(argv):
    arg = argv[index]
    if arg == '--account' or arg == '-a':
      index += 1
      config['account'] = sys.argv[index]
    elif arg == '--pw' or arg == '-p':
      index += 1
      config['pw'] = sys.argv[index]
    elif arg == '--board' or arg == '-b':
      index += 1
      config['board'] = sys.argv[index]
    elif arg == '--title' or arg == '-t':
      index += 1
      config['title'] = sys.argv[index]
    elif arg == '--content' or arg == '-c':
      index += 1
      config['content'] = sys.argv[index]
    elif arg == '--no-ad' or arg == '-n':
      config['ad'] = False
    elif arg == '--up-only' or arg == '-u':
      config['up_only'] = True
    elif arg == '-s':
      config['single_thread'] = True
    elif arg == '--help' or arg == '-h':
      print_usage(sys.argv, config)
      sys.exit(0)
    elif arg[0] == '-':
      print 'Unknown flag', arg
      print_usage(sys.argv, config)
      sys.exit(-1)
    else:
      config['files'].append(arg)
    index += 1
    # end while
  return config

if __name__ == '__main__':
  config = parse_args(sys.argv)
  load_account(config['account'], config)

  # filter out resized images
  config['files'] = filter(
      lambda f: '_resized_by_uploader' not in f,
      config['files'])

  l = len(config['files'])
  if l == 0:
    print '!Warning! file set is empty'
  else:
    print l, 'files found!'

  uploader = Uploader(config)
  if uploader.login():
    uploader.post()
