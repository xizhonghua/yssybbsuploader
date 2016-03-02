# yssybbsuploader

### Features
* Upload images/files to [YSSY BBS](https://bbs.sjtu.edu.cn)
* Post with content and links to all uploaded files

### Usage
```
./bbsupload.py [options] [file1 file2 file3...]
```

### Accounts
To prevent credential leakage, account is load from a json file (default is account.json) in following format
```
{
  "id": "your_id",
  "pw": "your_pd"
}
```

### Options
```
  -a, --account   account filename. default is "account.json"
  -b, --board:    board to upload/post. default is "PPPerson"
  -t, --title:    post title. default is "noname"
  -c, --content:  content of the post. default is empty
  -n, --no-ad:    post without ad
  -h, --help:     print usage
```

### Example
```
./bbsupload.py -b test -t "中文标题" -c "中文内容" ~/Pictures/*.jpg
```

### Dependencies
* python2.7 ?
* [requests](http://docs.python-requests.org/en/master/)

### TODO
* auto resize large image
