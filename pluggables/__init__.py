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

def patterns(*args):
    return args

def url(*args, **kwargs):
    return 'url', list(args), kwargs,

def include(*args, **kwargs):
    return 'include', list(args), kwargs,

def pluggable_view(func, pluggable):
    @wraps(func)
    def view_wrapper(request, *args, **kwargs):
        request.pluggable = PluggableView(pluggable, request, *args, **kwargs)
        pluggable_args, pluggable_kwargs = request.pluggable.pluggable_arguments
        return func(request, *pluggable_args, **pluggable_kwargs)
    return view_wrapper

def pluggable_placeholder(*args, **kwargs):
    raise Http404

class PluggableView(object):
    def __init__(self, pluggable_object, request, *args, **kwargs):
        # Public Data
        self.config = {}
        self.view_context = {}
        self.template_context = {}

        # Pluggable Configuration
        self.__pluggable_object = pluggable_object
        self.prefix = self.__pluggable_object.prefix

        # Parent and Pluggable function args/kwargs.
        _, self.__parent_args, self.__parent_kwargs = resolve('%s%s' % (request.path_info, self.__pluggable_object.unique_identifier))
        self.__pluggable_args = list(args[len(self.__parent_args):])
        self.__pluggable_kwargs = dict([ (x[0], x[1]) for x in kwargs.items() if x[0] not in self.__parent_kwargs ])

        # Generate the pluggable config/context
        self.view_context = self.__pluggable_object.get_view_context(request, *self.__parent_args, **self.__parent_kwargs)
        self.template_context = self.__pluggable_object.get_template_context(request, *self.__parent_args, **self.__parent_kwargs)
        self.config = self.__pluggable_object.get_config(request, *self.__parent_args, **self.__parent_kwargs)

    @property
    def pluggable_arguments(self):
        return self.__pluggable_args, self.__pluggable_kwargs

    @property
    def parent_arguments(self):
        return self.__parent_args, self.__parent_kwargs

class Pluggable(object):
    urlpatterns = patterns('', )

    def __init__(self, prefix=None):
        self.unique_identifier = '/@@pluggableapp@@/%s/' % str(uuid.uuid4())
        self.prefix = prefix
        self.urlpatterns = copy.deepcopy(self.urlpatterns)
        view_prefix = self.urlpatterns[0]
        urlpatterns = []
        for pattern in self.urlpatterns[1:]:
            pattern_type, pattern_args, pattern_kwargs = pattern
            if pattern_type == 'url':
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

                pattern_args[1] = pluggable_view(_callback, self)

                if 'name' in pattern_kwargs:
                    pattern_kwargs['name'] = '%s%s' % (prefix and '%s_' % prefix or '', pattern_kwargs['name'])

                urlpatterns.append(defaults.url(*pattern_args, **pattern_kwargs))
            elif pattern_type == 'include':
                urlpatterns.append(defaults.include(*pattern_args, **pattern_kwargs))
            else:
                raise Exception('Invalid url pattern type.')
        urlpatterns.append(defaults.url(r'^.*%s$' % self.unique_identifier, pluggable_placeholder))
        self.urlpatterns = defaults.patterns('', *urlpatterns)

    def __iter__(self):
        return self.urlpatterns.__iter__()

    def __getitem__(self, index):
        return self.urlpatterns[index]

    def __len__(self):
        return len(self.urlpatterns)

    def get_view_context(self, request, *args, **kwargs):
        return None

    def get_template_context(self, request, *args, **kwargs):
        return {}

    def get_config(self, request, *args, **kwargs):
        return {}

def pluggable_context_processor(request):
    if hasattr(request, 'pluggable'):
        return request.pluggable.template_context
    return {}

def pluggable_reverse(request, view_name, urlconf=None, args=None, kwargs=None, prefix=None):
    args = args or []
    kwargs = kwargs or {}

    if hasattr(request, 'pluggable'):
        view_name = request.pluggable.prefix and '%s_%s' % (request.pluggable.prefix, view_name) or '%s' % view_name
        parent_args, parent_kwargs = request.pluggable.parent_arguments()
        if parent_args:
            args = parent_args + args

        if parent_kwargs:
            kwargs.update(parent_kwargs)

    return reverse(view_name, urlconf, args, kwargs, prefix)
