"""
A tool for allowing reusable apps to exist at multiple URLs within a project.

.. autosummary::
   :template: autosummary_module
   :toctree:

   templatetags.pluggable

"""
from functools import wraps
import uuid
import copy

from django.conf import settings
from django.conf.urls import defaults
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import resolve, reverse, RegexURLPattern, get_callable, get_mod_func
from django.core.exceptions import ViewDoesNotExist
from django.http import Http404

def url(*args, **kwargs):
    return list(args), kwargs

def patterns(*args):
    return list(args)

def include(url_module):
    return [url_module]

def pluggable_view(func, pluggable, decorators):
    @wraps(func)
    def view_wrapper(request, *args, **kwargs):
        request.pluggable = PluggableView(pluggable, request, *args, **kwargs)
        new_args, new_kwargs = request.pluggable.get_remapped_args(func, request)
        return func(request, *new_args, **new_kwargs)

    for decorator in decorators:
        view_wrapper = decorator(view_wrapper)
    return view_wrapper

def pluggable_create_view(func):
    func.pluggable_create_view = True
    return func

def pluggable_placeholder(*args, **kwargs):
    raise Http404

class PluggableView(object):
    def __init__(self, pluggable, request, *args, **kwargs):
        self.pluggable = pluggable
        self.prefix = pluggable.prefix
        self.unique_identifier = pluggable.unique_identifier
        self.pluggable_object = None
        self.args = args
        self.kwargs = kwargs
        original_func, self.base_args, self.base_kwargs = resolve('%s%s' % (request.path_info, self.unique_identifier))
        self.args =  list(self.args[len(self.base_args):])
        self.kwargs = dict([ (x[0], x[1]) for x in self.kwargs.items() if x[0] not in self.base_kwargs ])

    def get_remapped_args(self, func, request):
        if not getattr(self, '_remapped', False):
            self._remapped = True
            if not getattr(func, 'pluggable_create_view', False):
                try:
                    self.pluggable_object = self.pluggable.get_object(request, *self.base_args, **self.base_kwargs)
                    extra_args, extra_kwargs = self.pluggable.get_extra_args(request, self.pluggable_object, *self.base_args, **self.base_kwargs)
                except ObjectDoesNotExist:
                    raise Http404
                self.args = [self.pluggable_object] + list(extra_args) + self.args
                self.kwargs.update(extra_kwargs)
        return self.args, self.kwargs

class Pluggable(object):
    urlpatterns = ('', )

    def __init__(self, prefix, decorators=None):
        self.unique_identifier = '/@@pluggableapp@@/%s/' % str(uuid.uuid4())
        self.prefix = prefix
        self.urlpatterns = copy.deepcopy(self.urlpatterns)
        decorators = decorators is not None and decorators or []
        view_prefix = self.urlpatterns[0]
        urlpatterns = []
        for pattern in self.urlpatterns[1:]:
            pattern_args, pattern_kwargs = pattern
            view = pattern_args[1]
            if type(view) == list:
                raise Exception("Pluggable applications do not support 'include(...)' url definitions.")

            if callable(view):
                _callback = view
            else:
                view = view_prefix and '%s.%s' % (view_prefix, view) or view
                try:
                    _callback = get_callable(view)
                except ImportError, e:
                    mod_name, _ = get_mod_func(view)
                    raise ViewDoesNotExist, "Could not import %s. Error was: %s" % (mod_name, str(e))
                except AttributeError, e:
                    mod_name, func_name = get_mod_func(view)
                    raise ViewDoesNotExist, "Tried %s in module %s. Error was: %s" % (func_name, mod_name, str(e))

            pattern_args[1] = pluggable_view(_callback, self, decorators)

            if 'name' in pattern_kwargs:
                pattern_kwargs['name'] = '%s%s' % (prefix and '%s_' % prefix or '', pattern_kwargs['name'])

            urlpatterns.append(defaults.url(*pattern_args, **pattern_kwargs))
        urlpatterns.append(defaults.url(r'^.*%s$' % self.unique_identifier, pluggable_placeholder))
        self.urlpatterns = defaults.patterns('', *urlpatterns)

    def __iter__(self):
        return self.urlpatterns.__iter__()

    def __getitem__(self, index):
        return self.urlpatterns[index]

    def __len__(self):
        return len(self.urlpatterns)

    def context_processor(self, request):
        return {}

    def get_object(self, request, *args, **kwargs):
        return None

    def get_extra_args(self, request, *args, **kwargs):
        return ((), {})

def pluggable_context_processor(request):
    if hasattr(request, 'pluggable'):
        context = request.pluggable.pluggable.context_processor(request)
        context.update({'pluggable_object': request.pluggable.pluggable_object})
        return context
    return {}

def pluggable_reverse(request, view_name, urlconf=None, args=None, kwargs=None, prefix=None):
    args = args or []
    kwargs = kwargs or {}

    if hasattr(request, 'pluggable'):
        view_name = request.pluggable.prefix and '%s_%s' % (request.pluggable.prefix, view_name) or '%s' % view_name
        if request.pluggable.base_args:
            args = request.pluggable.base_args + args

        if request.pluggable.base_kwargs:
            kwargs.update(request.pluggable.base_kwargs)
    return reverse(view_name, urlconf, args, kwargs, prefix)
