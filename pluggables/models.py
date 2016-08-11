from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.http import HttpRequest
from pluggables.utils.picklefield import PickledObjectField


class PluggableManager(models.Manager):
    def pluggable(self, request):
        return self.filter(pluggable_url=request.pluggable.pluggable_url_data)


class PluggableModel(models.Model):
    pluggable_url = PickledObjectField(blank=True)

    objects = PluggableManager()

    def save(self, request, *args, **kwargs):
        if request:
            self.pluggable_url = request.pluggable.pluggable_url_data
        super(PluggableModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class PluggableObjectManager(PluggableManager):
    def pluggable_object(self, request):
        if request.pluggable.view_context is None:
            return self.filter(pluggable_content_type__isnull=True, pluggable_object_id__isnull=True)
        else:
            content_type = ContentType.objects.get_for_model(request.pluggable.view_context)
            return self.filter(pluggable_content_type=content_type, pluggable_object_id=request.pluggable.view_context.pk)


class PluggableObjectModel(PluggableModel):
    pluggable_content_type = models.ForeignKey(ContentType, null=True, blank=True)
    pluggable_object_id = models.PositiveIntegerField(null=True, blank=True)

    pluggable_object = GenericForeignKey(fk_field='pluggable_object_id', ct_field='pluggable_content_type')

    objects = PluggableObjectManager()

    def save(self, request, *args, **kwargs):
        if request:
            self.pluggable_object = request.pluggable.view_context
        super(PluggableObjectModel, self).save(request, *args, **kwargs)

    class Meta:
        abstract = True
