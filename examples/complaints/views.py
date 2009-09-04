from django.template import RequestContext
from django.shortcuts import render_to_response

from complaints.forms import ComplaintForm
from complaints.models import Complaint

def index(request):
    return render_to_response('complaints/index.html', {
        }, context_instance=RequestContext(request))

def edit(request, complaint_id=None):
    try:
        complaint = Complaint.objects.get(pk=complaint_id)
    except:
        complaint = None

    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
    else:
        form = ComplaintForm(instance=complaint)

    return render_to_response('complaints/edit.html', {
        'form': form,
        'base_template': request.pluggable.config.get('base_template', 'base.html'),
        }, context_instance=RequestContext(request))
