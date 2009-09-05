from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from complaints.forms import ComplaintForm
from complaints.models import Complaint

from pluggables import PluggableViews, url, include, patterns, pluggable_reverse

class Complaints(PluggableViews):
    urlpatterns = patterns('',
        url(r'^$', 'index', name='complaints_index'),
        url(r'^create/$', 'edit', name='complaints_create'),
        url(r'^(?P<complaint_id>\d+)/edit/$', 'edit', name='complaints_edit'),
    )

    def index(self, request):
        complaints = Complaint.objects.pluggable(request)
        form = ComplaintForm()
        return render_to_response(request.pluggable.config.get('template', 'complaints/index.html'), {
            'complaints': complaints,
            'form': form,
            'base_template': request.pluggable.config.get('base_template', 'base.html'),
            }, context_instance=RequestContext(request))

    def edit(self, request, complaint_id=None):
        if complaint_id is not None:
            try:
                complaint = Complaint.objects.pluggable(request).get(pk=complaint_id)
            except Complaint.DoesNotExist:
                raise Http404
        else:
            complaint = None

        if request.method == 'POST':
            form = ComplaintForm(request.POST, instance=complaint)
            if form.is_valid():
                complaint = form.save(commit=False)
                complaint.set_pluggable_url(request)
                complaint.save()
                return HttpResponseRedirect(pluggable_reverse(request, 'complaints_index'))
        else:
            form = ComplaintForm(instance=complaint)

        return render_to_response(request.pluggable.config.get('template', 'complaints/edit.html'), {
            'form': form,
            'base_template': request.pluggable.config.get('base_template', 'base.html'),
            }, context_instance=RequestContext(request))
