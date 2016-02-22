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


def post(username, password, board, title, content, files=[]):
  s = Session()

  headers = {
      'Origin': 'https://bbs.sjtu.edu.cn',
      'Referer': 'https://bbs.sjtu.edu.cn/file/bbs/index/index.htm',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
  }

  resp = s.post('https://bbs.sjtu.edu.cn/bbslogin',
                data={
                    'id': username,
                    'pw': password
                },
                headers=headers)

  if 'utmpuserid' in s.cookies.get_dict():
    print 'Logged in!'
  else:
    print 'Failed to login!', resp.text.encode('gb2312')

  payload = {
      'board': board,
      'title': title,
      'signature': 1,
      'autocr': 'on',
      'text': 'content',
      'level': 0,
      'live': 180,
  }

  full_content = content + '\n'

  for filename in files:
    print 'uploading', filename
    fileurl = upload_file(s, headers, payload, filename)
    print 'done', fileurl
    full_content += fileurl + '\n'

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
  print 'Usage:', './' + argv[0], '-i id -p pw [options] file1 file2 ...'

if __name__ == '__main__':
  id = None
  pw = None
  board = 'PPPerson'
  title = 'noname'
  files = []
  for index, arg in enumerate(sys.argv):
    if arg == '--id' or arg == '-i':
      id = sys.argv[index + 1]
    elif arg == '--pw' or arg == '-p':
      pw = sys.argv[index + 1]
    elif arg == '--board' or arg == '-b':
      board = sys.argv[index + 1]
    elif arg == '--title' or arg == '-t':
      title = sys.argv[index + 1]
    elif arg == '--content' or arg == '-c':
      content = sys.argv[content]
    else:
      files.append(arg)

    if id is None or pw is None:
      print '!Error! id or pw is null'
      print_usage(sys.argv)
      sys.exit(-1)

    if len(files) == 0:
      print '!Error! file set is empty'
      print_usage(sys.argv)
      sys.exit(-1)

    post(id, pw, board, title, content, files)
