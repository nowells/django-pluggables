from django.contrib import admin
from sillywalks.models import SillyWalk

class SillyWalkAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(SillyWalk, SillyWalkAdmin)
