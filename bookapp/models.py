from django.db import models


# Create your models here.
# 表类写好后点最上面一栏的工具找到manage.py,打开后输入makemigrations后按回车再输入migrate(如果需要新增列需要在参数后加--fake)
class Ebook(models.Model):
    id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=100)
    autor = models.CharField(max_length=100)
    translator = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    publisher_data = models.CharField(max_length=100)
    price = models.CharField(max_length=20)
    rating_nums = models.CharField(max_length=10)
    rating_people = models.CharField(max_length=10)
    comment = models.CharField(max_length=200)
    book_num = models.CharField(max_length=20)
    is_published = models.BooleanField(default=False)


class BookComment(models.Model):
    reader = models.CharField(max_length=255)
    star = models.CharField(max_length=255)
    time = models.CharField(max_length=255)
    short_comm = models.TextField()
    read_img = models.CharField(max_length=255)
    book_img = models.CharField(max_length=255)
    ebook = models.ForeignKey(to="Ebook", to_field="id", on_delete=models.CASCADE)
    percent_type = models.CharField(max_length=255)
