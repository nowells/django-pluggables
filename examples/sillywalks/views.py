from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from complaints.urls import Complaints
from sillywalks.models import SillyWalk

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

complaints = SillyWalkComplaints()

def view(request, walk_name):
    return render_to_response(
        'view.html',
        complaints.get_template_context(request, walk_name),
        context_instance=RequestContext(request)
        )
