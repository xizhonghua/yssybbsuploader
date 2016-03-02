#!/usr/bin/env python

################################################
# Author: Zhonghua Xi (xxfflower@YSSY)
# Email: xizhonghua (AT) gmail.com
################################################

import json
import re
import sys
from requests import Request, Session


def upload_file(s, headers, payload, filename):
  files = {
      'up': open(filename, 'rb')
  }

  resp = s.post('https://bbs.sjtu.edu.cn/bbsdoupload',
                headers=headers,
                files=files,
                data=payload)

  m = re.search(r"<font color=green>([^<]+)", resp.text)

  return m.groups()[0]


def post(config):
  s = Session()

  headers = {
      'Origin': 'https://bbs.sjtu.edu.cn',
      'Referer': 'https://bbs.sjtu.edu.cn/file/bbs/index/index.htm',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
  }

  resp = s.post('https://bbs.sjtu.edu.cn/bbslogin',
                data={
                    'id': config['id'],
                    'pw': config['pw']
                },
                headers=headers)

  if 'utmpuserid' in s.cookies.get_dict():
    print 'Logged in with id:', config['id']
  else:
    print 'Failed to login with id:', config['id']
    return

  payload = {
      'board': config['board'],
      'title': config['title'].decode('utf-8').encode('gb2312'),
      'signature': 1,
      'autocr': 'on',
      'text': 'content',
      'level': 0,
      'live': 180,
  }

  print 'board   =', config['board']
  print 'title   =', config['title']
  print 'content =', config['content']

  full_content = config['content'].decode('utf-8')
  # upload files
  for filename in config['files']:
    print 'uploading', filename, 'to', config['board']
    fileurl = upload_file(s, headers, payload, filename)
    print 'done', fileurl
    full_content += fileurl + '\n'

  if config['ad'] == True:
    full_content += 'Post by bbsupload.py ver: ' + config['version']

  payload['text'] = full_content.encode('gb2312')

  resp = s.post(
      'https://bbs.sjtu.edu.cn/bbssnd',
      headers=headers,
      data=payload)

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
  print '  -a, --account  ', 'account filename. default is account.json'
  print '  -b, --board:   ', 'board to upload/post'
  print '  -t, --title:   ', 'post title'
  print '  -c, --content: ', 'content of the post'
  print '  -n, --no-ad:   ', 'post without ad'
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
      'version': '0.2'
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

  l = len(config['files'])
  if l == 0:
    print '!Warning! file set is empty'
  else:
    print l, 'files found!'

  post(config)
