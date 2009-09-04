from pluggables import Pluggable, url, include, patterns

class Complaints(Pluggable):
    urlpatterns = patterns('',
        url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'complaints/index.html'}),
        url(r'^create/$', 'django.views.generic.simple.direct_to_template', {'template': 'complaints/edit.html'}),
        url(r'^(?P<complaint_id>\d+)/edit/$', 'django.views.generic.simple.direct_to_template', {'template': 'complaints/edit.html'}),
    )

urlpatterns = Complaints()
