from pluggables import Pluggable, url, include, patterns

from complaints import views

class Complaints(Pluggable):
    urlpatterns = patterns('',
        url(r'^$', views.index),
        url(r'^create/$', views.edit),
        url(r'^(?P<complaint_id>\d+)/edit/$', views.edit),
    )

urlpatterns = Complaints()
