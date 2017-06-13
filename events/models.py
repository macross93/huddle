from __future__ import unicode_literals
from django.db import models

class charity(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField(max_length=400)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class user(models.Model):
    first_name = models.CharField(blank=True, max_length=25)
    last_name = models.CharField(blank=True, max_length=25)
    facebook_id = models.CharField(max_length=20)

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class charitycontact(models.Model):
    first_name = models.CharField(blank=True, max_length=25)
    last_name = models.CharField(blank=True, max_length=25)
    facebook_id = models.CharField(max_length=20)

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)

class event(models.Model):
    name = models.CharField(max_length=50)
    details = models.TextField(max_length=400)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=60)
    postcode = models.CharField(max_length=10)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField(blank=True)
    charity = models.ForeignKey(charity)
    image = models.ImageField(upload_to = 'photos/%Y/%m/%d/%s', default = 'pic_folder/None/no-img.jpg', blank=True)
    volunteer = models.CharField(max_length=30, blank=True, null=True)
    confirmed = models.CharField(max_length=1, default="n")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

# Create your models here.
