from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Post(models.Model):
    #title名 30文字まで
    title = models.CharField(max_length=30)
    #内容
    content = models.TextField()
    #作成日
    created = models.DateTimeField()
    #作成者
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def  __str__(self):
        return '{}::{}'.format(self.title, self.author)


