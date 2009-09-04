from django.db import models
from django.contrib import admin

class SillyWalk(models.Model):
    name = models.SlugField(unique=True)
    description = models.TextField()
    video_url = models.URLField()

    def __unicode__(self):
        return self.name

admin.site.register(SillyWalk)
