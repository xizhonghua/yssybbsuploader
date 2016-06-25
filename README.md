# YSSY BBS Uploader

### Features
* Upload images/files to [YSSY BBS](https://bbs.sjtu.edu.cn)
* Post with content and links to all uploaded files
* Auto resize images with filesize > 1MB

### Usage
```
./bbsupload.py [options] [file1 file2 file3...]
```

### Accounts
To prevent credential leakage, account is load from a json file (default is account.json) in following format
```
{
  "id": "your_id",
  "pw": "your_pw"
}
```

### Options
```
  -a, --account   account filename. default is "account.json"
  -b, --board:    board to upload/post. default is "PPPerson"
  -t, --title:    post title. default is "noname"
  -c, --content:  content of the post. default is empty
  -n, --no-ad:    post without ad
  -s:             use single thread. default uses 4 threads
  -u, --up-only   upload only, do not post
  -h, --help:     print usage
```

### Example
```
./bbsupload.py -b test -t "中文标题" -c "中文内容" ~/Pictures/*.jpg
```

### Dependencies
* python2.7 ?
* [requests](http://docs.python-requests.org/en/master/)
* [Pillow](http://pillow.readthedocs.org/en/3.1.x/index.html)

### TODO
* (done) auto resize large image 
* (done) multi-thread uploading

### Contact
* Zhonghua Xi (xxfflower@YSSY)
* xizhonghua (at) gmail.com
