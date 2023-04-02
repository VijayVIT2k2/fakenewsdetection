from django.db import models

class News(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    prediction = models.CharField(max_length=255, blank=True, null=True)

class Auth(models.Model):
    username = models.TextField()
    password = models.TextField()