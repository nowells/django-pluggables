from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from complaints.forms import ComplaintForm
from complaints.models import Complaint

def index(request):
    complaints = Complaint.objects.pluggable_object(request)
    form = ComplaintForm()
    return render_to_response(request.pluggable.config.get('template', 'complaints/index.html'), {
        'complaints': complaints,
        'form': form,
        'base_template': request.pluggable.config.get('base_template', 'base.html'),
        }, context_instance=RequestContext(request))

def edit(request, complaint_id=None):
    if complaint_id is not None:
        try:
            complaint = Complaint.objects.pluggable_object(request).get(pk=complaint_id)
        except Complaint.DoesNotExist:
            raise Http404
    else:
        complaint = None

    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint = form.save(request)
            return HttpResponseRedirect(pluggable_reverse(request, 'complaints_index'))
    else:
        form = ComplaintForm(instance=complaint)

    return render_to_response(request.pluggable.config.get('template', 'complaints/edit.html'), {
        'form': form,
        'base_template': request.pluggable.config.get('base_template', 'base.html'),
        }, context_instance=RequestContext(request))

def delete(request, complaint_id):
    try:
        complaint = Complaint.objects.pluggable_object(request).get(pk=complaint_id)
    except Complaint.DoesNotExist:
        raise Http404

    complaint.delete()

    return HttpResponseRedirect(pluggable_reverse(request, 'complaints_index'))
