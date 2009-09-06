from django.contrib import admin
from django.db import models

from pluggables.models import PluggableModel

class Complaint(PluggableModel):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __unicode__(self):
        return self.description

admin.site.register(Complaint)
