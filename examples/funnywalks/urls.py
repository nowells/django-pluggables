from django.conf.urls.defaults import url, include, patterns, handler404, handler500
from complaints.urls import Complaints

urlpatterns = patterns('',
    url('^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
    url('^(?P<funnywalk_id>\d+)/complaints/', include(Complaints())),
)
