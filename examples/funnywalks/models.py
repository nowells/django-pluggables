from django.db import models

class FunnyWalk(models.Model):
    description = models.TextField()
    video_url = models.URLField()

    def __unicode__(self):
        return self.description
