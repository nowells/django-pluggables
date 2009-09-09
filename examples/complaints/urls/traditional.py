from pluggables import PluggableApp, url, include, patterns

class ComplaintsApp(PluggableApp):
    urlpatterns = patterns('complaints.views.traditional',
        url(r'^$', 'index', name='complaints_index'),
        url(r'^create/$', 'edit', name='complaints_create'),
        url(r'^(?P<complaint_id>\d+)/edit/$', 'edit', name='complaints_edit'),
        url(r'^(?P<complaint_id>\d+)/delete/$', 'delete', name='complaints_delete'),
    )
