from pluggables import Pluggable, url, include, patterns

from complaints import views

class Complaints(Pluggable):
    urlpatterns = patterns('',
        url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'complaints/index.html'}),
        url(r'^create/$', views.edit),
        url(r'^(?P<complaint_id>\d+)/edit/$', views.edit),
    )

urlpatterns = Complaints()
