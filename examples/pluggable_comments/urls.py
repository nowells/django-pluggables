from django.conf.urls.defaults import url, include, patterns, handler404, handler500
import pluggables

class Comments(pluggables.Pluggable):
    urlpatterns = pluggables.patterns('',
        pluggables.url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'test.html'}),
    )

urlpatterns = patterns('',
    url('^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
    url('^(?P<name>\w+)/test/', include(Comments())),
)
