from django.conf import settings
from django.conf.urls.defaults import url, include, patterns, handler404, handler500

from complaints.urls import Complaints

class SillyWalkComplaints(Complaints):
    def get_config(self, request, walk_name=None):
        return {
            'base_template': 'base.html'
            }

urlpatterns = patterns('',
    url('^sillywalks/$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
    url('^sillywalks/(?P<walk_name>\w+)/$', 'django.views.generic.simple.direct_to_template', {'template': 'view.html'}),
    url('^sillywalks/(?P<walk_name>\w+)/complaints/', include(SillyWalkComplaints())),
)

if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += patterns('', (r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}))
