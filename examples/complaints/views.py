from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from complaints.forms import ComplaintForm
from complaints.models import Complaint
from pluggables import pluggable_reverse

def index(request):
    return render_to_response('complaints/index.html', {
        }, context_instance=RequestContext(request))

def edit(request, complaint_id=None):
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
            return HttpResponseRedirect(pluggable_reverse(request, 'complaints_edit', kwargs={'complaint_id': complaint.id}))
    else:
        form = ComplaintForm(instance=complaint)

    return render_to_response('complaints/edit.html', {
        'form': form,
        'base_template': request.pluggable.config.get('base_template', 'base.html'),
        }, context_instance=RequestContext(request))
