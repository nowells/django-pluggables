from django.db import models
from pluggables.models import PluggableModel

class Complaint(PluggableModel):
    description = models.TextField()

    def __unicode__(self):
        return self.description
