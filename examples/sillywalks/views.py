from django.core.urlresolvers import resolve
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from complaints.views import Complaints
from sillywalks.models import SillyWalk

def index(request):
    sillywalks = SillyWalk.objects.all()
    return render_to_response('sillywalks/index.html', {
        'sillywalks': sillywalks,
        }, context_instance=RequestContext(request))

def view(request, walk_name):
    return complaints.index(request, walk_name=walk_name)

class SillyWalkComplaints(Complaints):
    def pluggable_config(self, request, walk_name=None):
        return {'base_template': 'sillywalks/view.html'}

    def pluggable_view_context(self, request, walk_name):
        try:
            sillywalk = SillyWalk.objects.get(name=walk_name)
        except SillyWalk.DoesNotExist:
            raise Http404
        return sillywalk

    def pluggable_template_context(self, request, walk_name):
        return {'sillywalk': request.pluggable.view_context}

complaints = SillyWalkComplaints('sillywalks')
