from django.core.urlresolvers import resolve
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from complaints.urls import Complaints
from sillywalks.models import SillyWalk

def index(request):
    sillywalks = SillyWalk.objects.all()
    return render_to_response('index.html', {
        'sillywalks': sillywalks,
        }, context_instance=RequestContext(request))

def view(request, walk_name):
    request.path_info = '%scomplaints/' % request.path_info
    func, args, kwargs = resolve(request.path_info)
    return func(request, *args, **kwargs)

class SillyWalkComplaints(Complaints):
    def get_template_context(self, request, walk_name):
        try:
            sillywalk = SillyWalk.objects.get(name=walk_name)
        except SillyWalk.DoesNotExist:
            raise Http404
        return {
            'sillywalk': sillywalk
            }

    def get_config(self, request, walk_name=None):
        return {
            'base_template': 'view.html'
            }

complaints = SillyWalkComplaints('sillywalks')
