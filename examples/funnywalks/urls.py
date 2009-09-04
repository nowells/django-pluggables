from django.conf import settings
from django.conf.urls.defaults import url, include, patterns, handler404, handler500

from complaints.urls import Complaints

class FunnyWalkComplaints(Complaints):
    def get_config(self, funnywalk_id=None):
        return {
            'base_template': 'base.html'
            }

urlpatterns = patterns('',
    url('^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
    url('^(?P<funnywalk_id>\d+)/complaints/', include(FunnyWalkComplaints())),
)

if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += patterns('', (r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}))
