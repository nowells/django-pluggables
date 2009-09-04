from pluggables import Pluggable, url, include, patterns

from complaints import views

class Complaints(Pluggable):
    urlpatterns = patterns('',
        url(r'^$', views.index, name='complaints_index'),
        url(r'^create/$', views.edit, name='complaints_create'),
        url(r'^(?P<complaint_id>\d+)/edit/$', views.edit, name='complaints_edit'),
    )

urlpatterns = Complaints()
