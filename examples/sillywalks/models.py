from django.db import models

class SillyWalk(models.Model):
    description = models.TextField()
    video_url = models.URLField()

    def __unicode__(self):
        return self.description
