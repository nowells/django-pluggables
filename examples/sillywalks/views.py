from django.core.urlresolvers import resolve, reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from complaints.views import ComplaintsApp
from sillywalks.forms import SillyWalkForm
from sillywalks.models import SillyWalk

def index(request):
    sillywalks = SillyWalk.objects.all()
    return render_to_response('sillywalks/index.html', {
        'sillywalks': sillywalks,
        }, context_instance=RequestContext(request))

def view(request, walk_slug):
    return complaints_app.index(request, walk_slug=walk_slug)

def edit(request, walk_slug=None):
    try:
        sillywalk = SillyWalk.objects.get(slug=walk_slug)
    except SillyWalk.DoesNotExist:
        sillywalk = None

    if request.method == 'POST':
        form = SillyWalkForm(request.POST, instance=sillywalk)
        if form.is_valid():
            sillywalk = form.save()
            return HttpResponseRedirect(reverse('sillywalks_view', args=[sillywalk.slug]))
    else:
        form = SillyWalkForm(instance=sillywalk)

    return render_to_response('sillywalks/edit.html', {
        'sillywalk': sillywalk,
        'form': form,
        }, context_instance=RequestContext(request))

def delete(request, walk_slug):
    try:
        sillywalk = SillyWalk.objects.get(slug=walk_slug)
    except SillyWalk.DoesNotExist:
        raise Http404

    sillywalk.delete()

    return HttpResponseRedirect(reverse('sillywalks_index'))

class SillyWalkComplaintsApp(ComplaintsApp):
    def pluggable_config(self, request, walk_slug=None):
        return {'base_template': 'sillywalks/view.html'}

    def pluggable_view_context(self, request, walk_slug):
        try:
            sillywalk = SillyWalk.objects.get(slug=walk_slug)
        except SillyWalk.DoesNotExist:
            raise Http404
        return sillywalk

    def pluggable_template_context(self, request, walk_slug):
        return {'sillywalk': request.pluggable.view_context}

complaints_app = SillyWalkComplaintsApp('sillywalks')
