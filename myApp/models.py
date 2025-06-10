from django.db import models

# Create your models here.
class BookList(models.Model):
    id = models.AutoField("id", primary_key=True)
    #书籍编号
    bookId = models.CharField("bookId", max_length=255, default='')
    #类型
    tag = models.CharField("tag", max_length=255, default='')
    #书名
    title = models.CharField("title", max_length=255, default='')
    #封面
    cover = models.CharField("cover", max_length=2555, default='')
    #作者
    author = models.CharField("author", max_length=255, default='')
    #出版社
    press = models.CharField("press", max_length=255, default='')
    #出版年份
    year = models.CharField("year", max_length=255, default='')

    pageNum = models.CharField("pageNum", max_length=255, default='')
    price = models.CharField("price", max_length=255, default='')
    #评分
    rate = models.CharField("rate", max_length=255, default='')
    #星级列表
    startList = models.CharField("startList", max_length=255, default='')
    summary = models.TextField("summary", default='')
    #详情链接
    detailLink = models.CharField("detailLink", max_length=255, default='')

    createTime = models.CharField("createTime", max_length=2555, default='')
    #评论数量
    comment_len = models.CharField("comment_len", max_length=255, default='')
    #评论列表
    commentList = models.TextField("commentList", default='')

    class Meta:
        db_table = "booklist"


class User(models.Model):
    id = models.AutoField("id",primary_key=True)
    username = models.CharField("user",max_length=255,default='')
    password = models.CharField("password",max_length=255,default='')
    createTime = models.DateField("createTime",auto_now_add=True)

    class Meta:
        db_table = "user"
