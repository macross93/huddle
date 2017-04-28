from __future__ import unicode_literals

from django.db import models

class Charity(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField(max_length=400)
    website = models.URLField()
    email = models.EmailField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class User(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    facebook_id = models.CharField(max_length=20)

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class CharityContact(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    facebook_id = models.CharField(max_length=20)

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)

class Event(models.Model):
    name = models.CharField(max_length=50)
    details = models.TextField(max_length=400)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=60)
    postcode = models.CharField(max_length=10)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField()
    charity = models.ForeignKey(Charity)
    volunteer = models.ForeignKey(User)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

# Create your models here.
