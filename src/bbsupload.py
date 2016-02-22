#!/usr/bin/env python

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
    print 'Logged in!'
  else:
    print 'Failed to login!', resp.text.encode('gb2312')

  payload = {
      'board': config['board'],
      'title': config['title'],
      'signature': 1,
      'autocr': 'on',
      'text': 'content',
      'level': 0,
      'live': 180,
  }

  full_content = config['content'] + '\n'

  # upload files
  for filename in config['files']:
    print 'uploading', filename, 'to', config['board']
    fileurl = upload_file(s, headers, payload, filename)
    print 'done', fileurl
    full_content += fileurl + '\n'

  if config['ad'] == True:
    full_content += 'Posted by upload.py'

  payload['text'] = full_content

  resp = s.post(
      'https://bbs.sjtu.edu.cn/bbssnd',
      headers=headers,
      data=payload)

  print 'Posting...'
  if resp.status_code == 200:
    print 'Posted!'
  else:
    print 'Error! Failed to post'


def print_usage(argv):
  print 'Usage:', argv[0], '-i id -p pw [options] file1 file2 file3...'
  print 'Options:'
  print '  -i, --id:      ', 'bbs id'
  print '  -p, --pw:      ', 'bbs password'
  print '  -b, --board:   ', 'board to upload/post'
  print '  -t, --title:   ', 'post title'
  print '  -c, --content: ', 'content of the post'
  print '  -n, --no-ad:   ', 'post without ad'

if __name__ == '__main__':
  config = {
      'id': None,
      'pw': None,
      'board': 'PPPerson',
      'title': 'noname',
      'content': '',
      'files': [],
      'ad': True
  }
  index = 1
  while index < len(sys.argv):
    arg = sys.argv[index]
    if arg == '--id' or arg == '-i':
      index += 1
      config['id'] = sys.argv[index]
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
    else:
      config['files'].append(arg)
    index += 1

  if config['id'] is None or config['pw'] is None:
    print '!Error! id or pw is null'
    print_usage(sys.argv)
    sys.exit(-1)

  l = len(config['files'])
  if l == 0:
    print '!Warning! file set is empty'
  else:
    print l, 'files found!'

  post(config)
