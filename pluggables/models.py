from django.db import models
from django.http import HttpRequest
from pluggables.utils.picklefield import PickledObjectField

class PluggableManager(models.Manager):
    def pluggable(self, request):
        return self.filter(pluggable_url=request.pluggable.pluggable_url_data)

class PluggableModel(models.Model):
    def __init__(self, *args, **kwargs):
        if len(args) >= 1 and isinstance(args[0], HttpRequest):
            self.set_pluggable_url(args[0])
            args = args[1:]
        super(PluggableModel, self).__init__(*args, **kwargs)

    pluggable_url = PickledObjectField(blank=True)

    objects = PluggableManager()

    def set_pluggable_url(self, request):
        if request and hasattr(request, 'pluggable'):
            self.pluggable_url = request.pluggable.pluggable_url_data

    class Meta:
        abstract = True
