from django.db import models

class Complaint(models.Model):
    description = models.TextField()

    def __unicode__(self):
        return self.description
