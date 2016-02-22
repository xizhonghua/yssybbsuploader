# yssybbsuploader

### Features
* Upload images/files to [YSSY BBS](https://bbs.sjtu.edu.cn)
* Post with content and links to all uploaded files

### Usage
```
./bbsupload.py -i id -p pw [options] [file1 file2 file3 ...] 
```

### Options
```
-i, --id:       bbs id
-p, --pw:       bbs password
-b, --board:    board to upload/post
-t, --title:    post title
-c, --content:  content of the post
-n, --no-ad:    post without ad
```

### Example
```
./bbsupload.py -i your_id -p your_pwd -b PPPerson -t test -c "test of new tool" ~/Pictures/jpeg_full/wanzi/*small*.jpg
```
