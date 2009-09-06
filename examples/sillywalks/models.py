from django.db import models
from django.template.defaultfilters import slugify

class SillyWalk(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    video_url = models.URLField()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(SillyWalk, self).save(*args, **kwargs)
