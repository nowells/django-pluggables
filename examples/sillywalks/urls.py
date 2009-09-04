from django.conf import settings
from django.conf.urls.defaults import url, include, patterns, handler404, handler500
from django.contrib import admin

from sillywalks import views

admin.autodiscover()

urlpatterns = patterns('',
    url('^sillywalks/$', views.index, name='sillywalks_index'),
    url('^sillywalks/(?P<walk_name>[\w\-_]+)/$', views.view, name='sillywalks_view'),
    url('^sillywalks/(?P<walk_name>[\w\-_]+)/complaints/', include(views.complaints)),
)

urlpatterns += patterns('',
    url('^django-admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += patterns('', (r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}))
