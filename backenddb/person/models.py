from django.db import models

class Person(models.Model):
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    profile = models.CharField(max_length=64)

class Face(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    picture = models.ImageField(upload_to ='uploads/')
    include_in_learning_db = models.BooleanField(default=True)